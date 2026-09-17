---
id: EXP-0001
title: Caption JSON Editing Protocol
section: reverse-engineering
status: foundation
confidence: mixed
---

# Caption JSON Editing Protocol

**Document ID:** `EXP-0001`  
**Section:** `reverse-engineering`  
**Status:** Foundation draft

Experiment protocol for editing caption JSON-like structures: isolate sample, duplicate project, export, modify one field, reimport, compare rendering and serialization.

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
