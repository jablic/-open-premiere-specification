---
id: SER-0002
title: Caption JSON Serialization
section: serialization
status: foundation
confidence: mixed
---

# Caption JSON Serialization

**Document ID:** `SER-0002`  
**Section:** `serialization`  
**Status:** Foundation draft

Caption JSON-like structures must be edited conservatively. Unknown fields, ordering, style runs and run lengths must be preserved.

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
