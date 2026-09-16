---
id: examples-index
title: Examples Index
category: meta
status: current
stability: active
doc_status: complete
introduced: null
deprecated: null
eol: null
min_premiere_version: null
api_namespace: none
languages: [extendscript, javascript-es3, python]
tags: [examples, index, snippets, reference-code, runnable]
related: [extendscript-core, essential-graphics-mogrt-text, sequences-tracks-trackitems, export-rendering-media-encoder, xml-fcpxml, automation, best-practices, premiere-dom-overview]
supersedes: []
superseded_by: []
sources: []
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
---

# Examples Index

Runnable samples live in [`/Examples`](../Examples), organized by runtime. Each sample is
self-contained, production-oriented, and follows `PROJECT_SPECIFICATION.md` §8 code rules. Paths below
are relative to the repo root.

## TL;DR
- **3 runnable samples** today: 2 ExtendScript (`.jsx`) + 1 Python (`.py`).
- ExtendScript samples assume **json2.js** is bundled alongside and target **Premiere 14.x+** (New-World scripting).
- The Python sample uses the **standard library only** (Python 3.8+).
- Every sample names its source topic doc in a header comment block.
- Snippets embedded in Knowledge docs graduate here when they become **standalone runnable** (not fragments).

## Catalog

### ExtendScript (ES3)

| File | Min ver | Demonstrates | Topic doc | Prerequisites | How to run |
|---|---|---|---|---|---|
| [`Examples/extendscript/update-mogrt-text.jsx`](../Examples/extendscript/update-mogrt-text.jsx) | PPro 14.x+ | Import an AE-authored `.mogrt` onto the active sequence; set Source Text with correct `fontTextRunLength`; version-correct RGBA fill color; optional font PostScript name | `essential-graphics-mogrt-text` | **json2.js** (Crockford) in same folder. MOGRT authored in AE with "Allow font/style editing" enabled. Active sequence with at least one video track. Edit `MOGRT_PATH`, `NEW_TEXT`, track index constants at top of file. | **File → Scripts → Run Script File…** in Premiere, or invoke from a CEP panel via `evalScript`. Requires open project + active sequence. |
| [`Examples/extendscript/batch-export-guarded.jsx`](../Examples/extendscript/batch-export-guarded.jsx) | PPro 14.x+ | Queue **every sequence** in the open project to Adobe Media Encoder; verify AME installed via `BridgeTalk.getStatus("ame")`; **HEVC/H.265 preset guard** (blocked 25.5+ — refuses preset and logs warning); bind encoder completion/error events | `export-rendering-media-encoder` | Absolute path to an **H.264** `.epr` preset. AME installed. Edit `OUTPUT_DIR` and `EPR_PATH` at top of file. | **File → Scripts → Run Script File…** in Premiere with a project containing sequences. AME will launch/queue. Do **not** use HEVC presets on 25.5+. |

#### ExtendScript shared requirements

All `.jsx` samples in this repo follow these rules:

- **ES3 syntax only** — `var`, `function`, no arrows, no template literals, no native `JSON`.
- **json2.js bundled** — include via `//@include "json2.js"` and guard with `typeof JSON === "undefined"` check.
- **Return envelopes** — host functions return `{ ok, err, ... }` objects (JSON-stringified when called from CEP).
- **Validation chain** — project → sequence → target objects validated before mutation (see `best-practices`).
- **Header comment block** — runtime, status, topic doc, requirements, and usage instructions.

### Python

| File | Min ver | Demonstrates | Topic doc | Prerequisites | How to run |
|---|---|---|---|---|---|
| [`Examples/python/parse_premiere_fcpxml.py`](../Examples/python/parse_premiere_fcpxml.py) | Python 3.8+ | Parse Adobe Premiere Pro **FCP7 XML** (`xmeml`): extract sequence/clip **markers** (name, comment, frame in/out, timecode); best-effort **Base64 graphics-text** extraction from nested `<filter>/<effect>/<data>` nodes | `xml-fcpxml` | Standard library only (`xml.etree`, `json`, `base64`, `re`). Input: `.xml` exported via **File → Export → Final Cut Pro XML** (FCP7 format). | `python3 Examples/python/parse_premiere_fcpxml.py export.xml > out.json` |

#### Python notes

- **No Premiere runtime required** — operates on exported XML files offline.
- Graphics text extraction is **best-effort** — Adobe staff have noted Essential Graphics text is frequently unrecoverable once flattened to FCPXML. For reliable text, use the live scripting API (`essential-graphics-mogrt-text`).
- Output is JSON to stdout; redirect to file for downstream processing.

