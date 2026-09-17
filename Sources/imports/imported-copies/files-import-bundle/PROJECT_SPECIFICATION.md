---
id: project-specification
title: Project Specification & Authoring Rules
category: meta
status: current
doc_status: complete
audience: ai-agent
spec_version: "2.0"
last_verified: "2026-06-28"
---

# Open Premiere Specification — Project Specification

> **This file is the single source of authority for how every other document in this
> repository is written, structured, and consumed.** It is written for AI agents first
> and human maintainers second. If a rule here conflicts with a habit, the rule wins.

---

## 1. Mission

Build the most complete, structured, continuously-expandable knowledge base on
**developing for Adobe Premiere Pro** (scripting, panels, native plugins, automation,
interop), optimized for **retrieval and consumption by AI coding agents**.

The goal is not to rewrite Adobe's docs. The goal is to **collect, verify, structure, and
preserve** existing knowledge — official docs, SDK, community findings, reverse
engineering, and battle-tested code — in one machine-readable corpus so an agent can:

- answer any Premiere-development question precisely and with sources,
- write production-grade code that is **version-aware** and **status-aware**,
- know what is supported, what is deprecated, and what is an undocumented hack,
- cross-link concepts (e.g. "Source Text JSON" ↔ "MOGRT import" ↔ "QE DOM fallback").

## 2. Non-Goals

- Do **not** invent APIs, behaviors, or version numbers. Unverified = marked `confidence: low` or omitted.
- Do **not** write essays. Collect facts, signatures, gotchas, and working code.
- Do **not** duplicate content. Each fact lives in exactly **one** authoritative file (see §6).
- Do **not** restructure the top-level directory layout (§4) once populated.

---

## 3. Core Principles

1. **One source of truth.** A fact appears in one file. Everything else cross-links to it.
2. **Status before syntax.** Every API is tagged with its lifecycle status. An agent must never
   recommend a deprecated/blocked API as if it were current.
3. **Version-aware always.** Premiere behavior changes between releases. Pin claims to versions.
4. **Verifiable.** Every non-obvious claim carries a source URL. Undocumented/RE claims carry a
   `confidence` rating and a discovery note.
5. **Production-grade examples only.** Code must be runnable, ES3-correct (for ExtendScript), and
   handle the documented failure modes. No toy snippets without practical value.
6. **Machine-readable.** YAML frontmatter (§5) on every Knowledge document, stable anchors,
   consistent kebab-case IDs.

---

## 4. Repository Layout (FINAL — do not change)

```
open-premiere-specification/
  README.md                  # Human/agent entry point: index, status matrix, usage guide
  PROJECT_SPECIFICATION.md   # This file: authoring rules + format
  Knowledge/                 # The corpus. One .md per authoritative topic.
  Templates/                 # _TOPIC_TEMPLATE.md and any reusable skeletons
  Examples/                  # Standalone runnable code samples referenced by Knowledge docs
  Research/                  # Raw findings, source dumps, unverified material pending promotion
  Archive/                   # Superseded docs kept for history (never deleted, never indexed as current)
```

**Rules:**
- New knowledge → a file in `Knowledge/`.
- Long runnable code that several docs reference → a file in `Examples/`, linked from Knowledge.
- Unverified scraps → `Research/` until promoted (verified, sourced, tagged) into `Knowledge/`.
- When a doc is superseded, move the old version to `Archive/` and set `superseded_by` in the new one.

---

## 5. YAML Frontmatter Schema (REQUIRED on every Knowledge doc)

Every file in `Knowledge/` begins with this frontmatter block. Fields marked `*` are required.

