# indiv ZIP Loads Root File Only; Date-Range Partials Excluded

DuckDB can read directly from ZIP archives without extracting to disk. For most FEC file types this works without special handling — the ZIP contains exactly one `.txt` file. The `indiv` ZIP is the exception: it contains a root-level full-cycle file (`itcont.txt`) and a subdirectory of date-range-limited partial files (e.g., `by_date/itcont_*.txt`) that are subsets of the same data. Loading without explicit path selection causes DuckDB to glob all matching files, producing duplicates.

The load task explicitly targets the root-level file by path within the ZIP (e.g., `read_csv('indiv24.zip!itcont.txt', ...)`). The date-range partials are ignored. This decision is revisitable if incremental loading by date range is introduced later.
