---
id: SER-0001
title: Premiere XML Serialization
section: serialization
status: foundation
confidence: mixed
---

# Premiere XML Serialization

**Document ID:** `SER-0001`  
**Section:** `serialization`  
**Status:** Foundation draft

Premiere XML is an interchange layer, not a complete representation of every internal project state. XML workflows must preserve references and avoid lossy round-trips when possible.

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
