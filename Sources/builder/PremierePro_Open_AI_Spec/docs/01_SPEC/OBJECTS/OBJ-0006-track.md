---
id: OBJ-0006
title: Track Object
section: objects
status: foundation
confidence: mixed
---

# Track Object

**Document ID:** `OBJ-0006`  
**Section:** `objects`  
**Status:** Foundation draft

Track owns ordered TrackItems of a compatible media type. Track index and visual order must not be treated as stable identity.

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
