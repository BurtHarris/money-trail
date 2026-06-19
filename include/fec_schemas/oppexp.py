"""FEC Operating Expenditures (oppexp) schema.

Source: Schedule B filings — operating expenditures by committees.
FEC bulk download: ``oppexp{yy}.zip`` containing ``oppexp.txt``.
"""

from __future__ import annotations

import pyarrow as pa

from include.fec_schemas import FecColumn

COLUMNS: list[FecColumn] = [
    FecColumn("cmte_id",         "committee_id",                pa.string()),
    FecColumn("amndt_ind",       "amendment_indicator",         pa.string()),
    FecColumn("rpt_yr",          "report_year",                 pa.int16()),
    FecColumn("rpt_tp",          "report_type",                 pa.string()),
    FecColumn("image_num",       "image_number",                pa.string()),
    FecColumn("line_num",        "line_number",                 pa.string()),
    FecColumn("form_tp_cd",      "form_type",                   pa.string()),
    FecColumn("sched_tp_cd",     "schedule_type",               pa.string()),
    FecColumn("name",            "payee_name",                  pa.string()),
    FecColumn("city",            "payee_city",                  pa.string()),
    FecColumn("state",           "payee_state",                 pa.string()),
    FecColumn("zip_code",        "payee_zip",                   pa.string()),
    FecColumn("transaction_dt",  "transaction_date",            pa.string()),
    FecColumn("transaction_amt", "transaction_amount",          pa.float64()),
    FecColumn("transaction_pgi", "transaction_primary_general", pa.string()),
    FecColumn("purpose",         "purpose",                     pa.string()),
    FecColumn("category",        "category_code",               pa.string()),
    FecColumn("category_desc",   "category_description",        pa.string()),
    FecColumn("memo_cd",         "memo_code",                   pa.string()),
    FecColumn("memo_text",       "memo_text",                   pa.string()),
    FecColumn("entity_tp",       "entity_type",                 pa.string()),
    FecColumn("sub_id",          "submission_id",               pa.int64()),
    FecColumn("file_num",        "file_number",                 pa.int64()),
    FecColumn("tran_id",         "transaction_id",              pa.string()),
    FecColumn("back_ref_tran_id","back_reference_transaction_id",pa.string()),
]
