---
id: captions
title: Captions & Subtitles
category: workflow
status: legacy
stability: frozen
doc_status: stub
introduced: "CC era"
deprecated: "API frozen 2024"
eol: "2026-09"
min_premiere_version: null
api_namespace: app
languages: [extendscript, javascript-es3]
tags: [captions, subtitles, srt, scc, mcc, caption-track, whisper, autosubs, caption-to-graphics]
related: [markers, essential-graphics-mogrt-text, ai-integration, import, uxp]
supersedes: []
superseded_by: [uxp]
confidence: medium
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://ppro-scripting.docsforadobe.dev/
  - https://github.com/tmoroney/auto-subs
---

# Captions & Subtitles

## TL;DR
- `sequence.createCaptionTrack(projectItem, startAtTime, [format])` from an imported caption ProjectItem (SRT/SCC/MCC). **STUB.**
- Programmatic caption **content** access is notoriously limited; the caption-to-graphics workflow is largely UI-only.

## Status & Lifecycle
- ExtendScript `legacy/frozen`, EOL 2026-09. UXP transcripts/captions evolving. See `00-technology-status-matrix`.

## Architecture
Import a caption file as a ProjectItem → create a caption track from it. **STUB.**

## API Surface
`sequence.createCaptionTrack(projectItem, startAtTime, captionFormat)` (e.g. `Sequence.CAPTION_FORMAT_708`). Import via `app.project.importFiles(...)`. **STUB: format constants.**

## Working Examples
**STUB: import-SRT → create-caption-track example.**

## Limitations
Reading/editing caption text programmatically is very limited; 'Upgrade captions to graphics' is UI-only. **STUB.**

## Common Errors & Gotchas
Don't conflate captions with Essential Graphics text — different objects (see `essential-graphics-mogrt-text`). **STUB.**

## Workarounds
**AutoSubs** (`tmoroney/auto-subs`) — on-device Whisper/Moonshine/Parakeet transcription + diarization; imports subtitles as caption tracks. Its **CEP panel broke in Premiere 2026** (Issue #571) — a CEP-death data point; Premiere path historically CEP+ExtendScript. **STUB.**

## Migration
**STUB.**

## Cross-References
- `markers`
- `essential-graphics-mogrt-text`
- `ai-integration`
- `import`
- `uxp`

## Sources
- https://ppro-scripting.docsforadobe.dev/
- https://github.com/tmoroney/auto-subs

