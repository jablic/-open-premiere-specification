---
id: examples-index
title: Examples Index
category: meta
status: current
stability: active
doc_status: partial
introduced: null
deprecated: null
eol: null
min_premiere_version: null
api_namespace: none
languages: [extendscript, javascript-es3, python]
tags: [examples, index, snippets, reference-code, runnable]
related: [extendscript-core, essential-graphics-mogrt-text, sequences-tracks-trackitems, export-rendering-media-encoder, xml-fcpxml, automation]
supersedes: []
superseded_by: []
sources: []
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
---

# Examples Index

Runnable samples live in [`/Examples`](../Examples), organized by runtime. Each is self-contained and
production-oriented per `PROJECT_SPECIFICATION.md` §8. Paths below are relative to the repo root.

## TL;DR
- ExtendScript samples assume **json2.js** is bundled and target **Premiere 14.x+**.
- The Python sample uses the **standard library only** (Python 3.8+).
- Every sample names its source/topic doc in a header comment.

## Catalog

| File | Runtime | Min ver | Demonstrates | Topic doc |
|---|---|---|---|---|
| [`Examples/extendscript/update-mogrt-text.jsx`](../Examples/extendscript/update-mogrt-text.jsx) | ExtendScript (ES3) | PPro 14.x+ | Import a MOGRT + set Source Text with correct `fontTextRunLength`; version-correct RGBA; font set | `essential-graphics-mogrt-text` |
| [`Examples/extendscript/batch-export-guarded.jsx`](../Examples/extendscript/batch-export-guarded.jsx) | ExtendScript (ES3) | PPro 14.x+ | Queue every sequence to AME; **HEVC guard** (blocked 25.5+); AME-availability check | `export-rendering-media-encoder` |
| [`Examples/python/parse_premiere_fcpxml.py`](../Examples/python/parse_premiere_fcpxml.py) | Python 3.8+ | — | Parse FCP7 XML: markers → timecode; best-effort Base64 graphics-text extraction | `xml-fcpxml` |

## Planned (not yet added)
- `Examples/extendscript/project-tree-walk.jsx` — recursive ProjectItem/bin enumeration (snippet currently in `sequences-tracks-trackitems` §Working Examples).
- `Examples/uxp/*` — UXP equivalents (async + `executeTransaction`) once the UXP DOM surface is exercised.
- `Examples/extendscript/qe-apply-effect.jsx` — effect-by-name via QE DOM (undocumented; see `reverse-engineering-qe-dom`).

## Contribution rule
A snippet graduates from a Knowledge doc into `/Examples` when it is **standalone runnable** (not a
fragment). Add a header comment block (runtime, status, topic doc), keep it ES3-correct for
ExtendScript, and register it in the catalog above.

## Cross-References
- `extendscript-core` · `essential-graphics-mogrt-text` · `sequences-tracks-trackitems` · `export-rendering-media-encoder` · `xml-fcpxml` · `automation`
