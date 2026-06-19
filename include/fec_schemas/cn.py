"""FEC Candidate Master (cn) schema.

Source: Candidate master file — one record per candidate per cycle.
FEC bulk download: ``cn{yy}.zip`` containing ``cn.txt``.
"""

from __future__ import annotations

import pyarrow as pa

from include.fec_schemas import FecColumn

COLUMNS: list[FecColumn] = [
    FecColumn("cand_id",              "candidate_id",              pa.string()),
    FecColumn("cand_name",            "candidate_name",            pa.string()),
    FecColumn("cand_pty_affiliation", "party_affiliation",         pa.string()),
    FecColumn("cand_election_yr",     "election_year",             pa.int16()),
    FecColumn("cand_office_st",       "office_state",              pa.string()),
    FecColumn("cand_office",          "office",                    pa.string()),
    FecColumn("cand_office_district", "office_district",           pa.string()),
    FecColumn("cand_ici",             "incumbent_challenger_open", pa.string()),
    FecColumn("cand_status",          "candidate_status",          pa.string()),
    FecColumn("cand_pcc",             "principal_campaign_cmte",   pa.string()),
    FecColumn("cand_st1",             "mailing_address_1",         pa.string()),
    FecColumn("cand_st2",             "mailing_address_2",         pa.string()),
    FecColumn("cand_city",            "mailing_city",              pa.string()),
    FecColumn("cand_st",              "mailing_state",             pa.string()),
    FecColumn("cand_zip",             "mailing_zip",               pa.string()),
]
