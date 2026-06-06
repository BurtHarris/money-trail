# FEC Bulk Downloads Over the REST API

FEC data is sourced from bulk download ZIP files (fec.gov/data/bulk-downloads/) rather than the `api.open.fec.gov` REST API. The API is rate-limited, requires a key for serious use, and returns paginated JSON that is expensive to reconstruct into full cycle snapshots. Bulk files are free, cover complete cycles, and are the authoritative snapshots the FEC publishes. The example DAG in the repo points at the API developer page — that is a placeholder only.
