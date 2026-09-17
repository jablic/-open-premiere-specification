# Preserve Object Identity

**ID:** `RULE-AI-0002`
**Kind:** `rule`

**Confidence:** high

**Severity:** critical

## Purpose

This specification is generated from Knowledge Source Language.

## Rule

AI MUST preserve object identity and must not equate objects by display name.

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
