---
name: premiere-dev
description: >-
  Develop Adobe Premiere Pro extensions, panels, plugins, and automation scripts.
  Use when the user asks about Premiere Pro scripting (ExtendScript, UXP, CEP),
  QE DOM, MOGRT/text, export/import, native SDK, FCPXML, captions, markers,
  panels, debugging, or AI/MCP integration for Premiere.
---

# Premiere Pro Development

Machine-readable knowledge base: **open-premiere-specification** (this repo or linked copy).

## Before writing any code

1. **Resolve target Premiere version** — ask if unknown.
2. Read [`Knowledge/00-technology-status-matrix.md`](../Knowledge/00-technology-status-matrix.md) — pick technologies whose `status` + `min_premiere_version` fit.
3. Open the **topic doc** for the task. Read `TL;DR`, `Limitations`, `Common Errors & Gotchas` first.
4. Follow [`PROJECT_SPECIFICATION.md`](../PROJECT_SPECIFICATION.md) §8 code rules.

## Status discipline

| `status` | Agent behavior |
|---|---|
| `current` | Default recommendation |
| `legacy` | Compat only — warn user |
| `deprecated` | Do not recommend — name replacement |
| `undocumented` | Last resort (QE DOM) — flag risk |
| `mixed` | Read per-section notes |

**Never** recommend `deprecated`/`undocumented` APIs as if current.

## Topic routing

| Task | Knowledge doc |
|---|---|
| Lifecycle / which tech to use | `00-technology-status-matrix` |
| ExtendScript / ES3 / json2 | `extendscript-core` |
| MOGRT / Source Text / fonts | `essential-graphics-mogrt-text` |
| Sequences / tracks / bins | `sequences-tracks-trackitems` |
| Export / AME / HEVC | `export-rendering-media-encoder` |
| Import media / MOGRT | `import` |
| Markers | `markers` |
| Captions / subtitles | `captions` |
| CEP panels | `cep` |
| UXP panels / scripting | `uxp` |
| CEP vs UXP panels | `panels` |
| QE DOM / effects by name | `reverse-engineering-qe-dom` |
| C++ / PrSDK / hybrid | `cpp-native-sdk` |
| DOM object map | `premiere-dom-overview` |
| FCPXML / XML / OTIO | `xml-fcpxml` |
| pymiere / automation | `automation` |
| LLM / MCP servers | `ai-integration` |
| Debugging | `debugging` |
| Production rules | `best-practices` |
| Runnable samples | `examples-index` → `Examples/` |

## Code rules (mandatory)

- **ExtendScript = ES3** — no `let`/`const`, arrows, template literals, native `JSON`. Bundle json2.js.
- **UXP = async** — `await` DOM methods; wrap mutations in `executeTransaction`.
- **Validate chain** — project → sequence → track → clip → component → property before use.
- **Version-gate** — Time objects (14.1+), color 0–255 vs 0–1, HEVC block (25.5+), `fontTextRunLength`.
- Label code blocks: `// ExtendScript (ES3) — Premiere 25.x` or `// UXP — Premiere 25.6+`.

## Critical traps (encode in every answer)

- **No from-scratch title API** — author `.mogrt` in AE → import → patch Source Text JSON.
- **`fontTextRunLength` must equal `[newText.length]`** or text corrupts.
- **HEVC programmatic export blocked since 25.5** — use H.264 or manual AME.
- **ExtendScript EOL: 2026-09** — new work → UXP (25.6+).
- **CEP 12 = last runtime** — build UXP in parallel.

## Agent safety rules (from PKC)

- Do NOT invent API methods (e.g. `sequence.captions`, `project.exportCaptions()`).
- Distinguish **ProjectItem** (project bin) from **TrackItem** (timeline clip).
- Distinguish **MOGRT file** from **timeline instance**.
- Sequence does not own source media — relink at ProjectItem level.
- Caption text is serialized JSON, not plain text — preserve unknown fields.
- Backup or duplicate before destructive timeline edits.

## Search locally

If this repo is present, prefer reading Knowledge docs over guessing. Optional build artifacts in `build/query_index.json` and `build/rag_chunks.jsonl` (run `python3 tools/build_index.py`).

## Sources priority

1. Official Adobe docs → 2. SDK/samples → 3. Open-source (bbb999, Bolt CEP, AutoSubs) → 4. Community → 5. RE (confidence: low/medium)
