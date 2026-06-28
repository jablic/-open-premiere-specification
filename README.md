# Open Premiere Specification

**A machine-readable knowledge base on developing for Adobe Premiere Pro — built for AI coding agents.**

This repository collects, verifies, and structures everything an agent needs to write
**production-grade, version-aware** Premiere extensions: scripting (ExtendScript / UXP), panels
(CEP / UXP), native plugins (C++ PrSDK / AE SDK), interop (FCPXML, pymiere, MCP), and the
undocumented internals (QE DOM). It is not a rewrite of Adobe's docs — it is a curated,
status-tagged, cross-linked corpus optimized for retrieval and code generation.

> **New here (human or agent)? Read [`Knowledge/00-technology-status-matrix.md`](Knowledge/00-technology-status-matrix.md) first.**
> It is the lifecycle authority every other document defers to.

---

## ⚠️ Status banner (the three facts that change every decision)

| Fact | Detail |
|---|---|
| **ExtendScript is dying** | API frozen (2024); supported **through September 2026**. Use only for existing tooling / users below Premiere 25.6. |
| **UXP is the present** | General release in **Premiere 25.6** (Dec 2025). Async DOM, no Chromium bridge — but an **incomplete** API surface (no MOGRT text-blob parity yet). |
| **CEP is on its way out** | **CEP 12 (Premiere 25.0) is the last major runtime.** Loading already degraded in 25.x; some panels broke in Premiere 2026. Build UXP for anything new. |

Plus two recurring traps an agent must encode:
- **No from-scratch title API.** Text-on-timeline = author a `.mogrt` in After Effects → import → patch the Source Text JSON (`fontTextRunLength` **must** equal `[newText.length]`). See [`essential-graphics-mogrt-text`](Knowledge/essential-graphics-mogrt-text.md).
- **HEVC/H.265 programmatic export is blocked since Premiere 25.5, by design.** Use H.264, or render HEVC manually in AME. See [`export-rendering-media-encoder`](Knowledge/export-rendering-media-encoder.md).

---

## How an agent should use this repository

1. **Resolve the target Premiere version** (ask the user if unknown).
2. **Open [`00-technology-status-matrix`](Knowledge/00-technology-status-matrix.md)** → pick technologies whose `status` + `min_premiere_version` fit that target.
3. **Open the topic file** for the task. Read its `status`, `Limitations`, and `Common Errors & Gotchas` before writing code.
4. **Never recommend a `deprecated`/`undocumented` API as if it were current.** If only that path exists, say so, show the safest variant, and state the risk.
5. **Honor the code rules** in [`PROJECT_SPECIFICATION.md`](PROJECT_SPECIFICATION.md) §8 (ES3 + json2.js for ExtendScript; `await` + `executeTransaction` for UXP; validate the whole object chain; version-gate behavior).

---

## Repository structure

```
open-premiere-specification/
  README.md                  ← you are here
  PROJECT_SPECIFICATION.md   ← authoring rules + machine-readable format (read before contributing)
  Knowledge/                 ← the corpus: one .md per authoritative topic (20 docs, all complete)
  Templates/                 ← _TOPIC_TEMPLATE.md (skeleton for new docs)
  Examples/                  ← standalone runnable samples referenced by Knowledge docs
  Research/                  ← raw/unverified findings pending promotion into Knowledge
  Archive/                   ← superseded docs (pkc-legacy/) — never indexed as current
  tools/                     ← validate_frontmatter.py, build_index.py
  .cursor/skills/premiere-dev/  ← Cursor Agent Skill entry point
  build/                     ← generated: query_index.json, rag_chunks.jsonl (gitignored)
```

---

## Knowledge index

Legend — **Status:** `current` · `legacy` · `deprecated` · `undocumented` · `mixed`  |  **Doc:** `complete` · `partial` · `stub`

| Document | Status | Doc | Covers |
|---|---|---|---|
| [00-technology-status-matrix](Knowledge/00-technology-status-matrix.md) | mixed | ✅ complete | Lifecycle + version matrix; **read first** |
| [extendscript-core](Knowledge/extendscript-core.md) | legacy | ✅ complete | ES3 runtime, json2.js, ticks, evalScript bridge |
| [essential-graphics-mogrt-text](Knowledge/essential-graphics-mogrt-text.md) | mixed | ✅ complete | MOGRT import + Source Text JSON, `fontTextRunLength`, fonts |
| [sequences-tracks-trackitems](Knowledge/sequences-tracks-trackitems.md) | legacy | ✅ complete | Editing DOM, Time/ticks, insert/overwrite, project tree |
| [export-rendering-media-encoder](Knowledge/export-rendering-media-encoder.md) | legacy | ✅ complete | `app.encoder`, AME, `.epr`, HEVC block, direct export |
| [cep](Knowledge/cep.md) | legacy | ✅ complete | Panels, manifest, `CSInterface`, Bolt CEP, signing |
| [reverse-engineering-qe-dom](Knowledge/reverse-engineering-qe-dom.md) | undocumented | ✅ complete | `app.enableQE()`, effects-by-name, matchName catalog |
| [uxp](Knowledge/uxp.md) | current | ✅ complete | `premierepro` module, async DOM, UDT, Hybrid plugins |
| [cpp-native-sdk](Knowledge/cpp-native-sdk.md) | current | ✅ complete | PrSDK/AE SDK, importers/exporters/filters, `.uxpaddon` |
| [premiere-dom-overview](Knowledge/premiere-dom-overview.md) | legacy | ✅ complete | Object-model map / API index |
| [xml-fcpxml](Knowledge/xml-fcpxml.md) | current | ✅ complete | FCP7 XML / FCPXML / OTIO, Base64 graphics text |
| [automation](Knowledge/automation.md) | legacy | ✅ complete | pymiere, BridgeTalk, CLI `.jsx` |
| [best-practices](Knowledge/best-practices.md) | current | ✅ complete | Validation chain, version-aware rules, PKC agent rules |
| [import](Knowledge/import.md) | legacy | ✅ complete | `importFiles`, project-item creation |
| [markers](Knowledge/markers.md) | legacy | ✅ complete | Sequence/clip markers, types, colors |
| [captions](Knowledge/captions.md) | legacy | ✅ complete | Caption tracks, SRT/SCC/MCC, AutoSubs |
| [panels](Knowledge/panels.md) | mixed | ✅ complete | CEP vs UXP panel comparison |
| [ai-integration](Knowledge/ai-integration.md) | current | ✅ complete | LLM APIs from panels, MCP servers |
| [debugging](Knowledge/debugging.md) | mixed | ✅ complete | ExtendScript Debugger, DevTools, UDT |
| [examples-index](Knowledge/examples-index.md) | current | ✅ complete | Index of `/Examples` samples |

