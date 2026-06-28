# No Fake APIs

**ID:** `RULE-AI-0001`
**Kind:** `rule`

**Confidence:** high

**Severity:** critical

## Purpose

This specification is generated from Knowledge Source Language.

## Rule

AI MUST NOT invent Premiere API methods such as sequence.captions or project.exportCaptions().

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
