"""FEC Committee Master (cm) schema.

Source: Committee master file — one record per registered committee.
FEC bulk download: ``cm{yy}.zip`` containing ``cm.txt``.
"""

from __future__ import annotations

import pyarrow as pa

from include.fec_schemas import FECColumn

COLUMNS: list[FECColumn] = [
    FECColumn("cmte_id",             "committee_id",        pa.string()),
    FECColumn("cmte_nm",             "committee_name",      pa.string()),
    FECColumn("tres_nm",             "treasurer_name",      pa.string()),
    FECColumn("cmte_st1",            "street_1",            pa.string()),
    FECColumn("cmte_st2",            "street_2",            pa.string()),
    FECColumn("cmte_city",           "city",                pa.string()),
    FECColumn("cmte_st",             "state",               pa.string()),
    FECColumn("cmte_zip",            "zip_code",            pa.string()),
    FECColumn("cmte_dsgn",           "designation",         pa.string()),
    FECColumn("cmte_tp",             "committee_type",      pa.string()),
    FECColumn("cmte_pty_affiliation","party_affiliation",   pa.string()),
    FECColumn("cmte_filing_freq",    "filing_frequency",    pa.string()),
    FECColumn("org_tp",              "interest_group_type", pa.string()),
    FECColumn("connected_org_nm",    "connected_org_name",  pa.string()),
    FECColumn("cand_id",             "candidate_id",        pa.string()),
]
