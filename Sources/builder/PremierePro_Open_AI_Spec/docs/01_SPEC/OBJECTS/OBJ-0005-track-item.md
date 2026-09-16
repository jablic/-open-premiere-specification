---
id: OBJ-0005
title: Track Item Object
section: objects
status: foundation
confidence: mixed
---

# Track Item Object

**Document ID:** `OBJ-0005`  
**Section:** `objects`  
**Status:** Foundation draft

TrackItem is a timeline instance referencing a ProjectItem. Multiple TrackItems may reference the same ProjectItem.

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
