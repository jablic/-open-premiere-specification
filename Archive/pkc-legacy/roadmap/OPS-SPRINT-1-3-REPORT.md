# OPS Sprint 1.3 Report — Graph Integrity and CI

## Summary

Sprint 1.3 fixes the broken references reported by `tools/ops_graph.py validate` and adds the first GitHub Actions workflow for continuous validation.

## Added

### Tests

- TEST-0002 — Active project context must be resolved before mutation
- TEST-0004 — Project inventory must traverse project-level containers
- TEST-0005 — Project destructive edit requires backup or rollback path
- TEST-0006 — Bin display name is not a stable unique identifier
- TEST-0007 — Bin deletion must not be treated as filesystem media deletion
- TEST-0009 — ProjectItem may represent media or a sequence
- TEST-0010 — ProjectItem relink is a project-level reference operation
- TEST-0012 — Sequence destructive timeline edit requires duplicate or rollback path
- TEST-0013 — Sequence does not own source media files

### Automation

- `.github/workflows/ci.yml` validates the repository on push and pull requests.
- `.gitignore` excludes generated artifacts and local cache files.

## Expected Validation

After applying this sprint:

```bash
python3 tools/ops_graph.py build
python3 tools/ops_graph.py validate
python3 tools/pkc.py all
python3 tools/pkc.py validate
pytest -q
```

Expected graph validation result:

```text
OK: graph validation passed.
```

## Engineering Impact

This sprint converts validator failures into explicit knowledge cards, making previously dangling graph references real, reviewable test entities.
