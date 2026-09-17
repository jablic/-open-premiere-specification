---
id: OBJ-0007
title: Component Object
section: objects
status: foundation
confidence: mixed
---

# Component Object

**Document ID:** `OBJ-0007`  
**Section:** `objects`  
**Status:** Foundation draft

Component represents an effect or intrinsic property container attached to a TrackItem. Components expose Properties.

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
