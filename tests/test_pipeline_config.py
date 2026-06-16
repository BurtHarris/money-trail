from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from include.pipeline_config import (
    PipelineConfig,
    Parallelism,
    Style,
    build_scope_plan,
    load_config,
)


class TestPipelineConfig(unittest.TestCase):
    def _write_temp_config(self, yaml_text: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        config_path = Path(temp_dir.name) / "pipeline.yaml"
        config_path.write_text(yaml_text, encoding="utf-8")
        return config_path

    def test_valid_config_parses_cleanly(self) -> None:
        config_path = self._write_temp_config(
            """
parallelism:
  cycles: sequential
  file_types: parallel
styles:
  current:
    file_types: [indiv, cn]
    change_detection: true
cycles:
  - cycle: 2024
    style: current
"""
        )

        config = load_config(config_path)
        self.assertEqual(config.parallelism.cycles, "sequential")
        self.assertEqual(config.parallelism.file_types, "parallel")
        self.assertIn("current", config.styles)
        self.assertEqual(config.styles["current"].file_types, ["indiv", "cn"])
        self.assertTrue(config.styles["current"].change_detection)
        self.assertEqual(len(config.cycles), 1)
        self.assertEqual(config.cycles[0].cycle, 2024)
        self.assertEqual(config.cycles[0].style.name, "current")

    def test_cycle_range_expands_even_years(self) -> None:
        config_path = self._write_temp_config(
            """
parallelism:
  cycles: sequential
  file_types: parallel
styles:
  current:
    file_types: [indiv, cn]
    change_detection: true
  historical:
    file_types: [indiv]
    change_detection: false
cycles:
  - cycle: 2024
    style: current
  - cycles: "2010-2022"
    style: historical
"""
        )

        config = load_config(config_path)
        self.assertEqual(
            [cycle.cycle for cycle in config.cycles],
            [2024, 2010, 2012, 2014, 2016, 2018, 2020, 2022],
        )

    def test_unknown_style_reference_raises(self) -> None:
        config_path = self._write_temp_config(
            """
parallelism:
  cycles: sequential
  file_types: parallel
styles:
  current:
    file_types: [indiv]
    change_detection: true
cycles:
  - cycle: 2024
    style: missing_style
"""
        )

        with self.assertRaisesRegex(ValueError, "unknown style"):
            load_config(config_path)

    def test_invalid_cycle_range_raises(self) -> None:
        config_path = self._write_temp_config(
            """
parallelism:
  cycles: sequential
  file_types: parallel
styles:
  historical:
    file_types: [indiv]
    change_detection: false
cycles:
  - cycles: "2011-2023"
    style: historical
"""
        )

        with self.assertRaisesRegex(ValueError, "even years"):
            load_config(config_path)

    def test_scope_worklist_targets_are_deterministic_and_ordered(self) -> None:
        config_path = self._write_temp_config(
            """
parallelism:
  cycles: sequential
  file_types: parallel
styles:
  current:
    file_types: [indiv, cn]
    change_detection: true
  historical:
    file_types: [cm]
    change_detection: false
cycles:
  - cycle: 2024
    style: current
  - cycles: "2018-2020"
    style: historical
"""
        )

        config = load_config(config_path)
        worklist = build_scope_plan(config)

        self.assertEqual(worklist.parallelism.cycles, "sequential")
        self.assertEqual(worklist.parallelism.file_types, "parallel")
        self.assertEqual(
            [
                (
                    target.cycle,
                    target.fec_file_type,
                    target.style_key,
                    target.change_detection,
                )
                for target in worklist.targets
            ],
            [
                (2024, "indiv", "current", True),
                (2024, "cn", "current", True),
                (2018, "cm", "historical", False),
                (2020, "cm", "historical", False),
            ],
        )

    def test_scope_worklist_output_is_stable_across_repeated_runs(self) -> None:
        config_path = self._write_temp_config(
            """
parallelism:
  cycles: parallel
  file_types: sequential
styles:
  current:
    file_types: [indiv]
    change_detection: true
cycles:
  - cycle: 2024
    style: current
"""
        )

        first_worklist = build_scope_plan(load_config(config_path))
        second_worklist = build_scope_plan(load_config(config_path))

        self.assertEqual(first_worklist.parallelism, second_worklist.parallelism)
        self.assertEqual(first_worklist.targets, second_worklist.targets)

    def test_scope_worklist_with_no_cycles_returns_no_targets(self) -> None:
        config = PipelineConfig(
            parallelism=Parallelism(cycles="sequential", file_types="parallel"),
            styles={"current": Style("current", ["indiv"], True)},
            cycles=[],
        )
        worklist = build_scope_plan(config)
        self.assertEqual(worklist.parallelism, config.parallelism)
        self.assertEqual(worklist.targets, [])


if __name__ == "__main__":
    unittest.main()
