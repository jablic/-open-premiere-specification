# Encoder Boundary

**ID:** `API-ENC-0001`
**Kind:** `api`

**Status:** draft

**Confidence:** MEDIUM

## Purpose

Define the boundary, risks and planning rules for Encoder Boundary.

## Summary

Encoding workflows may use Premiere export APIs or Adobe Media Encoder integration. Export plans must specify preset, path, side effects and queue behavior.

## Constraints

- Do not mix APIs in one solution unless the bridging mechanism is explicit.
- Always state whether a proposed method is ExtendScript, UXP, CEP, QE, Python, XML, or external automation.

## AI Rules

- If the API surface is unknown, stop and ask for verification instead of inventing methods.

## Related

- RULE-AI-0001
- FOUND-0001

## Knowledge Links

- `related` → `RULE-AI-0001`
- `related` → `FOUND-0001`

## Agent Notes

- Treat this page as compiled output. Edit the YAML source, not this Markdown file.
- Machine-readable authority lives in `build/artifacts/knowledge_ast.json`.
