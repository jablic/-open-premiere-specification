---
id: TEST-0000
title: Tests Overview
section: tests
status: foundation
confidence: mixed
---

# Tests Overview

**Document ID:** `TEST-0000`  
**Section:** `tests`  
**Status:** Foundation draft

Tests validate object invariants, serialization safety, link integrity, RAG chunking and generated documentation.

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
