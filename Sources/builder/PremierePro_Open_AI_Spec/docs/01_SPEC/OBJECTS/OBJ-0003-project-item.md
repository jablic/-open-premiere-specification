---
id: OBJ-0003
title: Project Item Object
section: objects
status: foundation
confidence: mixed
---

# Project Item Object

**Document ID:** `OBJ-0003`  
**Section:** `objects`  
**Status:** Foundation draft

ProjectItem represents imported media, bins, sequences or other project-level assets. Timeline clips reference ProjectItems but do not own the media itself.

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
