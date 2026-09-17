---
id: ADR-0002
title: ADR-0002 AI Native Specification
section: foundation
status: foundation
confidence: mixed
---

# ADR-0002 AI Native Specification

**Document ID:** `ADR-0002`  
**Section:** `foundation`  
**Status:** Foundation draft

The repository is designed as a specification for AI agents, not only a human-readable manual.

## AI Rules

- Do not invent unsupported Premiere Pro APIs.
- Preserve unknown fields during serialization workflows.
- Identify object ownership before proposing automation.
- Prefer reversible workflows: backup, duplicate sequence, export XML, validate.

## Validation Checklist

- [ ] Object identity is preserved.
- [ ] Scope of operation is explicit.
- [ ] Version assumptions are stated.
- [ ] Destructive changes have rollback.
- [ ] Generated code avoids fake methods.
