# Distinguish MOGRT Source and Instance

**ID:** `RULE-MOGRT-0001`
**Kind:** `rule`

**Status:** active

**Confidence:** high

**Severity:** error

## Purpose

Prevent unsafe or hallucinated AI behavior when developing Premiere Pro automation.

## Rule

AI must distinguish a MOGRT file/source from a timeline instance with editable parameters.

## Validation

- Check generated answer for rule compliance.

## Prevents

- Unsupported code generation
- Data loss
- Wrong API-layer assumptions

## Related

- FOUND-0001
- FOUND-0002

## Knowledge Links

- `related` → `FOUND-0001`
- `related` → `FOUND-0002`
- `prevents` → `Unsupported code generation`
- `prevents` → `Data loss`
- `prevents` → `Wrong API-layer assumptions`

## Agent Notes

- Treat this page as compiled output. Edit the YAML source, not this Markdown file.
- Machine-readable authority lives in `build/artifacts/knowledge_ast.json`.
