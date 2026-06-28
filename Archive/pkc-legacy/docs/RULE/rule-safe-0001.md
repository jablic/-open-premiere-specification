# Backup Before Destructive Operations

**ID:** `RULE-SAFE-0001`
**Kind:** `rule`

**Confidence:** high

**Severity:** critical

## Purpose

This specification is generated from Knowledge Source Language.

## Rule

Production workflows MUST create backup or duplicate sequence before batch mutation.

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
