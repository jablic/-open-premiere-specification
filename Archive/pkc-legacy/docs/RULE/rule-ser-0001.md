# Preserve Unknown Fields

**ID:** `RULE-SER-0001`
**Kind:** `rule`

**Confidence:** high

**Severity:** critical

## Purpose

This specification is generated from Knowledge Source Language.

## Rule

Serializers MUST preserve unknown fields and ordering when modifying structured data.

## Validation

- Check generated code for unsupported members.
- Check output against object model.

## Prevents

- hallucination
- destructive_editing

## Knowledge Links

- `prevents` → `hallucination`
- `prevents` → `destructive_editing`

## Agent Notes

- Treat this page as compiled output. Edit the YAML source, not this Markdown file.
- Machine-readable authority lives in `build/artifacts/knowledge_ast.json`.
