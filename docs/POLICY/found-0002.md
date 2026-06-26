# AI Agent Ingestion Contract

**ID:** `FOUND-0002`
**Kind:** `policy`

**Status:** active

**Confidence:** high

## Purpose

Specify how an external AI coding agent should ingest this repository.

## Summary

Agents should use build/artifacts/*.json as machine-readable authority, docs/ as human explanation, and build/rag/rag_chunks.jsonl as retrieval input.

## Steps

- Run python3 tools/pkc.py all.
- Load build/artifacts/knowledge_ast.json.
- Load build/artifacts/ai_rulepack.json before code generation.
- Use build/rag/rag_chunks.jsonl for semantic retrieval.
- Use docs/ only for human-readable explanations.

## Validation

- The agent can answer object/rule/API questions from AST without Markdown search.
- The agent can reject fake APIs using AI rulepack.

## Agent Notes

- Treat this page as compiled output. Edit the YAML source, not this Markdown file.
- Machine-readable authority lives in `build/artifacts/knowledge_ast.json`.
