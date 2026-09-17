---
id: OBJ-0009
title: Caption Object
section: objects
status: foundation
confidence: mixed
---

# Caption Object

**Document ID:** `OBJ-0009`  
**Section:** `objects`  
**Status:** Foundation draft

Caption is a timed text object that may include text, timing, style runs, formatting metadata and internal serialization constraints.

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
