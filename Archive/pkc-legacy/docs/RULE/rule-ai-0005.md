# Prefer Official API Before QE

**ID:** `RULE-AI-0005`
**Kind:** `rule`

**Status:** active

**Confidence:** high

**Severity:** warning

## Purpose

Prevent unsafe or hallucinated AI behavior when developing Premiere Pro automation.

## Rule

QE-dependent workflows must be treated as fallback or user-approved experimental paths.

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
