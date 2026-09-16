---
id: RULE-SER-0001
title: Preserve Unknown Fields
section: rules
status: foundation
confidence: mixed
---

# Preserve Unknown Fields

**Document ID:** `RULE-SER-0001`  
**Section:** `rules`  
**Status:** Foundation draft

Serialization workflows MUST preserve unknown fields byte-for-byte or structure-for-structure whenever possible.

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
