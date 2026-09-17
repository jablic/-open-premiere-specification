---
id: BUG-0000
title: Bug Database Overview
section: bugs
status: foundation
confidence: mixed
---

# Bug Database Overview

**Document ID:** `BUG-0000`  
**Section:** `bugs`  
**Status:** Foundation draft

The bug database tracks known Premiere Pro automation, serialization and workflow failures with recovery guidance.

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
