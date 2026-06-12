"""FEC All-Candidates Financial Summary (weball) schema.

Source: FEC's all-candidates summary file — one record per candidate per
cycle with aggregate financial statistics (total receipts, disbursements,
cash-on-hand, loans, etc.).
FEC bulk download: ``weball{yy}.zip`` containing ``weball.txt``.
"""

from __future__ import annotations

import pyarrow as pa

from include.fec_schemas import FECColumn

COLUMNS: list[FECColumn] = [
    FECColumn("cand_id",              "candidate_id",                   pa.string()),
    FECColumn("cand_name",            "candidate_name",                 pa.string()),
    FECColumn("cand_ici",             "incumbent_challenger_open",      pa.string()),
    FECColumn("pty_cd",               "party_code",                     pa.string()),
    FECColumn("cand_pty_affiliation", "party_affiliation",              pa.string()),
    FECColumn("ttl_receipts",         "total_receipts",                 pa.float64()),
    FECColumn("trans_from_auth",      "transfers_from_authorized",      pa.float64()),
    FECColumn("ttl_disb",             "total_disbursements",            pa.float64()),
    FECColumn("trans_to_auth",        "transfers_to_authorized",        pa.float64()),
    FECColumn("coh_bop",              "cash_on_hand_beginning",         pa.float64()),
    FECColumn("coh_cop",              "cash_on_hand_close",             pa.float64()),
    FECColumn("cand_contrib",         "candidate_contributions",        pa.float64()),
    FECColumn("cand_loans",           "candidate_loans",                pa.float64()),
    FECColumn("other_loans",          "other_loans",                    pa.float64()),
    FECColumn("cand_loan_repay",      "candidate_loan_repayments",      pa.float64()),
    FECColumn("other_loan_repay",     "other_loan_repayments",          pa.float64()),
    FECColumn("debts_owed_by",        "debts_owed_by",                  pa.float64()),
    FECColumn("ttl_indiv_contrib",    "total_individual_contributions", pa.float64()),
    FECColumn("cand_office_st",       "office_state",                   pa.string()),
    FECColumn("cand_office_district", "office_district",                pa.string()),
    FECColumn("spec_election",        "special_election",               pa.string()),
    FECColumn("prim_election",        "primary_election",               pa.string()),
    FECColumn("run_election",         "runoff_election",                pa.string()),
    FECColumn("gen_election",         "general_election",               pa.string()),
    FECColumn("gen_election_precent", "general_election_percent",       pa.float64()),
    FECColumn("other_pol_cmte_contrib","other_committee_contributions", pa.float64()),
    FECColumn("pol_pty_contrib",      "party_contributions",            pa.float64()),
    FECColumn("cvg_end_dt",           "coverage_end_date",              pa.string()),
    FECColumn("indiv_refunds",        "individual_refunds",             pa.float64()),
    FECColumn("cmte_refunds",         "committee_refunds",              pa.float64()),
]
