---
id: REC-0000
title: Recipes Overview
section: recipes
status: foundation
confidence: mixed
---

# Recipes Overview

**Document ID:** `REC-0000`  
**Section:** `recipes`  
**Status:** Foundation draft

Recipes are production workflows with preflight, procedure, validation and recovery steps.

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
