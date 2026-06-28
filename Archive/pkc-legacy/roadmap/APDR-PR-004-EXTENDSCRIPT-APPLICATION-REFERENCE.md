# APDR PR-004 — ExtendScript Application Reference

## Purpose

Adds the first real developer reference chapter for the ExtendScript `app` object. This PR moves the project from framework/template work into concrete Premiere Pro developer documentation.

## Added

- `developer_reference/extendscript/Application/README.md`
- `developer_reference/extendscript/Application/Methods/enableQE.md`
- `inventory/extendscript/application_attributes.csv`
- `inventory/extendscript/application_methods.csv`
- `tests/test_extendscript_application_reference.py`

## Scope

This PR covers inventory and contract-level documentation for the ExtendScript global `app` object. It does not attempt to fully document all returned objects (`Project`, `Encoder`, `Production`, etc.).

## Validation

Expected checks:

```bash
python3 tools/ops_graph.py build
python3 tools/ops_graph.py validate
python3 tools/pkc.py all
python3 tools/pkc.py validate
pytest -q
```

## Next work

- Add method-contract pages for `app.openDocument()`, `app.newProject()`, `app.setEnableProxies()`, and `app.setExtensionPersistent()`.
- Begin `Project` reference chapter.
- Add reproducible experiments for failure modes listed in the Application chapter.
