---
id: AP-0001
title: Caption Plain Text Assumption
section: anti-patterns
status: foundation
confidence: mixed
---

# Caption Plain Text Assumption

**Document ID:** `AP-0001`  
**Section:** `anti-patterns`  
**Status:** Foundation draft

Assuming captions are only plain text is unsafe. Captions can carry timing, styling, run-length data, metadata and version-specific serialization.

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
