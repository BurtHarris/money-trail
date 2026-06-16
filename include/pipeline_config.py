"""Pipeline configuration loader.

Parses and validates ``config/pipeline.yaml`` at import time and exposes a
single :data:`PIPELINE_CONFIG` instance ready for use by Airflow DAGs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "pipeline.yaml"
_VALID_PARALLELISM_VALUES = {"sequential", "parallel"}

VALID_FILE_TYPES = frozenset(
    ["indiv", "cn", "cm", "oth", "oppexp", "ccl", "weball", "pas2", "indexp"]
)

_CYCLE_RANGE_RE = re.compile(r"^(\d{4})-(\d{4})$")


@dataclass
class Style:
    name: str
    file_types: list[str]
    change_detection: bool


@dataclass
class CycleConfig:
    cycle: int
    style: Style


@dataclass
class Parallelism:
    cycles: Literal["sequential", "parallel"]
    file_types: Literal["sequential", "parallel"]


@dataclass
class PipelineConfig:
    parallelism: Parallelism
    styles: dict[str, Style]
    cycles: list[CycleConfig] = field(default_factory=list)


@dataclass(frozen=True)
class ScopeTarget:
    """One normalized scope target derived from Scope Config."""

    cycle: int
    fec_file_type: str
    style_key: str
    change_detection: bool

    @property
    def file_type(self) -> str:
        """Backward-compatible alias for ``fec_file_type``."""
        return self.fec_file_type

    @property
    def style_name(self) -> str:
        """Backward-compatible alias for ``style_key``."""
        return self.style_key


@dataclass
class ScopeWorklist:
    """Scope expansion output: normalized targets plus Parallelism metadata."""

    parallelism: Parallelism
    targets: list[ScopeTarget] = field(default_factory=list)

    @property
    def plan_units(self) -> list[ScopeTarget]:
        """Backward-compatible alias for ``targets``."""
        return self.targets


def build_scope_worklist(config: PipelineConfig) -> ScopeWorklist:
    """Build deterministic scope targets from Scope Config."""
    targets: list[ScopeTarget] = []
    for cycle_config in config.cycles:
        for file_type in cycle_config.style.file_types:
            targets.append(
                ScopeTarget(
                    cycle=cycle_config.cycle,
                    fec_file_type=file_type,
                    style_key=cycle_config.style.name,
                    change_detection=cycle_config.style.change_detection,
                )
            )
    return ScopeWorklist(parallelism=config.parallelism, targets=targets)


# Backward-compatible aliases for existing callers; prefer the new names.
PlanUnit = ScopeTarget
ScopePlan = ScopeWorklist
build_scope_plan = build_scope_worklist


def _expand_cycle_range(range_str: str) -> list[int]:
    """Expand a Cycle Range string like ``"2010-2022"`` to individual even-year cycles."""
    m = _CYCLE_RANGE_RE.match(range_str)
    if not m:
        raise ValueError(
            f"Invalid Cycle Range {range_str!r}. Expected format 'YYYY-YYYY'."
        )
    start, end = int(m.group(1)), int(m.group(2))
    if start > end:
        raise ValueError(
            f"Cycle Range start {start} must be <= end {end} in {range_str!r}."
        )
    if start % 2 != 0 or end % 2 != 0:
        raise ValueError(
            f"Cycle Range endpoints must be even years; got {range_str!r}."
        )
    return list(range(start, end + 1, 2))


def _parse_styles(raw: dict) -> dict[str, Style]:
    if not isinstance(raw, dict):
        raise ValueError("Field 'styles' must be a mapping.")

    styles: dict[str, Style] = {}
    for name, cfg in raw.items():
        if not isinstance(cfg, dict):
            raise ValueError(f"Style {name!r} must be a mapping.")

        file_types = cfg.get("file_types")
        if not isinstance(file_types, list) or not file_types:
            raise ValueError(
                f"Style {name!r} must define a non-empty 'file_types' list."
            )
        if not all(isinstance(file_type, str) for file_type in file_types):
            raise ValueError(f"Style {name!r} has non-string values in 'file_types'.")

        unknown = set(file_types) - VALID_FILE_TYPES
        if unknown:
            raise ValueError(
                f"Style {name!r} references unknown file types: {sorted(unknown)}"
            )
        change_detection = cfg.get("change_detection")
        if not isinstance(change_detection, bool):
            raise ValueError(f"Style {name!r} must define boolean 'change_detection'.")
        styles[name] = Style(
            name=name,
            file_types=file_types,
            change_detection=change_detection,
        )
    return styles


def _parse_cycles(raw: list, styles: dict[str, Style]) -> list[CycleConfig]:
    if not isinstance(raw, list):
        raise ValueError("Field 'cycles' must be a list.")

    result: list[CycleConfig] = []
    for entry in raw:
        if not isinstance(entry, dict):
            raise ValueError(f"Cycle entry must be a mapping, got: {entry!r}")

        has_cycle = "cycle" in entry
        has_cycle_range = "cycles" in entry
        if has_cycle == has_cycle_range:
            raise ValueError(
                f"Cycle entry must define exactly one of 'cycle' or 'cycles': {entry!r}"
            )

        style_name = entry.get("style")
        if not isinstance(style_name, str):
            raise ValueError(f"Cycle entry must define string 'style': {entry!r}")
        if style_name not in styles:
            raise ValueError(
                f"Cycle entry references unknown style {style_name!r}. "
                f"Known styles: {sorted(styles)}"
            )
        style = styles[style_name]

        if has_cycle:
            try:
                cycle = int(entry["cycle"])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Cycle entry has invalid 'cycle' value: {entry['cycle']!r}"
                ) from exc
            if cycle % 2 != 0:
                raise ValueError(
                    f"Cycle values must be even years; got {cycle!r} in {entry!r}."
                )
            result.append(CycleConfig(cycle=cycle, style=style))
        else:
            for year in _expand_cycle_range(str(entry["cycles"])):
                result.append(CycleConfig(cycle=year, style=style))
    return result


def _parse_parallelism(raw: dict) -> Parallelism:
    if not isinstance(raw, dict):
        raise ValueError("Field 'parallelism' must be a mapping.")

    cycles = raw.get("cycles", "sequential")
    file_types = raw.get("file_types", "parallel")
    if cycles not in _VALID_PARALLELISM_VALUES:
        raise ValueError(
            "Field 'parallelism.cycles' must be one of: "
            f"{sorted(_VALID_PARALLELISM_VALUES)}"
        )
    if file_types not in _VALID_PARALLELISM_VALUES:
        raise ValueError(
            "Field 'parallelism.file_types' must be one of: "
            f"{sorted(_VALID_PARALLELISM_VALUES)}"
        )
    return Parallelism(cycles=cycles, file_types=file_types)


def load_config(path: Path = _CONFIG_PATH) -> PipelineConfig:
    """Parse and validate the pipeline YAML configuration file.

    Raises :class:`ValueError` on invalid configuration so problems surface at
    DAG import time rather than at runtime.
    """
    with path.open() as fh:
        raw = yaml.safe_load(fh)

    if raw is None:
        raise ValueError(f"Configuration file is empty: {path}")
    if not isinstance(raw, dict):
        raise ValueError("Configuration root must be a mapping.")

    parallelism = _parse_parallelism(raw.get("parallelism", {}))

    styles = _parse_styles(raw.get("styles", {}))
    if not styles:
        raise ValueError("Configuration must define at least one style.")

    cycles = _parse_cycles(raw.get("cycles", []), styles)
    if not cycles:
        raise ValueError("Configuration must define at least one cycle entry.")

    return PipelineConfig(parallelism=parallelism, styles=styles, cycles=cycles)


PIPELINE_CONFIG: PipelineConfig = load_config()
