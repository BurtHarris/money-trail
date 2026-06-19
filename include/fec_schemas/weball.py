"""FEC All-Candidates Financial Summary (weball) schema.

Source: FEC's all-candidates summary file — one record per candidate per
cycle with aggregate financial statistics (total receipts, disbursements,
cash-on-hand, loans, etc.).
FEC bulk download: ``weball{yy}.zip`` containing ``weball.txt``.
"""

from __future__ import annotations

import pyarrow as pa

from include.fec_schemas import FecColumn

COLUMNS: list[FecColumn] = [
    FecColumn("cand_id",              "candidate_id",                   pa.string()),
    FecColumn("cand_name",            "candidate_name",                 pa.string()),
    FecColumn("cand_ici",             "incumbent_challenger_open",      pa.string()),
    FecColumn("pty_cd",               "party_code",                     pa.string()),
    FecColumn("cand_pty_affiliation", "party_affiliation",              pa.string()),
    FecColumn("ttl_receipts",         "total_receipts",                 pa.float64()),
    FecColumn("trans_from_auth",      "transfers_from_authorized",      pa.float64()),
    FecColumn("ttl_disb",             "total_disbursements",            pa.float64()),
    FecColumn("trans_to_auth",        "transfers_to_authorized",        pa.float64()),
    FecColumn("coh_bop",              "cash_on_hand_beginning",         pa.float64()),
    FecColumn("coh_cop",              "cash_on_hand_close",             pa.float64()),
    FecColumn("cand_contrib",         "candidate_contributions",        pa.float64()),
    FecColumn("cand_loans",           "candidate_loans",                pa.float64()),
    FecColumn("other_loans",          "other_loans",                    pa.float64()),
    FecColumn("cand_loan_repay",      "candidate_loan_repayments",      pa.float64()),
    FecColumn("other_loan_repay",     "other_loan_repayments",          pa.float64()),
    FecColumn("debts_owed_by",        "debts_owed_by",                  pa.float64()),
    FecColumn("ttl_indiv_contrib",    "total_individual_contributions", pa.float64()),
    FecColumn("cand_office_st",       "office_state",                   pa.string()),
    FecColumn("cand_office_district", "office_district",                pa.string()),
    FecColumn("spec_election",        "special_election",               pa.string()),
    FecColumn("prim_election",        "primary_election",               pa.string()),
    FecColumn("run_election",         "runoff_election",                pa.string()),
    FecColumn("gen_election",         "general_election",               pa.string()),
    FecColumn("gen_election_precent", "general_election_percent",       pa.float64()),
    FecColumn("other_pol_cmte_contrib","other_committee_contributions", pa.float64()),
    FecColumn("pol_pty_contrib",      "party_contributions",            pa.float64()),
    FecColumn("cvg_end_dt",           "coverage_end_date",              pa.string()),
    FecColumn("indiv_refunds",        "individual_refunds",             pa.float64()),
    FecColumn("cmte_refunds",         "committee_refunds",              pa.float64()),
]
