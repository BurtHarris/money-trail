from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from include.pipeline_config import (
    DownloadProfile,
    PipelineConfig,
    Parallelism,
    build_scope_plan,
    load_config,
)

# Backward-compat import still available
from include.pipeline_config import Style  # noqa: F401


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
  tables: parallel
download_profiles:
  current:
    tables: [indiv, cn]
    change_detection: true
cycles:
  - cycle: 2024
    download_profile: current
"""
        )

        config = load_config(config_path)
        self.assertEqual(config.parallelism.cycles, "sequential")
        self.assertEqual(config.parallelism.tables, "parallel")
        self.assertIn("current", config.download_profiles)
        self.assertEqual(config.download_profiles["current"].tables, ["indiv", "cn"])
        self.assertTrue(config.download_profiles["current"].change_detection)
        self.assertEqual(len(config.cycles), 1)
        self.assertEqual(config.cycles[0].cycle, 2024)
        self.assertEqual(config.cycles[0].download_profile.name, "current")

    def test_cycle_range_expands_even_years(self) -> None:
        config_path = self._write_temp_config(
            """
parallelism:
  cycles: sequential
  tables: parallel
download_profiles:
  current:
    tables: [indiv, cn]
    change_detection: true
  historical:
    tables: [indiv]
    change_detection: false
cycles:
  - cycle: 2024
    download_profile: current
  - cycles: "2010-2022"
    download_profile: historical
"""
        )

        config = load_config(config_path)
        self.assertEqual(
            [cycle.cycle for cycle in config.cycles],
            [2024, 2010, 2012, 2014, 2016, 2018, 2020, 2022],
        )

    def test_unknown_download_profile_reference_raises(self) -> None:
        config_path = self._write_temp_config(
            """
parallelism:
  cycles: sequential
  tables: parallel
download_profiles:
  current:
    tables: [indiv]
    change_detection: true
cycles:
  - cycle: 2024
    download_profile: missing_profile
"""
        )

        with self.assertRaisesRegex(ValueError, "unknown DownloadProfile"):
            load_config(config_path)

    def test_invalid_cycle_range_raises(self) -> None:
        config_path = self._write_temp_config(
            """
parallelism:
  cycles: sequential
  tables: parallel
download_profiles:
  historical:
    tables: [indiv]
    change_detection: false
cycles:
  - cycles: "2011-2023"
    download_profile: historical
"""
        )

        with self.assertRaisesRegex(ValueError, "even years"):
            load_config(config_path)

    def test_scope_worklist_targets_are_deterministic_and_ordered(self) -> None:
        config_path = self._write_temp_config(
            """
parallelism:
  cycles: sequential
  tables: parallel
download_profiles:
  current:
    tables: [indiv, cn]
    change_detection: true
  historical:
    tables: [cm]
    change_detection: false
cycles:
  - cycle: 2024
    download_profile: current
  - cycles: "2018-2020"
    download_profile: historical
"""
        )

        config = load_config(config_path)
        worklist = build_scope_plan(config)

        self.assertEqual(worklist.parallelism.cycles, "sequential")
        self.assertEqual(worklist.parallelism.tables, "parallel")
        self.assertEqual(
            [
                (
                    target.cycle,
                    target.fec_table,
                    target.download_profile_key,
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
  tables: sequential
download_profiles:
  current:
    tables: [indiv]
    change_detection: true
cycles:
  - cycle: 2024
    download_profile: current
"""
        )

        first_worklist = build_scope_plan(load_config(config_path))
        second_worklist = build_scope_plan(load_config(config_path))

        self.assertEqual(first_worklist.parallelism, second_worklist.parallelism)
        self.assertEqual(first_worklist.targets, second_worklist.targets)

    def test_scope_worklist_with_no_cycles_returns_no_targets(self) -> None:
        config = PipelineConfig(
            parallelism=Parallelism(cycles="sequential", tables="parallel"),
            download_profiles={"current": DownloadProfile("current", ["indiv"], True)},
            cycles=[],
        )
        worklist = build_scope_plan(config)
        self.assertEqual(worklist.parallelism, config.parallelism)
        self.assertEqual(worklist.targets, [])

    def test_backward_compat_aliases_on_scope_target(self) -> None:
        """Deprecated properties fec_file_type, file_type, style_key, style_name still work.

        These are kept for callers that haven't migrated to fec_table /
        download_profile_key yet; prefer the new names in new code.
        """
        config_path = self._write_temp_config(
            """
parallelism:
  cycles: sequential
  tables: parallel
download_profiles:
  current:
    tables: [indiv]
    change_detection: true
cycles:
  - cycle: 2024
    download_profile: current
"""
        )
        config = load_config(config_path)
        worklist = build_scope_plan(config)
        target = worklist.targets[0]

        self.assertEqual(target.fec_table, "indiv")
        self.assertEqual(target.fec_file_type, "indiv")
        self.assertEqual(target.file_type, "indiv")
        self.assertEqual(target.download_profile_key, "current")
        self.assertEqual(target.style_key, "current")
        self.assertEqual(target.style_name, "current")


if __name__ == "__main__":
    unittest.main()
