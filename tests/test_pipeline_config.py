from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from include.pipeline_config import load_config


class TestPipelineConfig(unittest.TestCase):
    def _write_temp_config(self, yaml_text: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        config_path = Path(temp_dir.name) / "pipeline.yaml"
        config_path.write_text(yaml_text, encoding="utf-8")
        return config_path

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

    def test_build_plan_expands_ordered_plan_units(self) -> None:
        config_path = self._write_temp_config(
            """
parallelism:
  cycles: parallel
  file_types: sequential
styles:
  current:
    file_types: [indiv, cn]
    change_detection: true
  historical:
    file_types: [weball]
    change_detection: false
cycles:
  - cycle: 2024
    style: current
  - cycles: "2020-2022"
    style: historical
"""
        )

        config = load_config(config_path)
        plan = config.build_plan()

        self.assertEqual(plan.parallelism.cycles, "parallel")
        self.assertEqual(plan.parallelism.file_types, "sequential")
        self.assertEqual(
            [
                (
                    unit.cycle,
                    unit.file_type,
                    unit.style_name,
                    unit.change_detection,
                )
                for unit in plan.units
            ],
            [
                (2024, "indiv", "current", True),
                (2024, "cn", "current", True),
                (2020, "weball", "historical", False),
                (2022, "weball", "historical", False),
            ],
        )

    def test_build_plan_is_stable_across_repeated_calls(self) -> None:
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

        self.assertEqual(config.build_plan(), config.build_plan())


if __name__ == "__main__":
    unittest.main()
