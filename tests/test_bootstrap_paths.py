from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP_SCRIPT = REPO_ROOT / "scripts" / "bootstrap.sh"


class TestBootstrapPaths(unittest.TestCase):
    def test_bootstrap_creates_all_data_tiers_and_exports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "dbt").mkdir()
            (workspace / "dbt" / "profiles.yml.example").write_text("money_trail:\n", encoding="utf-8")

            env = os.environ.copy()
            env["BOOTSTRAP_AIRFLOW"] = "0"

            subprocess.run(
                ["bash", str(BOOTSTRAP_SCRIPT)],
                check=True,
                cwd=workspace,
                env=env,
            )

            self.assertTrue((workspace / ".airflow").is_dir())
            self.assertTrue((workspace / "logs").is_dir())
            self.assertTrue((workspace / "exports").is_dir())

            data_dir = workspace / "data"
            self.assertTrue((data_dir / "raw").is_dir())
            self.assertTrue((data_dir / "stage").is_dir())
            self.assertTrue((data_dir / "ducklake").is_dir())
            self.assertTrue((data_dir / "duckdb").is_dir())
            self.assertTrue((workspace / "dbt" / "profiles.yml").is_file())
