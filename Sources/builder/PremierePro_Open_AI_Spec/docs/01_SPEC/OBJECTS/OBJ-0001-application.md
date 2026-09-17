---
id: OBJ-0001
title: Application Object
section: objects
status: foundation
confidence: mixed
---

# Application Object

**Document ID:** `OBJ-0001`  
**Section:** `objects`  
**Status:** Foundation draft

Application is the top-level runtime context. It owns the active Project session and exposes supported automation entry points through available APIs.

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
