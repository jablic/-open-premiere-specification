---
id: AP-0000
title: Anti Patterns Overview
section: anti-patterns
status: foundation
confidence: mixed
---

# Anti Patterns Overview

**Document ID:** `AP-0000`  
**Section:** `anti-patterns`  
**Status:** Foundation draft

Anti-patterns document unsafe assumptions that AI systems commonly make when working with Premiere Pro.

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
