Domain docs layout

Layout: Single-context

This repository is configured as a single-context project. Skills that consume domain documentation will look for:

- D:\money-trail\CONTEXT.md — single source of domain language and consumer rules
- D:\money-trail\docs\adr\ — architectural decision records for historical context

If the repo becomes a monorepo with multiple contexts, create a CONTEXT-MAP.md at the root pointing to per-context CONTEXT.md files and update this document.