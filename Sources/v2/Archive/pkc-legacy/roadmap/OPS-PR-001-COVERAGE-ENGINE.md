# OPS PR-001 — Coverage Engine

Status: implemented

## Purpose

Add a machine-readable coverage engine for the OPS knowledge graph.

The coverage engine measures structural readiness of Knowledge Cards without
claiming factual completeness. It is designed to become the primary project KPI
as the knowledge base grows.

## Added

- `tools/ops_coverage.py`
- `tests/test_ops_coverage.py`
- CI steps for coverage build and validation
- generated outputs:
  - `build/coverage/coverage.json`
  - `build/coverage/coverage.md`

## Validation

Expected local commands:

```bash
python3 tools/ops_graph.py build
python3 tools/ops_graph.py validate
python3 tools/ops_coverage.py build
python3 tools/ops_coverage.py validate
python3 tools/pkc.py all
python3 tools/pkc.py validate
pytest -q
```

## Notes

Coverage v0.1 is intentionally conservative. It checks graph structure and
basic readiness signals such as tests and evidence. Stricter semantic coverage
rules should be added after the compiler core is refactored into a reusable
library.
