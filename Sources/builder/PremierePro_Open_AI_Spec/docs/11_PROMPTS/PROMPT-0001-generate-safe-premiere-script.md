---
id: PROMPT-0001
title: Generate Safe Premiere Script Prompt
section: prompts
status: foundation
confidence: mixed
---

# Generate Safe Premiere Script Prompt

**Document ID:** `PROMPT-0001`  
**Section:** `prompts`  
**Status:** Foundation draft

Prompt pattern: identify Premiere version, operation target, API availability, backup workflow, safe code generation and validation steps before generating ExtendScript, UXP or Python.

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
