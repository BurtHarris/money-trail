"""FEC schema definitions.

Each sub-module (indiv, cn, cm, etc.) defines an ordered ``COLUMNS`` list of
:class:`FecColumn` entries that serve as the single source of truth for raw
column names, readable aliases, and pyarrow types used across the pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass

import pyarrow as pa


@dataclass(frozen=True)
class FecColumn:
    """Metadata for a single column in an FEC bulk data file.

    Attributes:
        fec_name: The FEC-assigned raw column name (as found in the bulk file).
        alias: A human-readable alias applied in dbt staging models.
        pa_type: The pyarrow data type used when loading the raw file.
    """

    fec_name: str
    alias: str
    pa_type: pa.DataType
