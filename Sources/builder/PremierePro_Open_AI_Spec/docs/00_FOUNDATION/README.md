---
id: FOUND-0000
title: Foundation Overview
section: foundation
status: foundation
confidence: mixed
---

# Foundation Overview

**Document ID:** `FOUND-0000`  
**Section:** `foundation`  
**Status:** Foundation draft

The foundation layer defines repository standards, terminology, confidence levels, document IDs, ADRs and build conventions.

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
