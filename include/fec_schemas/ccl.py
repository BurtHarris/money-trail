"""FEC Candidate-Committee Linkage (ccl) schema.

Source: Candidate-committee linkage file — maps candidates to their
authorized committees.
FEC bulk download: ``ccl{yy}.zip`` containing ``ccl.txt``.
"""

from __future__ import annotations

import pyarrow as pa

from include.fec_schemas import FECColumn

COLUMNS: list[FECColumn] = [
    FECColumn("cand_id",          "candidate_id",   pa.string()),
    FECColumn("cand_election_yr", "election_year",  pa.int16()),
    FECColumn("fec_election_yr",  "fec_election_yr",pa.int16()),
    FECColumn("cmte_id",          "committee_id",   pa.string()),
    FECColumn("cmte_tp",          "committee_type", pa.string()),
    FECColumn("cmte_dsgn",        "designation",    pa.string()),
    FECColumn("linkage_id",       "linkage_id",     pa.int64()),
]
