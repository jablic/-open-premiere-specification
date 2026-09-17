# Knowledge OS / Premiere Knowledge Compiler v0.6.0

Knowledge OS is an experimental compiler-oriented platform for engineering knowledge.

The first production module is **Premiere Pro Open AI Specification**.

Primary source of truth:

```text
plugins/premiere/spec_src/**/*.yaml
```

Generated outputs:

```text
build/premiere/docs/              Human-readable Markdown
build/premiere/site/              MkDocs site output
build/premiere/artifacts/*.json   AST, graph, rulepack, digital twin
build/premiere/rag/*.jsonl        RAG chunks
```

## Quick start

```bash
python3 -m knowledge_os.cli init-premiere --target /Users/konstantinguryanov/Desktop/APP_AI_MD/PremierePro_Open_AI_Spec --force
cd /Users/konstantinguryanov/Desktop/APP_AI_MD/PremierePro_Open_AI_Spec
python3 tools/pkc.py all
python3 tools/pkc.py serve
```

If port 8000 is busy, `serve` automatically tries the next free port.
