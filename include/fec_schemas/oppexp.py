"""FEC Operating Expenditures (oppexp) schema.

Source: Schedule B filings — operating expenditures by committees.
FEC bulk download: ``oppexp{yy}.zip`` containing ``oppexp.txt``.
"""

from __future__ import annotations

import pyarrow as pa

from include.fec_schemas import FECColumn

COLUMNS: list[FECColumn] = [
    FECColumn("cmte_id",         "committee_id",                pa.string()),
    FECColumn("amndt_ind",       "amendment_indicator",         pa.string()),
    FECColumn("rpt_yr",          "report_year",                 pa.int16()),
    FECColumn("rpt_tp",          "report_type",                 pa.string()),
    FECColumn("image_num",       "image_number",                pa.string()),
    FECColumn("line_num",        "line_number",                 pa.string()),
    FECColumn("form_tp_cd",      "form_type",                   pa.string()),
    FECColumn("sched_tp_cd",     "schedule_type",               pa.string()),
    FECColumn("name",            "payee_name",                  pa.string()),
    FECColumn("city",            "payee_city",                  pa.string()),
    FECColumn("state",           "payee_state",                 pa.string()),
    FECColumn("zip_code",        "payee_zip",                   pa.string()),
    FECColumn("transaction_dt",  "transaction_date",            pa.string()),
    FECColumn("transaction_amt", "transaction_amount",          pa.float64()),
    FECColumn("transaction_pgi", "transaction_primary_general", pa.string()),
    FECColumn("purpose",         "purpose",                     pa.string()),
    FECColumn("category",        "category_code",               pa.string()),
    FECColumn("category_desc",   "category_description",        pa.string()),
    FECColumn("memo_cd",         "memo_code",                   pa.string()),
    FECColumn("memo_text",       "memo_text",                   pa.string()),
    FECColumn("entity_tp",       "entity_type",                 pa.string()),
    FECColumn("sub_id",          "submission_id",               pa.int64()),
    FECColumn("file_num",        "file_number",                 pa.int64()),
    FECColumn("tran_id",         "transaction_id",              pa.string()),
    FECColumn("back_ref_tran_id","back_reference_transaction_id",pa.string()),
]
