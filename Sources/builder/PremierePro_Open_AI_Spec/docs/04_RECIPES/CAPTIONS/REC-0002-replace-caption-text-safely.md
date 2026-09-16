---
id: REC-0002
title: Replace Caption Text Safely
section: recipes
status: foundation
confidence: mixed
---

# Replace Caption Text Safely

**Document ID:** `REC-0002`  
**Section:** `recipes`  
**Status:** Foundation draft

Safe caption replacement requires identifying caption source format, preserving timing, validating text/style runs and testing import/export before applying changes to a production sequence.

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
