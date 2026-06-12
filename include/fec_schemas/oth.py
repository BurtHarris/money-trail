"""FEC Committee-to-Committee Transfers (oth) schema.

Source: Schedule B, committee-to-committee transfers — transactions where
one committee transfers funds to another committee (not to a candidate).
The recipient is identified via ``other_id`` (their FEC committee ID).
FEC bulk download: ``oth{yy}.zip`` containing ``itoth.txt``.
"""

from __future__ import annotations

import pyarrow as pa

from include.fec_schemas import FECColumn

COLUMNS: list[FECColumn] = [
    FECColumn("cmte_id",         "committee_id",                pa.string()),
    FECColumn("amndt_ind",       "amendment_indicator",         pa.string()),
    FECColumn("rpt_tp",          "report_type",                 pa.string()),
    FECColumn("transaction_pgi", "transaction_primary_general", pa.string()),
    FECColumn("image_num",       "image_number",                pa.string()),
    FECColumn("transaction_tp",  "transaction_type",            pa.string()),
    FECColumn("entity_tp",       "entity_type",                 pa.string()),
    FECColumn("name",            "contributor_name",            pa.string()),
    FECColumn("city",            "contributor_city",            pa.string()),
    FECColumn("state",           "contributor_state",           pa.string()),
    FECColumn("zip_code",        "contributor_zip",             pa.string()),
    FECColumn("employer",        "contributor_employer",        pa.string()),
    FECColumn("occupation",      "contributor_occupation",      pa.string()),
    FECColumn("transaction_dt",  "transaction_date",            pa.string()),
    FECColumn("transaction_amt", "transaction_amount",          pa.float64()),
    FECColumn("other_id",        "other_id",                    pa.string()),
    FECColumn("tran_id",         "transaction_id",              pa.string()),
    FECColumn("file_num",        "file_number",                 pa.int64()),
    FECColumn("memo_cd",         "memo_code",                   pa.string()),
    FECColumn("memo_text",       "memo_text",                   pa.string()),
    FECColumn("sub_id",          "submission_id",               pa.int64()),
]
