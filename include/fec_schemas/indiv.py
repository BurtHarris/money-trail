"""FEC Individual Contributions (indiv) schema.

Source: Schedule A filings — contributions from individuals.
FEC bulk download: ``indiv{yy}.zip`` containing ``itcont.txt``.

``ZIP_INNER_PATH`` identifies the full-cycle root file within the ZIP.  The
archive also contains date-range partial files in a subdirectory; loading
without an explicit inner path would produce duplicates (ADR 0005).
"""

from __future__ import annotations

import pyarrow as pa

from include.fec_schemas import FecColumn

ZIP_INNER_PATH: str = "itcont.txt"

COLUMNS: list[FecColumn] = [
    FecColumn("cmte_id",         "committee_id",                pa.string()),
    FecColumn("amndt_ind",       "amendment_indicator",         pa.string()),
    FecColumn("rpt_tp",          "report_type",                 pa.string()),
    FecColumn("transaction_pgi", "transaction_primary_general", pa.string()),
    FecColumn("image_num",       "image_number",                pa.string()),
    FecColumn("transaction_tp",  "transaction_type",            pa.string()),
    FecColumn("entity_tp",       "entity_type",                 pa.string()),
    FecColumn("name",            "contributor_name",            pa.string()),
    FecColumn("city",            "contributor_city",            pa.string()),
    FecColumn("state",           "contributor_state",           pa.string()),
    FecColumn("zip_code",        "contributor_zip",             pa.string()),
    FecColumn("employer",        "contributor_employer",        pa.string()),
    FecColumn("occupation",      "contributor_occupation",      pa.string()),
    FecColumn("transaction_dt",  "transaction_date",            pa.string()),
    FecColumn("transaction_amt", "transaction_amount",          pa.float64()),
    FecColumn("other_id",        "other_id",                    pa.string()),
    FecColumn("tran_id",         "transaction_id",              pa.string()),
    FecColumn("file_num",        "file_number",                 pa.int64()),
    FecColumn("memo_cd",         "memo_code",                   pa.string()),
    FecColumn("memo_text",       "memo_text",                   pa.string()),
    FecColumn("sub_id",          "submission_id",               pa.int64()),
]
