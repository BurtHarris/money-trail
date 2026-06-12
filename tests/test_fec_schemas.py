"""Tests for include/fec_schemas/* — column-count contracts and special attributes.

Each schema file defines an ordered ``COLUMNS`` list of :class:`FECColumn`
entries.  These tests verify:

1. The column count for each file type matches the FEC-published specification.
2. Every column has non-empty ``fec_name`` and ``alias`` strings.
3. ``indiv.ZIP_INNER_PATH`` is set to ``"itcont.txt"`` (ADR 0005).
"""

from __future__ import annotations

import importlib
import unittest

import pyarrow as pa

from include.fec_schemas import FECColumn


# ---------------------------------------------------------------------------
# Expected column counts per FEC-published specification
# ---------------------------------------------------------------------------
#
#  Source references used to establish these counts:
#    indiv (21): FEC individual contributions file description
#    cn    (15): FEC candidate master file description
#    cm    (15): FEC committee master file description
#    ccl   ( 7): FEC candidate-committee linkage file description
#    oth   (21): FEC committee-to-committee transfers file description
#    pas2  (22): FEC contributions-to-candidates file description
#    oppexp(25): FEC operating expenditures file description
#    weball(30): FEC all-candidates financial summary file description
#    indexp(36): FEC independent expenditures file description
#
EXPECTED_COLUMN_COUNTS: dict[str, int] = {
    "indiv":  21,
    "cn":     15,
    "cm":     15,
    "ccl":     7,
    "oth":    21,
    "pas2":   22,
    "oppexp": 25,
    "weball": 30,
    "indexp": 36,
}


class TestFecSchemaColumnCounts(unittest.TestCase):
    """Verify column counts match FEC-published specifications."""

    def _load_schema(self, file_type: str):
        return importlib.import_module(f"include.fec_schemas.{file_type}")

    def _assert_column_count(self, file_type: str, expected: int) -> None:
        module = self._load_schema(file_type)
        self.assertTrue(
            hasattr(module, "COLUMNS"),
            msg=f"include/fec_schemas/{file_type}.py must define COLUMNS",
        )
        actual = len(module.COLUMNS)
        self.assertEqual(
            actual,
            expected,
            msg=(
                f"{file_type}: expected {expected} columns "
                f"(FEC-published count) but got {actual}"
            ),
        )

    def test_indiv_column_count(self):
        self._assert_column_count("indiv", EXPECTED_COLUMN_COUNTS["indiv"])

    def test_cn_column_count(self):
        self._assert_column_count("cn", EXPECTED_COLUMN_COUNTS["cn"])

    def test_cm_column_count(self):
        self._assert_column_count("cm", EXPECTED_COLUMN_COUNTS["cm"])

    def test_ccl_column_count(self):
        self._assert_column_count("ccl", EXPECTED_COLUMN_COUNTS["ccl"])

    def test_oth_column_count(self):
        self._assert_column_count("oth", EXPECTED_COLUMN_COUNTS["oth"])

    def test_pas2_column_count(self):
        self._assert_column_count("pas2", EXPECTED_COLUMN_COUNTS["pas2"])

    def test_oppexp_column_count(self):
        self._assert_column_count("oppexp", EXPECTED_COLUMN_COUNTS["oppexp"])

    def test_weball_column_count(self):
        self._assert_column_count("weball", EXPECTED_COLUMN_COUNTS["weball"])

    def test_indexp_column_count(self):
        self._assert_column_count("indexp", EXPECTED_COLUMN_COUNTS["indexp"])


class TestFecSchemaColumnMetadata(unittest.TestCase):
    """Verify every column in every schema has valid fec_name, alias, and pa_type."""

    def _check_columns(self, file_type: str) -> None:
        module = importlib.import_module(f"include.fec_schemas.{file_type}")
        columns: list[FECColumn] = module.COLUMNS
        for i, col in enumerate(columns):
            self.assertIsInstance(
                col,
                FECColumn,
                msg=f"{file_type}[{i}] must be a FECColumn instance",
            )
            self.assertTrue(
                col.fec_name,
                msg=f"{file_type}[{i}].fec_name must be a non-empty string",
            )
            self.assertTrue(
                col.alias,
                msg=f"{file_type}[{i}].alias must be a non-empty string",
            )
            self.assertIsInstance(
                col.pa_type,
                pa.DataType,
                msg=f"{file_type}[{i}] ({col.fec_name}).pa_type must be a pa.DataType",
            )

    def test_indiv_column_metadata(self):
        self._check_columns("indiv")

    def test_cn_column_metadata(self):
        self._check_columns("cn")

    def test_cm_column_metadata(self):
        self._check_columns("cm")

    def test_ccl_column_metadata(self):
        self._check_columns("ccl")

    def test_oth_column_metadata(self):
        self._check_columns("oth")

    def test_pas2_column_metadata(self):
        self._check_columns("pas2")

    def test_oppexp_column_metadata(self):
        self._check_columns("oppexp")

    def test_weball_column_metadata(self):
        self._check_columns("weball")

    def test_indexp_column_metadata(self):
        self._check_columns("indexp")


class TestIndivZipInnerPath(unittest.TestCase):
    """Verify that indiv.ZIP_INNER_PATH is set correctly (ADR 0005)."""

    def test_zip_inner_path_present(self):
        from include.fec_schemas import indiv

        self.assertTrue(
            hasattr(indiv, "ZIP_INNER_PATH"),
            msg="include/fec_schemas/indiv.py must define ZIP_INNER_PATH",
        )

    def test_zip_inner_path_value(self):
        from include.fec_schemas import indiv

        self.assertEqual(
            indiv.ZIP_INNER_PATH,
            "itcont.txt",
            msg="indiv.ZIP_INNER_PATH must equal 'itcont.txt'",
        )


class TestFecSchemaFecNamesUnique(unittest.TestCase):
    """Verify fec_name values are unique within each schema."""

    def _check_unique_fec_names(self, file_type: str) -> None:
        module = importlib.import_module(f"include.fec_schemas.{file_type}")
        fec_names = [col.fec_name for col in module.COLUMNS]
        self.assertEqual(
            len(fec_names),
            len(set(fec_names)),
            msg=f"{file_type}: fec_name values must be unique within COLUMNS",
        )

    def test_indiv_unique_fec_names(self):
        self._check_unique_fec_names("indiv")

    def test_cn_unique_fec_names(self):
        self._check_unique_fec_names("cn")

    def test_cm_unique_fec_names(self):
        self._check_unique_fec_names("cm")

    def test_ccl_unique_fec_names(self):
        self._check_unique_fec_names("ccl")

    def test_oth_unique_fec_names(self):
        self._check_unique_fec_names("oth")

    def test_pas2_unique_fec_names(self):
        self._check_unique_fec_names("pas2")

    def test_oppexp_unique_fec_names(self):
        self._check_unique_fec_names("oppexp")

    def test_weball_unique_fec_names(self):
        self._check_unique_fec_names("weball")

    def test_indexp_unique_fec_names(self):
        self._check_unique_fec_names("indexp")


if __name__ == "__main__":
    unittest.main()
