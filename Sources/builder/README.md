# PPAIKB Builder v0.5.0

Premiere Pro Open AI Specification builder.

## New in v0.5.0

- Evaluation and benchmark DSL types.
- Dataset fixture contracts.
- Expanded test manifest: tests, benchmarks, and evaluation rubrics.
- Additional machine-readable artifacts for AI/RAG workflows.

## Bootstrap

```bash
python3 bootstrap_to_desktop.py
cd /Users/konstantinguryanov/Desktop/APP_AI_MD/PPAIKB_Builder
python3 -m ppaikb_builder.cli init --target /Users/konstantinguryanov/Desktop/APP_AI_MD/PremierePro_Open_AI_Spec --force
cd /Users/konstantinguryanov/Desktop/APP_AI_MD/PremierePro_Open_AI_Spec
python3 tools/ppaikb.py all
mkdocs serve
```
