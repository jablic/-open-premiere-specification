# Knowledge OS / Premiere Knowledge Compiler v0.7.0

PKC compiles a YAML knowledge source tree into human documentation, AI rulepacks, RAG chunks, JSON AST, graph data, Digital Twin data and test manifests.

## Install to Desktop

```bash
python3 bootstrap_to_desktop.py
```

## Create / refresh Premiere specification repository

```bash
cd /Users/konstantinguryanov/Desktop/APP_AI_MD/Knowledge_OS_PKC_v0_7_0
python3 -m knowledge_os.cli init-premiere --target /Users/konstantinguryanov/Desktop/APP_AI_MD/PremierePro_Open_AI_Spec --force

cd /Users/konstantinguryanov/Desktop/APP_AI_MD/PremierePro_Open_AI_Spec
python3 tools/pkc.py all
python3 tools/pkc.py stats
python3 tools/pkc.py query Caption
python3 tools/pkc.py serve
```

## Agent ingestion priority

1. `build/artifacts/knowledge_ast.json`
2. `build/artifacts/ai_rulepack.json`
3. `build/artifacts/digital_twin.json`
4. `build/rag/rag_chunks.jsonl`
5. `docs/`
