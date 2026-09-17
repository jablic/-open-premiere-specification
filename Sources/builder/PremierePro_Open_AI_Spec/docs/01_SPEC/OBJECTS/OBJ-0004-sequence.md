---
id: OBJ-0004
title: Sequence Object
section: objects
status: foundation
confidence: mixed
---

# Sequence Object

**Document ID:** `OBJ-0004`  
**Section:** `objects`  
**Status:** Foundation draft

Sequence is a timeline container. It owns tracks and timeline markers but references ProjectItems through TrackItems.

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
