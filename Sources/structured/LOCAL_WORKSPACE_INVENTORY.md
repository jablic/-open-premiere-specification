# Canonical local workspace inventory — 2026-09-16

This checkout is the canonical local source of truth for Adobe Premiere Pro plugin and extension development. It is structurally richer than the current remote `main`: it contains machine-readable specifications, generated references, source inventories, rules, recipes, tests, and production workflow material.

## Primary content

| Area | Purpose |
| --- | --- |
| `spec_src/` | Versioned API, object, capability, rule, recipe, serialization, benchmark, caption, and test YAML source files. |
| `knowledge/` | Evidence-backed capabilities, objects, workflows, policy rules, and behavioural tests. |
| `developer_reference/` | Developer-facing API contracts, source policy, terminology, and evidence guidance. |
| `inventory/` | UXP, CEP, ExtendScript, and SDK surface inventories. |
| `docs/` | Generated human-readable API, object, rule, recipe, benchmark, and test references. |
| `Examples/` | Production-oriented ExtendScript, CEP, UXP, FCP XML, caption, and export examples. |
| `knowledge_os/`, `tools/`, `tests/` | Compiler, generators, validation tools, and automated tests. |

## Git relationship

The local branch is 6 commits ahead of and 20 commits behind GitHub `origin/main`; the histories reflect incompatible knowledge-base architectures. Do not merge them mechanically. The GitHub `main` snapshot and the VFX/UXP, v2, and PKC v0.6 versions are preserved in the parent workspace `Backup/2026-09-16/`.

## Validation

Run the local test suite with:

```sh
../_tools/venv/bin/python -m pytest -q
```