```yaml
---
id: extendscript-core                 # * kebab-case, unique, == filename without .md
title: ExtendScript Core              # * human title
category: scripting                   # * see §5.1 taxonomy
status: legacy                        # * technology lifecycle: see §5.2
stability: frozen                     # API churn: active | frozen | unstable | experimental
doc_status: complete                  # * authoring completeness: complete | partial | stub
introduced: "Adobe CC (pre-2015)"     # when this tech/API first appeared
deprecated: "API work frozen 2024"    # when deprecation began (or null)
eol: "2026-09"                        # end-of-life date if known (or null)
min_premiere_version: null            # earliest Premiere version required (e.g. "25.6"), or null
api_namespace: app                    # app | qe | premierepro | PrSDK | CSInterface | none
languages: [extendscript, javascript-es3]   # languages relevant to this doc
tags: [extendscript, es3, json2, jsx]        # * free-form retrieval tags
related: [cep, uxp, automation, debugging]   # * ids of related Knowledge docs (for cross-link graph)
supersedes: []                        # ids this doc replaces
superseded_by: [uxp]                  # ids that replace this (migration target), or []
sources:                              # * list of authoritative URLs
  - https://ppro-scripting.docsforadobe.dev/
confidence: high                      # high | medium | low — lower for undocumented/RE content
last_verified: "2026-06-28"           # * ISO date this doc's facts were last checked
verified_against_version: "25.x"      # * Premiere version(s) the claims were checked against
---
```

### 5.1 `category` taxonomy
- `scripting` — ExtendScript, UXP scripting, the scripting DOM
- `ui-extensibility` — CEP, UXP panels, panel architecture
- `native` — C++ PrSDK / AE SDK, native plugins, exporters/importers/filters
- `interop` — XML/FCPXML/OTIO, pymiere, MCP, BridgeTalk, external automation
- `data-format` — JSON blobs (Source Text), .epr presets, .mogrt internals
- `workflow` — markers, captions, export pipeline, import pipeline
- `meta` — this spec, README, templates, status matrix

### 5.2 `status` lifecycle values (the single most important field)
| Value | Meaning | Agent behavior |
|---|---|---|
| `current` | Actively supported, recommended for new work | Default recommendation |
| `legacy` | Still works, maintenance-only, being phased out | Use only for existing/compat targets; warn |
| `deprecated` | Officially deprecated and/or broken in modern versions | Do not recommend; name the replacement |
| `undocumented` | Works but unsupported, undocumented, may break anytime (e.g. QE DOM) | Last-resort only; flag risk explicitly |
| `mixed` | Doc spans technologies of different statuses | Read per-section status notes |

### 5.3 Status-discipline rule
When an agent uses this KB to write code, it MUST:
1. Resolve the target Premiere version (from the user, or ask).
2. Select APIs whose `status` + `min_premiere_version` fit that target.
3. If only a `deprecated`/`undocumented` path exists, say so, show the safest variant, and state the risk.

---

## 6. Topic ↔ File Mapping (resolving "one doc per topic" vs "no duplication")

The original brief enumerated 28 topics. Several of them are the **same conceptual unit** at the
API level (Tracks/TrackItems/ProjectItems/Bins are one DOM hierarchy; Export/Rendering/Media Encoder
are one pipeline; C++/Premiere SDK/Native Plugins are one native surface; Premiere DOM/Premiere API
overlap). Splitting those into separate files would force **content duplication**, violating Core
Principle #1.

**Resolution:** authoritative content is consolidated into the files below. The README index maps
**all 28 original topic names** to the correct file + anchor, so retrieval by any original name works.

| Original topic | Authoritative file |
|---|---|
| ExtendScript | `Knowledge/extendscript-core.md` |
| CEP | `Knowledge/cep.md` |
| UXP | `Knowledge/uxp.md` |
| C++ / Premiere SDK / Native Plugins / Plugins | `Knowledge/cpp-native-sdk.md` |
| Premiere DOM / Premiere API | `Knowledge/premiere-dom-overview.md` |
| Sequences / Tracks / TrackItems / Project Items / Bins | `Knowledge/sequences-tracks-trackitems.md` |
| Export / Rendering / Media Encoder | `Knowledge/export-rendering-media-encoder.md` |
| Import | `Knowledge/import.md` |
| XML / FCPXML | `Knowledge/xml-fcpxml.md` |
| Markers | `Knowledge/markers.md` |
| Captions | `Knowledge/captions.md` |
| Essential Graphics / Text / Fonts / MOGRT | `Knowledge/essential-graphics-mogrt-text.md` |
| Panels | `Knowledge/panels.md` |
| AI Integration | `Knowledge/ai-integration.md` |
| Automation | `Knowledge/automation.md` |
| Debugging | `Knowledge/debugging.md` |
| Reverse Engineering | `Knowledge/reverse-engineering-qe-dom.md` |
| Best Practices | `Knowledge/best-practices.md` |
| Examples | `Examples/` + `Knowledge/examples-index.md` |
| (cross-cutting) Technology status | `Knowledge/00-technology-status-matrix.md` |

