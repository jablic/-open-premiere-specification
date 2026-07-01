---
id: examples-index
title: Examples Index
category: reference
status: current
stability: active
doc_status: complete
introduced: "2024"
min_premiere_version: null
api_namespace: null
languages: [javascript, extendscript, python, html, css]
tags: [examples, reference, production-code, batch-operations, automation]
related: [extendscript-core, uxp, cep, export-rendering-media-encoder, markers-and-annotations, media-linking-batch-operations, captions, panels, debugging]
sources: [
  "Production testing: Premiere 24.x, 25.x"
]
confidence: high
last_verified: "2026-07-01"
verified_against_version: "25.6"
---

# Examples Index

Production-ready code examples for common Premiere automation tasks.

---

## ExtendScript Examples

### update-mogrt-text.jsx
Update MOGRT (Animated Graphic) text dynamically. See: `Examples/extendscript/update-mogrt-text.jsx`

### batch-export-guarded.jsx
Batch export sequences with HEVC/H.265 guard. See: `Examples/extendscript/batch-export-guarded.jsx`

### cep-bridge-safe.jsx
Safe CEP panel ↔ ExtendScript communication with error wrapping. See: `Examples/extendscript/cep-bridge-safe.jsx`

### qe-safe-wrapper.jsx
QE DOM utilities with bounds checking and error handling. See: `Examples/extendscript/qe-safe-wrapper.jsx`

### markers-batch-add.jsx
Batch create timeline markers with colors and metadata from JSON spec. See: `Examples/markers-batch-add.jsx`

### media-batch-relink.jsx
Batch relink offline media, import new files, generate report. See: `Examples/media-batch-relink.jsx`

### captions-batch-read.jsx
Extract captions from timeline, export to SRT/CSV, analyze statistics. See: `Examples/captions-batch-read.jsx`

### batch-import-organize.jsx
Intelligent batch media import with auto-organization by type/resolution, proxy generation. See: `Examples/batch-import-organize.jsx`

### batch-effects-filters.jsx
Batch apply effects/filters to clips by name pattern, with effect presets (warm, cold, vintage, cinematic). See: `Examples/batch-effects-filters.jsx`

---

## UXP Examples

### list-sequences.jsx
List all sequences with metadata (async). See: `Examples/uxp/list-sequences.jsx`

### batch-effects-captions.jsx
Batch apply effects and captions using UXP. See: `Examples/uxp/batch-effects-captions.jsx`

### uxp-async-patterns.js
Comprehensive async/await patterns, createSequenceFromMedia, batch markers, error handling. See: `Examples/uxp-async-patterns.js`

---

## Python Examples

### parse_premiere_fcpxml.py
Parse FCP7 XML exported from Premiere Pro. Extracts clips, markers, timing. See: `Examples/python/parse_premiere_fcpxml.py`

---

## Organization & Version Matrix

| Example | Language | Min Version | Status |
|---|---|---|---|
| update-mogrt-text.jsx | ExtendScript | 14.1 | ✅ Production |
| batch-export-guarded.jsx | ExtendScript | 24.x | ✅ Production |
| markers-batch-add.jsx | ExtendScript | 14.x | ✅ Production |
| media-batch-relink.jsx | ExtendScript | 14.x | ✅ Production |
| captions-batch-read.jsx | ExtendScript | 20.x | ✅ Production |
| batch-import-organize.jsx | ExtendScript | 14.x | ✅ Production |
| batch-effects-filters.jsx | ExtendScript | 14.x | ✅ Production |
| cep-bridge-safe.jsx | ExtendScript | 25.x | ⚠️ Legacy |
| qe-safe-wrapper.jsx | ExtendScript | 24.x | ⚠️ Undocumented |
| cep-theme-sync-panel.jsx+html | CEP (HTML/JS) | 14.x | ✅ Production |
| uxp-responsive-rubber-panel.html | UXP panel | 25.6 | ✅ Current |
| list-sequences.jsx | UXP/JavaScript | 25.6 | ✅ Current |
| batch-effects-captions.jsx | UXP/JavaScript | 25.6 | ✅ Current |
| uxp-async-patterns.js | UXP/JavaScript | 25.6 | ✅ Current |
| parse_premiere_fcpxml.py | Python | 3.8+ | ✅ Current |

---

## See Also

- PROJECT_SPECIFICATION.md — Authoring rules
- README.md — Knowledge base index
- Individual Knowledge/*.md docs — Full reference
