"""FEC Candidate-Committee Linkage (ccl) schema.

Source: Candidate-committee linkage file — maps candidates to their
authorized committees.
FEC bulk download: ``ccl{yy}.zip`` containing ``ccl.txt``.
"""

from __future__ import annotations

import pyarrow as pa

from include.fec_schemas import FecColumn

COLUMNS: list[FecColumn] = [
    FecColumn("cand_id",          "candidate_id",   pa.string()),
    FecColumn("cand_election_yr", "election_year",  pa.int16()),
    FecColumn("fec_election_yr",  "fec_election_yr",pa.int16()),
    FecColumn("cmte_id",          "committee_id",   pa.string()),
    FecColumn("cmte_tp",          "committee_type", pa.string()),
    FecColumn("cmte_dsgn",        "designation",    pa.string()),
    FecColumn("linkage_id",       "linkage_id",     pa.int64()),
]