---

## Original-topic → file map

The original brief enumerated 28 topics; several are the same conceptual unit at the API level.
To honor **one source of truth** (no duplication), tightly-coupled topics are consolidated, and every
original name maps here. Rationale and reversibility: [`PROJECT_SPECIFICATION.md`](PROJECT_SPECIFICATION.md) §6.

| Original topic | File |
|---|---|
| ExtendScript | `Knowledge/extendscript-core.md` |
| CEP | `Knowledge/cep.md` |
| UXP | `Knowledge/uxp.md` |
| C++ · Premiere SDK · Native Plugins · Plugins | `Knowledge/cpp-native-sdk.md` |
| Premiere DOM · Premiere API | `Knowledge/premiere-dom-overview.md` |
| Sequences · Tracks · Project Items · Bins | `Knowledge/sequences-tracks-trackitems.md` |
| Export · Rendering · Media Encoder | `Knowledge/export-rendering-media-encoder.md` |
| Import | `Knowledge/import.md` |
| XML · FCPXML | `Knowledge/xml-fcpxml.md` |
| Markers | `Knowledge/markers.md` |
| Captions | `Knowledge/captions.md` |
| Essential Graphics · Text · Fonts · MOGRT | `Knowledge/essential-graphics-mogrt-text.md` |
| Panels | `Knowledge/panels.md` |
| AI Integration | `Knowledge/ai-integration.md` |
| Automation | `Knowledge/automation.md` |
| Debugging | `Knowledge/debugging.md` |
| Reverse Engineering | `Knowledge/reverse-engineering-qe-dom.md` |
| Best Practices | `Knowledge/best-practices.md` |
| Examples | `Examples/` + `Knowledge/examples-index.md` |

---

## Frontmatter schema (every Knowledge doc)

Each document opens with YAML frontmatter so the corpus is queryable. Required fields: `id`, `title`,
`category`, `status`, `doc_status`, `tags`, `related`, `sources`, `last_verified`, `verified_against_version`.
Full schema + taxonomy: [`PROJECT_SPECIFICATION.md`](PROJECT_SPECIFICATION.md) §5.

```yaml
id: extendscript-core
status: legacy            # current | legacy | deprecated | undocumented | mixed
doc_status: complete      # complete | partial | stub
min_premiere_version: null
api_namespace: app        # app | qe | premierepro | PrSDK | CSInterface | none
related: [cep, uxp, automation]
last_verified: "2026-06-28"
```

---

## Build & validate

```bash
pip install -r requirements.txt
python3 tools/validate_frontmatter.py   # frontmatter + cross-links
python3 tools/build_index.py            # → build/query_index.json, build/rag_chunks.jsonl
```

CI runs both on every push (`.github/workflows/validate.yml`).

## Cursor Agent Skill

Load `.cursor/skills/premiere-dev/SKILL.md` (or install to `~/.cursor/skills/premiere-dev/`) so agents route to the correct Knowledge doc before writing Premiere code.

## Contributing / maintenance

- New knowledge → a file in `Knowledge/` using `Templates/_TOPIC_TEMPLATE.md`. Unverified scraps → `Research/`.
- Every non-obvious claim needs a source URL. Undocumented/RE claims carry a `confidence` rating.
- On each Premiere release: re-verify touched docs, bump `last_verified` / `verified_against_version`,
  update `status`/`eol` where Adobe announces changes. Superseded docs → `Archive/`.
- The one test for any change: **does it make the KB more complete, accurate, and useful to an AI agent?**

## Provenance

Facts are sourced from official Adobe documentation (Scripting Guide, UXP docs, PrSDK/AE SDK guides),
Adobe Developer blog, the Adobe-CEP repositories, real open-source projects (Bolt CEP, pymiere,
AutoSubs, Premiere MCP servers), and community/reverse-engineering findings — each cited in the
relevant document's `Sources` section. Version-specific claims are stamped with the Premiere version
they were verified against.
