---
id: BUG-CAP-0001
title: Caption Run Length Mismatch
section: bugs
status: foundation
confidence: mixed
---

# Caption Run Length Mismatch

**Document ID:** `BUG-CAP-0001`  
**Section:** `bugs`  
**Status:** Foundation draft

A mismatch between caption text length and style/font run lengths may cause incorrect formatting, import errors or silent corruption.

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
