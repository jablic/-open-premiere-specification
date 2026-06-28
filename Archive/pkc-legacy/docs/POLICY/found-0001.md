# Knowledge Source and Confidence Policy

**ID:** `FOUND-0001`
**Kind:** `policy`

**Status:** active

**Confidence:** high

## Purpose

Define how documented facts, reverse-engineered observations, inferred rules and hypotheses are stored without mixing confidence levels.

## Summary

Every technical claim SHOULD carry a confidence level. AI agents MUST prefer documented and experimentally verified facts over inferred or hypothetical claims.

## References

- Adobe UXP for Premiere Pro official documentation
- Premiere Pro Scripting Guide public compendium
- AdobeDocs UXP Premiere samples

## Constraints

- Use DOCUMENTED for official Adobe documentation or official samples.
- Use REVERSE_ENGINEERED only for reproducible experiments.
- Use INFERRED only when derived from confirmed facts.
- Use HYPOTHESIS only for unverified research notes.

## AI Rules

- When confidence is low, say so explicitly.
- Never convert a hypothesis into a production rule without validation.

## External / Source References

- Adobe UXP for Premiere Pro official documentation
- Premiere Pro Scripting Guide public compendium
- AdobeDocs UXP Premiere samples

## Knowledge Links

- `references` → `Adobe UXP for Premiere Pro official documentation`
- `references` → `Premiere Pro Scripting Guide public compendium`
- `references` → `AdobeDocs UXP Premiere samples`

## Agent Notes

- Treat this page as compiled output. Edit the YAML source, not this Markdown file.
- Machine-readable authority lives in `build/artifacts/knowledge_ast.json`.
