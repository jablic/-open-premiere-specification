---
id: RULE-AI-0002
title: Preserve Object Identity
section: rules
status: foundation
confidence: mixed
---

# Preserve Object Identity

**Document ID:** `RULE-AI-0002`  
**Section:** `rules`  
**Status:** Foundation draft

AI MUST NOT infer identity from visible name, track position, UI order or filename alone. Stable identifiers or explicit references are required when available.

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
