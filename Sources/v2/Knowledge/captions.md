---
id: captions
title: Captions & Subtitles
category: workflow
status: legacy
stability: frozen
doc_status: complete
introduced: "CC era; Auto-captions ~2020+"
deprecated: "API frozen 2024"
eol: "2026-09"
min_premiere_version: null
api_namespace: app
languages: [extendscript, javascript-es3, javascript, python]
tags: [captions, subtitles, srt, scc, mcc, caption-track, whisper, autosubs, caption-to-graphics, 608, 708]
related: [markers, essential-graphics-mogrt-text, ai-integration, import, uxp]
supersedes: []
superseded_by: [uxp]
sources:
  - https://ppro-scripting.docsforadobe.dev/
  - https://github.com/tmoroney/auto-subs
  - https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
confidence: medium
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
---

# Captions & Subtitles

> Caption tracks, SRT/SCC/MCC import, and the limits of programmatic caption editing.
> **Caption text is serialized data, not plain strings** — preserve unknown JSON/XML fields on round-trip.

## TL;DR
- Workflow: **import caption file** (SRT/SCC/MCC) as `ProjectItem` → **`sequence.createCaptionTrack(projectItem, startTime, format)`**.
- **Reading/editing caption text programmatically is severely limited** in ExtendScript — most caption content APIs are UI-only or undocumented.
- **Do not confuse captions with MOGRT/Essential Graphics text** — different objects, different pipelines (`essential-graphics-mogrt-text`).
- **AutoSubs** (Whisper/Moonshine) generates captions via CEP+ExtendScript; **CEP panel broke in Premiere 2026** (Issue #571).
- UXP adds **transcript/caption** APIs (evolving in 25.6+) — check `@adobe/premierepro` for current surface.

## Status & Lifecycle
- ExtendScript caption track creation is **legacy/frozen**, EOL **2026-09**.
- UXP caption/transcript APIs are **current** but still maturing (25.6+).
- "Upgrade captions to graphics" is **UI-only** — not scriptable.

## Architecture
```
SRT/SCC/MCC file
  └─ app.project.importFiles → ProjectItem (caption sidecar)
       └─ sequence.createCaptionTrack(projectItem, startAtTime, captionFormat)
            └─ Caption track on timeline (separate from video/audio tracks)
```

Captions are **not** `TrackItem` clips in the video sense — they live on dedicated caption tracks.

## API Surface

### `sequence.createCaptionTrack(projectItem, startAtTime, captionFormat)`

| Param | Type | Notes |
|---|---|---|
| `projectItem` | `ProjectItem` | Imported caption file |
| `startAtTime` | `Time` | Where caption track begins on timeline |
| `captionFormat` | constant | e.g. `Sequence.CAPTION_FORMAT_708` |

### Caption format constants (ExtendScript)

| Constant | Format |
|---|---|
| `Sequence.CAPTION_FORMAT_608` | CEA-608 |
| `Sequence.CAPTION_FORMAT_708` | CEA-708 |
| `Sequence.CAPTION_FORMAT_TELETEXT` | Teletext (region-dependent) |
| `Sequence.CAPTION_FORMAT_SUBTITLE` | Subtitle |
| `Sequence.CAPTION_FORMAT_OPEN_EBU` | EBU |

### Import caption files

Use `app.project.importFiles([srtPath], true, null, false)` — Premiere recognizes `.srt`, `.scc`, `.mcc`, `.stl`, `.xml` (caption XML).

## Working Examples

```js
// ExtendScript (ES3) — import SRT and create caption track
function addCaptionTrackFromSrt(srtPath, seq) {
  if (!seq) { seq = app.project.activeSequence; }
  if (!seq) { return { ok: false, error: 'No active sequence' }; }

  var imported = app.project.importFiles([srtPath], true, null, false);
  if (!imported) { return { ok: false, error: 'Import failed' }; }

  var item = app.project.rootItem.findItemsMatchingMediaPath(srtPath, true);
  if (!item) { return { ok: false, error: 'Caption ProjectItem not found' }; }

  var start = seq.zeroPoint; // or new Time(0, seq.timebase)
  var track = seq.createCaptionTrack(item, start, Sequence.CAPTION_FORMAT_708);
  return { ok: true, trackCreated: !!track };
}
```

```js
// ExtendScript (ES3) — list caption tracks (via sequence structure)
function countCaptionTracks(seq) {
  // Caption tracks are accessed separately from videoTracks/audioTracks
  // Use sequence.getCaptionTrackCount() if available on your build
  var n = 0;
  try {
    if (typeof seq.getCaptionTrackCount === 'function') {
      n = seq.getCaptionTrackCount();
    }
  } catch (e) { n = -1; }
  return n;
}
```

## Limitations
- **No reliable ExtendScript API to read/write individual caption text blocks** on the timeline.
- Caption internal representation uses **serialized JSON/XML** — naive string replacement breaks styling/timing.
- "Create captions from markers" and "Upgrade captions to graphics" are **UI workflows only**.
- Auto-transcription (Speech to Text) is a **host feature**, not exposed as a stable scripting API.
- CEA-608/708 broadcast compliance requires format-specific rules — test on target deliverable.

## Common Errors & Gotchas
- **Symptom:** Caption track empty after import. **Cause:** Wrong `captionFormat` constant for file type. **Fix:** Match SRT → `CAPTION_FORMAT_SUBTITLE` or 708 as appropriate.
- **Symptom:** Timing drift. **Cause:** `startAtTime` offset wrong vs sequence start. **Fix:** Use `seq.zeroPoint` or explicit `Time` aligned to sequence timebase.
- **Symptom:** AI suggests `sequence.captions[i].text = "..."`. **Cause:** Hallucinated API. **Fix:** This method does not exist — see Agent Rules in `best-practices`.
- **Symptom:** Confused MOGRT text with captions. **Cause:** Both appear as text on screen. **Fix:** MOGRT = Essential Graphics (`essential-graphics-mogrt-text`); captions = caption track.

## Workarounds
- **AutoSubs** (`github.com/tmoroney/auto-subs`) — on-device Whisper transcription → caption track. Requires CEP; broken in Premiere 2026 — monitor project for UXP port.
- **External pipeline:** Generate SRT in Python → import via `importFiles` + `createCaptionTrack`.
- **MCP servers** wrap caption workflows as agent tools (`ai-integration`) — verify actual tool implementations against source.
- Parse exported XML for caption data if live API insufficient (`xml-fcpxml`).

## Migration
- UXP 25.6+ adds `CaptionTrack`, transcript APIs — check `developer.adobe.com/premiere-pro/uxp/ppro-reference/`.
- Preserve unknown caption serialization fields on any transform (PKC rule RULE-CAP-0002).

## Cross-References
- `markers` — chapter markers → caption UI workflow
- `essential-graphics-mogrt-text` — NOT captions
- `ai-integration` — Whisper, MCP, AutoSubs
- `import` — SRT import path
- `uxp` — evolving caption/transcript API

## Sources
- https://ppro-scripting.docsforadobe.dev/
- https://github.com/tmoroney/auto-subs
- https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
