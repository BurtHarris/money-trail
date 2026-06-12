# Architecture docs

Repository-level architecture contracts and restructuring guidance.

## Index

- `repository-restructuring-plan.md` - target-state repository contract and phased migration slices.
- `dev-vs-runtime-topology.md` - boundary contract between devcontainer/editor setup and runtime service topology.
- `data-tier-path-contract.md` - canonical path ownership for `data/` tiers and `exports/`.
- `data-path-reference-inventory.md` - current code/doc references using compatibility paths and migration ordering.

## How to use

1. Read `repository-restructuring-plan.md` for sequencing.
2. Apply topology changes against `dev-vs-runtime-topology.md`.
3. Apply path changes against `data-tier-path-contract.md`.
4. Check ADR alignment before modifying runtime behavior.