> If strict one-file-per-topic is later required, split is mechanical: promote each anchor to its own
> file and replace it with a pointer. Reversible by design.

---

## 7. Document Body Structure

Every Knowledge doc follows the section order in `Templates/_TOPIC_TEMPLATE.md`:

1. **TL;DR** — 2–5 bullets: what this is, current status, the one thing to get right.
2. **Status & Lifecycle** — version-pinned: introduced / deprecated / eol / replacement.
3. **Architecture** — how it fits in the stack, what talks to what.
4. **API Surface** — signatures, objects, properties. Tables for enums/constants.
5. **Working Examples** — production-ready code (ES3-correct where applicable).
6. **Limitations** — what it cannot do; documented hard walls.
7. **Common Errors & Gotchas** — symptom → cause → fix. Version-pinned bugs.
8. **Workarounds** — for limitations/bugs, with risk notes.
9. **Migration** — path to the `superseded_by` technology, with parity gaps.
10. **Cross-References** — links to `related` docs and Examples.
11. **Sources** — all URLs backing this doc.

Sections may be omitted if genuinely N/A, but keep the order. Use stable `##`/`###` headings so
anchors are predictable (`#api-surface`, `#common-errors--gotchas`, etc.).

---

## 8. Code Rules

- **ExtendScript = ES3.** No `let`/`const`, arrow functions, template literals, `Promise`, default
  params, or native `JSON`. Bundle/assume **json2.js**. Mark any ES5+ snippet explicitly as UXP/Node.
- **UXP = async.** DOM methods return Promises — show `await`. Wrap mutations in `executeTransaction`.
- **Always validate** active project / sequence / track / clip / component / property before use.
- **Version-gate** behavior that differs across releases (color 0–255 vs 0–1, Time object vs number,
  the HEVC block at 25.5, the Source-Text caching bug regressions).
- **UTF-8** for all `.jsx` (Cyrillic safety). Note encoding where it matters.
- Label every code block's runtime in a comment header, e.g. `// ExtendScript (ES3) — Premiere 14.1+`.

## 9. Sourcing & Confidence Rules

- Prefer: official Adobe docs → SDK → real open-source projects → community (forum/SO/blog) → RE findings.
- Every undocumented/QE/RE claim: `confidence: low|medium`, plus an inline note on how it was discovered
  and which versions it was observed on.
- Conflicting sources: present both, mark the more authoritative, don't silently pick.
- Never fabricate a source. If unverified, it goes to `Research/`, not `Knowledge/`.

## 10. Maintenance Lifecycle

- On every new Premiere release: re-check docs touching changed areas, bump `last_verified` and
  `verified_against_version`, update `status`/`eol` where Adobe announces changes.
- Promote `Research/` → `Knowledge/` only after verification + sourcing + frontmatter.
- Superseded docs → `Archive/`, with `superseded_by` set on the replacement. Never hard-delete history.

## 11. Definition of Done (per doc)

A Knowledge doc is `doc_status: complete` when it has: valid frontmatter, all applicable body
sections, ≥1 production-ready example (or an explicit "no API exists" statement), version-pinned
limitations and gotchas, a migration note if `superseded_by` is set, and sources for every non-obvious claim.

## 12. The One Question

Before adding or changing anything, ask:
**"Does this make the knowledge base more complete, accurate, and useful to an AI agent?"**
If no, it does not go in.
