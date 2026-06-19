"""FEC Independent Expenditures (indexp) schema.

Source: Schedule E filings — independent expenditures made by committees
expressly advocating for or against a federal candidate, without coordination
with any candidate or political party.
FEC bulk download: ``indexp{yy}.zip`` containing ``indexp.txt``.
"""

from __future__ import annotations

import pyarrow as pa

from include.fec_schemas import FecColumn

COLUMNS: list[FecColumn] = [
    FecColumn("cmte_id",              "committee_id",                pa.string()),
    FecColumn("amndt_ind",            "amendment_indicator",         pa.string()),
    FecColumn("rpt_tp",               "report_type",                 pa.string()),
    FecColumn("transaction_pgi",      "transaction_primary_general", pa.string()),
    FecColumn("image_num",            "image_number",                pa.string()),
    FecColumn("line_num",             "line_number",                 pa.string()),
    FecColumn("form_tp_cd",           "form_type",                   pa.string()),
    FecColumn("sched_tp_cd",          "schedule_type",               pa.string()),
    FecColumn("name",                 "payee_name",                  pa.string()),
    FecColumn("city",                 "payee_city",                  pa.string()),
    FecColumn("state",                "payee_state",                 pa.string()),
    FecColumn("zip_code",             "payee_zip",                   pa.string()),
    FecColumn("entity_tp",            "entity_type",                 pa.string()),
    FecColumn("payee_cmte_id",        "payee_committee_id",          pa.string()),
    FecColumn("cand_id",              "candidate_id",                pa.string()),
    FecColumn("cand_name",            "candidate_name",              pa.string()),
    FecColumn("cand_pty_affiliation", "party_affiliation",           pa.string()),
    FecColumn("cand_office",          "office",                      pa.string()),
    FecColumn("cand_office_st",       "office_state",                pa.string()),
    FecColumn("cand_office_district", "office_district",             pa.string()),
    FecColumn("conduit_cmte_id",      "conduit_committee_id",        pa.string()),
    FecColumn("conduit_cmte_nm",      "conduit_committee_name",      pa.string()),
    FecColumn("conduit_cmte_st1",     "conduit_street_1",            pa.string()),
    FecColumn("conduit_cmte_st2",     "conduit_street_2",            pa.string()),
    FecColumn("conduit_cmte_city",    "conduit_city",                pa.string()),
    FecColumn("conduit_cmte_st",      "conduit_state",               pa.string()),
    FecColumn("conduit_cmte_zip",     "conduit_zip",                 pa.string()),
    FecColumn("transaction_dt",       "transaction_date",            pa.string()),
    FecColumn("transaction_amt",      "transaction_amount",          pa.float64()),
    FecColumn("purpose",              "purpose",                     pa.string()),
    FecColumn("memo_cd",              "memo_code",                   pa.string()),
    FecColumn("memo_text",            "memo_text",                   pa.string()),
    FecColumn("sub_id",               "submission_id",               pa.int64()),
    FecColumn("file_num",             "file_number",                 pa.int64()),
    FecColumn("tran_id",              "transaction_id",              pa.string()),
    FecColumn("back_ref_tran_id",     "back_reference_transaction_id", pa.string()),
]