## Samples by topic

Cross-reference for finding the right example by task:

| Task | Example | Topic doc |
|---|---|---|
| MOGRT text update / Source Text JSON | `update-mogrt-text.jsx` | `essential-graphics-mogrt-text` |
| Batch AME export / HEVC guard | `batch-export-guarded.jsx` | `export-rendering-media-encoder` |
| Marker extraction from export | `parse_premiere_fcpxml.py` | `xml-fcpxml`, `markers` |
| Validation chain pattern | (helpers in `best-practices`) | `best-practices`, `extendscript-core` |
| Project tree walk | (inline in `premiere-dom-overview`) | `premiere-dom-overview`, `sequences-tracks-trackitems` |
| Ticks / Time conversion | (inline in `sequences-tracks-trackitems`) | `sequences-tracks-trackitems` |
| CEP ↔ ExtendScript bridge | (inline in `extendscript-core`) | `extendscript-core`, `cep` |

## Planned (not yet in `/Examples`)

These are documented as inline snippets in Knowledge docs and will graduate to standalone files when exercised end-to-end:

| Planned file | Source snippet location | Notes |
|---|---|---|
| `Examples/extendscript/project-tree-walk.jsx` | `premiere-dom-overview` §Working Examples | Recursive ProjectItem/bin enumeration with JSON output |
| `Examples/extendscript/validation-chain.jsx` | `best-practices` §Working Examples | Extracted guard helpers as a reusable library |
| `Examples/extendscript/import-and-place.jsx` | `import`, `sequences-tracks-trackitems` | importFiles + insertClip with full validation |
| `Examples/extendscript/qe-apply-effect.jsx` | `reverse-engineering-qe-dom` | Effect-by-name via QE DOM (undocumented; experimental) |
| `Examples/extendscript/caption-track-create.jsx` | `captions` | importFiles SRT + createCaptionTrack |
| `Examples/uxp/sequence-edit-actions.js` | `uxp`, `sequences-tracks-trackitems` | UXP async + executeTransaction equivalents |
| `Examples/uxp/import-and-markers.js` | `uxp`, `markers` | UXP import + marker CRUD |

## Contribution rules

A snippet graduates from a Knowledge doc into `/Examples` when it meets all of these criteria:

1. **Standalone runnable** — not a fragment; includes all helpers, guards, and constants it needs.
2. **Header comment block** with: runtime, Premiere min version, lifecycle status, topic doc ID, requirements, usage, and known caveats.
3. **ES3-correct** for ExtendScript (or modern JS with `await`/transactions for UXP).
4. **json2.js guard** for any ExtendScript sample using JSON.
5. **Non-destructive by default** — batch/destructive ops include backup guidance or guards.
6. **Registered in this catalog** — add a row to the table above with prerequisites and run instructions.
7. **Topic doc cross-link** — the source Knowledge doc's Working Examples section should link back to the `/Examples` file.

## Related inline examples (Knowledge docs)

These are complete code blocks inside topic docs (not separate files):

| Location | What it demonstrates |
|---|---|
| `extendscript-core` | json2 bootstrap, active sequence guard, UTF-8 I/O, component param walk, CEP envelope |
| `sequences-tracks-trackitems` | ticks conversion, insertClip, find clip by name, project tree walk, new sequence, trim source |
| `essential-graphics-mogrt-text` | canonical `updateMogrtText`, import + set text, color normalization, cache flush |
| `export-rendering-media-encoder` | queue H.264 export, AME detection, HEVC guard, encoder event binding |
| `captions` | import SRT + createCaptionTrack, count caption tracks |
| `markers` | create/walk/delete markers, set type and color |
| `best-practices` | validation chain helpers, version gates, backup/clone, UTF-8, UXP transaction |
| `premiere-dom-overview` | full project walk, component param lookup |

## Cross-References
- `best-practices` — validation chain, PKC agent rules, version gates
- `extendscript-core` — ES3 runtime rules, json2, CEP bridge patterns
- `essential-graphics-mogrt-text` — MOGRT Source Text JSON contract
- `sequences-tracks-trackitems` — timeline/project DOM, Time objects
- `export-rendering-media-encoder` — AME queue, HEVC block, presets
- `xml-fcpxml` — FCP7 XML format, round-trip limitations
- `automation` — pymiere, BridgeTalk, command-line `.jsx` invocation
- `premiere-dom-overview` — object tree reference for reading sample code
- `00-technology-status-matrix` — which runtime to choose before picking an example
