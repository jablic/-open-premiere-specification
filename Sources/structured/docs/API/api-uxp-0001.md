# UXP Boundary

**ID:** `API-UXP-0001`
**Kind:** `api`

**Status:** draft

**Confidence:** DOCUMENTED

## Purpose

Define the boundary, risks and planning rules for UXP Boundary.

## Summary

UXP is the modern plugin and scripting platform for Premiere Pro. UXP exposes the Premiere DOM through require("premierepro"); Premiere operations may require asynchronous calls.

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
