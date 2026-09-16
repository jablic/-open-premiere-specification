---
id: OBJ-0002
title: Project Object
section: objects
status: foundation
confidence: mixed
---

# Project Object

**Document ID:** `OBJ-0002`  
**Section:** `objects`  
**Status:** Foundation draft

Project owns bins, project items, metadata, sequences and global project-level state. A project is not a timeline.

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
