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

VALID_FEC_TABLES = frozenset(
    ["indiv", "cn", "cm", "oth", "oppexp", "ccl", "weball", "pas2", "indexp"]
)
"""Valid FecTable identifiers — the FEC's own short codes for bulk download categories."""

# Backward-compatible alias; prefer VALID_FEC_TABLES.
VALID_FILE_TYPES = VALID_FEC_TABLES

_CYCLE_RANGE_RE = re.compile(r"^(\d{4})-(\d{4})$")


@dataclass
class DownloadProfile:
    """A named, reusable download configuration.

    Specifies which FecTables to fetch and whether change detection is active.
    Cycles reference a DownloadProfile by name rather than repeating these settings.
    """

    name: str
    tables: list[str]
    change_detection: bool


@dataclass
class CycleConfig:
    cycle: int
    download_profile: DownloadProfile


@dataclass
class Parallelism:
    cycles: Literal["sequential", "parallel"]
    tables: Literal["sequential", "parallel"]


@dataclass
class PipelineConfig:
    parallelism: Parallelism
    download_profiles: dict[str, DownloadProfile]
    cycles: list[CycleConfig] = field(default_factory=list)


@dataclass(frozen=True)
class ScopeTarget:
    """One normalized scope target derived from Scope Config."""

    cycle: int
    fec_table: str
    download_profile_key: str
    change_detection: bool

    @property
    def fec_file_type(self) -> str:
        """Deprecated: use ``fec_table`` instead."""
        return self.fec_table

    @property
    def file_type(self) -> str:
        """Deprecated: use ``fec_table`` instead."""
        return self.fec_table

    @property
    def style_key(self) -> str:
        """Deprecated: use ``download_profile_key`` instead."""
        return self.download_profile_key

    @property
    def style_name(self) -> str:
        """Deprecated: use ``download_profile_key`` instead."""
        return self.download_profile_key


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
        for table in cycle_config.download_profile.tables:
            targets.append(
                ScopeTarget(
                    cycle=cycle_config.cycle,
                    fec_table=table,
                    download_profile_key=cycle_config.download_profile.name,
                    change_detection=cycle_config.download_profile.change_detection,
                )
            )
    return ScopeWorklist(parallelism=config.parallelism, targets=targets)


# Backward-compatible aliases for existing callers; prefer the new names.
Style = DownloadProfile  # Legacy alias: prefer DownloadProfile.
PlanUnit = ScopeTarget  # Legacy alias: prefer ScopeTarget.
ScopePlan = ScopeWorklist  # Legacy alias: prefer ScopeWorklist.
build_scope_plan = build_scope_worklist  # Legacy alias: prefer build_scope_worklist.


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


def _parse_download_profiles(raw: dict) -> dict[str, DownloadProfile]:
    if not isinstance(raw, dict):
        raise ValueError("Field 'download_profiles' must be a mapping.")

    profiles: dict[str, DownloadProfile] = {}
    for name, cfg in raw.items():
        if not isinstance(cfg, dict):
            raise ValueError(f"DownloadProfile {name!r} must be a mapping.")

        tables = cfg.get("tables")
        if not isinstance(tables, list) or not tables:
            raise ValueError(
                f"DownloadProfile {name!r} must define a non-empty 'tables' list."
            )
        if not all(isinstance(t, str) for t in tables):
            raise ValueError(
                f"DownloadProfile {name!r} has non-string values in 'tables'."
            )

        unknown = set(tables) - VALID_FEC_TABLES
        if unknown:
            raise ValueError(
                f"DownloadProfile {name!r} references unknown FecTables: {sorted(unknown)}"
            )
        change_detection = cfg.get("change_detection")
        if not isinstance(change_detection, bool):
            raise ValueError(
                f"DownloadProfile {name!r} must define boolean 'change_detection'."
            )
        profiles[name] = DownloadProfile(
            name=name,
            tables=tables,
            change_detection=change_detection,
        )
    return profiles


def _parse_cycles(
    raw: list, download_profiles: dict[str, DownloadProfile]
) -> list[CycleConfig]:
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

        profile_name = entry.get("download_profile")
        if not isinstance(profile_name, str):
            raise ValueError(
                f"Cycle entry must define string 'download_profile': {entry!r}"
            )
        if profile_name not in download_profiles:
            raise ValueError(
                f"Cycle entry references unknown DownloadProfile {profile_name!r}. "
                f"Known profiles: {sorted(download_profiles)}"
            )
        download_profile = download_profiles[profile_name]

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
            result.append(CycleConfig(cycle=cycle, download_profile=download_profile))
        else:
            for year in _expand_cycle_range(str(entry["cycles"])):
                result.append(
                    CycleConfig(cycle=year, download_profile=download_profile)
                )
    return result


def _parse_parallelism(raw: dict) -> Parallelism:
    if not isinstance(raw, dict):
        raise ValueError("Field 'parallelism' must be a mapping.")

    cycles = raw.get("cycles", "sequential")
    tables = raw.get("tables", "parallel")
    if cycles not in _VALID_PARALLELISM_VALUES:
        raise ValueError(
            "Field 'parallelism.cycles' must be one of: "
            f"{sorted(_VALID_PARALLELISM_VALUES)}"
        )
    if tables not in _VALID_PARALLELISM_VALUES:
        raise ValueError(
            "Field 'parallelism.tables' must be one of: "
            f"{sorted(_VALID_PARALLELISM_VALUES)}"
        )
    return Parallelism(cycles=cycles, tables=tables)


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

    download_profiles = _parse_download_profiles(raw.get("download_profiles", {}))
    if not download_profiles:
        raise ValueError("Configuration must define at least one download_profile.")

    cycles = _parse_cycles(raw.get("cycles", []), download_profiles)
    if not cycles:
        raise ValueError("Configuration must define at least one cycle entry.")

    return PipelineConfig(
        parallelism=parallelism, download_profiles=download_profiles, cycles=cycles
    )


PIPELINE_CONFIG: PipelineConfig = load_config()
