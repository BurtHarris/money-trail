"""FEC Candidate Master (cn) schema.

Source: Candidate master file — one record per candidate per cycle.
FEC bulk download: ``cn{yy}.zip`` containing ``cn.txt``.
"""

from __future__ import annotations

import pyarrow as pa

from include.fec_schemas import FECColumn

COLUMNS: list[FECColumn] = [
    FECColumn("cand_id",              "candidate_id",              pa.string()),
    FECColumn("cand_name",            "candidate_name",            pa.string()),
    FECColumn("cand_pty_affiliation", "party_affiliation",         pa.string()),
    FECColumn("cand_election_yr",     "election_year",             pa.int16()),
    FECColumn("cand_office_st",       "office_state",              pa.string()),
    FECColumn("cand_office",          "office",                    pa.string()),
    FECColumn("cand_office_district", "office_district",           pa.string()),
    FECColumn("cand_ici",             "incumbent_challenger_open", pa.string()),
    FECColumn("cand_status",          "candidate_status",          pa.string()),
    FECColumn("cand_pcc",             "principal_campaign_cmte",   pa.string()),
    FECColumn("cand_st1",             "mailing_address_1",         pa.string()),
    FECColumn("cand_st2",             "mailing_address_2",         pa.string()),
    FECColumn("cand_city",            "mailing_city",              pa.string()),
    FECColumn("cand_st",              "mailing_state",             pa.string()),
    FECColumn("cand_zip",             "mailing_zip",               pa.string()),
]
