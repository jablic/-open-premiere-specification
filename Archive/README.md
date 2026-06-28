# Archive

Superseded or legacy material kept for history. **Not indexed as current knowledge.**

## `pkc-legacy/`

Previous machine-first PKC (Premiere Knowledge Corpus) architecture:
- YAML knowledge atoms (`knowledge/`, `spec_src/`)
- Granular `docs/API/`, `docs/OBJECT/` cards
- `developer_reference/` book-style TOC
- `tools/pkc.py`, `knowledge_os/` build pipeline
- Generated `build/artifacts/knowledge_graph.json`

**Status:** Archived 2026-06-28. Valuable rules, recipes, and object models were harvested into `Knowledge/best-practices.md` and related topic docs. The authoritative corpus is now `Knowledge/*.md` per `PROJECT_SPECIFICATION.md` v2.0.

To regenerate old PKC artifacts (reference only):
```bash
cd Archive/pkc-legacy
python3 tools/pkc.py all
```
