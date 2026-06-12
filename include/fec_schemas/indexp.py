"""FEC Independent Expenditures (indexp) schema.

Source: Schedule E filings — independent expenditures made by committees
expressly advocating for or against a federal candidate, without coordination
with any candidate or political party.
FEC bulk download: ``indexp{yy}.zip`` containing ``indexp.txt``.
"""

from __future__ import annotations

import pyarrow as pa

from include.fec_schemas import FECColumn

COLUMNS: list[FECColumn] = [
    FECColumn("cmte_id",              "committee_id",                pa.string()),
    FECColumn("amndt_ind",            "amendment_indicator",         pa.string()),
    FECColumn("rpt_tp",               "report_type",                 pa.string()),
    FECColumn("transaction_pgi",      "transaction_primary_general", pa.string()),
    FECColumn("image_num",            "image_number",                pa.string()),
    FECColumn("line_num",             "line_number",                 pa.string()),
    FECColumn("form_tp_cd",           "form_type",                   pa.string()),
    FECColumn("sched_tp_cd",          "schedule_type",               pa.string()),
    FECColumn("name",                 "payee_name",                  pa.string()),
    FECColumn("city",                 "payee_city",                  pa.string()),
    FECColumn("state",                "payee_state",                 pa.string()),
    FECColumn("zip_code",             "payee_zip",                   pa.string()),
    FECColumn("entity_tp",            "entity_type",                 pa.string()),
    FECColumn("payee_cmte_id",        "payee_committee_id",          pa.string()),
    FECColumn("cand_id",              "candidate_id",                pa.string()),
    FECColumn("cand_name",            "candidate_name",              pa.string()),
    FECColumn("cand_pty_affiliation", "party_affiliation",           pa.string()),
    FECColumn("cand_office",          "office",                      pa.string()),
    FECColumn("cand_office_st",       "office_state",                pa.string()),
    FECColumn("cand_office_district", "office_district",             pa.string()),
    FECColumn("conduit_cmte_id",      "conduit_committee_id",        pa.string()),
    FECColumn("conduit_cmte_nm",      "conduit_committee_name",      pa.string()),
    FECColumn("conduit_cmte_st1",     "conduit_street_1",            pa.string()),
    FECColumn("conduit_cmte_st2",     "conduit_street_2",            pa.string()),
    FECColumn("conduit_cmte_city",    "conduit_city",                pa.string()),
    FECColumn("conduit_cmte_st",      "conduit_state",               pa.string()),
    FECColumn("conduit_cmte_zip",     "conduit_zip",                 pa.string()),
    FECColumn("transaction_dt",       "transaction_date",            pa.string()),
    FECColumn("transaction_amt",      "transaction_amount",          pa.float64()),
    FECColumn("purpose",              "purpose",                     pa.string()),
    FECColumn("memo_cd",              "memo_code",                   pa.string()),
    FECColumn("memo_text",            "memo_text",                   pa.string()),
    FECColumn("sub_id",               "submission_id",               pa.int64()),
    FECColumn("file_num",             "file_number",                 pa.int64()),
    FECColumn("tran_id",              "transaction_id",              pa.string()),
    FECColumn("back_ref_tran_id",     "back_reference_transaction_id", pa.string()),
]
