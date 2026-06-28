# Premiere Extension Coding Benchmark

**ID:** `BENCH-0002`
**Kind:** `benchmark`

**Status:** draft

**Confidence:** medium

## Purpose

Evaluate whether an AI agent can design and generate safe Premiere extension code without hallucinating APIs.

## Summary

The benchmark scores API-layer declaration, method verification, safety planning, version awareness, rollback, and explanation quality.

## Uses

- RULE-AI-0001
- RULE-AI-0003
- RULE-UXP-0001
- RULE-EXT-0001

## Metrics

- API correctness
- Safety compliance
- Version awareness
- Rollback quality
- Code clarity
- Evidence chain

## Related

- FOUND-0002

## Knowledge Links

- `uses` → `RULE-AI-0001`
- `uses` → `RULE-AI-0003`
- `uses` → `RULE-UXP-0001`
- `uses` → `RULE-EXT-0001`
- `related` → `FOUND-0002`

## Agent Notes

- Treat this page as compiled output. Edit the YAML source, not this Markdown file.
- Machine-readable authority lives in `build/artifacts/knowledge_ast.json`.
