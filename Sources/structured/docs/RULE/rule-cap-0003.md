# Do Not Flatten Caption Formatting

**ID:** `RULE-CAP-0003`
**Kind:** `rule`

**Status:** active

**Confidence:** high

**Severity:** warning

## Purpose

Prevent unsafe or hallucinated AI behavior when developing Premiere Pro automation.

## Rule

Caption text replacement must not flatten unknown style runs unless the user explicitly requests plain text output.

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
