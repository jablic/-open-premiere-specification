---
id: EXP-0000
title: Reverse Engineering Overview
section: reverse-engineering
status: foundation
confidence: mixed
---

# Reverse Engineering Overview

**Document ID:** `EXP-0000`  
**Section:** `reverse-engineering`  
**Status:** Foundation draft

Reverse engineering notes are separated from documented APIs and marked by confidence level.

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
