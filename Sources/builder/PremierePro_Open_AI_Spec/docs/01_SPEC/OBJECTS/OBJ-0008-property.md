---
id: OBJ-0008
title: Property Object
section: objects
status: foundation
confidence: mixed
---

# Property Object

**Document ID:** `OBJ-0008`  
**Section:** `objects`  
**Status:** Foundation draft

Property represents an editable parameter. Values may be numeric, boolean, color, time, point, enum, text or complex serialized data.

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
