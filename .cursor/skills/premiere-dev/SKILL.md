---
name: premiere-dev
description: >-
  Develop Adobe Premiere Pro extensions, panels, plugins, and automation scripts.
---

# Premiere Pro Development

Machine-readable knowledge base: **open-premiere-specification**

## Quick reference

- Lifecycle: `Knowledge/00-technology-status-matrix.md`
- ExtendScript: `Knowledge/extendscript-core.md`
- MOGRT/text: `Knowledge/essential-graphics-mogrt-text.md`
- Sequences: `Knowledge/sequences-tracks-trackitems.md`
- Export: `Knowledge/export-rendering-media-encoder.md`

**Status:** 20 docs (5 complete, 9 partial, 6 stub)

## Critical traps

- No from-scratch title API — author `.mogrt` in AE → import → patch Source Text JSON
- `fontTextRunLength` must equal `[newText.length]` or text corrupts
- HEVC programmatic export blocked since 25.5 — use H.264 or manual AME
- ExtendScript EOL: 2026-09 — new work → UXP
- CEP 12 = last runtime — build UXP in parallel

## Agent rules

- Never invent API methods
- Distinguish ProjectItem vs TrackItem
- Backup before destructive edits
- Caption text is JSON, not plain text
