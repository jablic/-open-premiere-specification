---
id: REC-0001
title: Create VFX List from Premiere
section: recipes
status: foundation
confidence: mixed
---

# Create VFX List from Premiere

**Document ID:** `REC-0001`  
**Section:** `recipes`  
**Status:** Foundation draft

Pipeline: locked Premiere sequence → markers with CG shot IDs → XML export → Python parser → thumbnails/previews with ffmpeg → XLSX/CSV VFX list → review and delivery.

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
