---
id: RULE-AI-0001
title: No Fake APIs
section: rules
status: foundation
confidence: mixed
---

# No Fake APIs

**Document ID:** `RULE-AI-0001`  
**Section:** `rules`  
**Status:** Foundation draft

AI MUST NOT generate Premiere Pro methods that are not documented, verified, or explicitly labeled as hypothetical. Examples of unsafe hallucinations include `sequence.captions` and `project.exportCaptions()` when unsupported.

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
