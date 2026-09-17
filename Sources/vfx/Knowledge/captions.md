---
id: captions
title: Captions & Subtitles
category: workflow
status: current
stability: active
doc_status: partial
introduced: "Premiere Pro 2020"
min_premiere_version: "20.0"
api_namespace: app
languages: [extendscript, uxp]
tags: [captions, subtitles, accessibility, cea-608, srt]
related: [export-rendering-media-encoder, automation]
sources: [
  "Adobe Captions documentation",
  "Production workflows (Premiere 25.x)"
]
confidence: high
last_verified: "2026-07-14"
verified_against_version: "25.6"
---

# Captions & Subtitles

## TL;DR

**Captions = text overlays for dialogue/audio description (accessibility).** Premiere 2020+ native support. **Formats:** CEA-608 (legacy, TV), SRT (standard), VTT (web). **Automation:** Limited via ExtendScript; UXP emerging support (25.6+). **Gotcha:** Caption data stored per-sequence; export requires format selection.

---

## Caption Formats

| Format | Use Case | CEA-608 | SRT | VTT |
|---|---|---|---|---|
| **Legacy TV** | Closed captions (legacy) | ✅ | ❌ | ❌ |
| **Standard (SRT)** | Web, streaming | ❌ | ✅ | ❌ |
| **Web (VTT)** | HTML5 video | ❌ | ❌ | ✅ |

---

## Create Caption (Premiere UI)

1. Sequence → Sequence Settings → Captions
2. Enable caption track
3. Click in timeline to add caption
4. Type text, set duration

**API:** Limited automation; recommend UI for now.

---

## Automation Reality (Confirmed 2026-07, Production Testing)

**There is no write API for a live Captions track at all — confirmed independently three ways:** the DOM scripting guide, this doc's earlier "Limited via ExtendScript" note, and directly from Adobe on the community forum (Bruce Bullis, "Adobe Legend"): *"There is no API access to caption tracks [for writing]... won't be available until PPro moves to UXP-based extensibility; no dates available."* Do not spend time hunting for a per-entry write method — it does not exist as of Premiere 25.6/26.x.

**Read is possible** (DOM `getCaptionTrackCount()`/`getCaptionTrack(i)` → `.getTrackItems()`/`.trackItems`/`.clips`, with a QE fallback via `qe.project.getActiveSequence().getCaptionTrackAt(i)` if DOM comes back empty — see `reverse-engineering-qe-dom.md`).

**Write is only possible via full-track replacement, not per-entry edit:**
```javascript
// Sequence.createCaptionTrack(projectItem, startAtTime, [captionFormat])
// startAtTime is a TIME value (usually 0), NOT a track index — there is no
// parameter to target/replace an existing track.
var created = seq.createCaptionTrack(srtItem, 0, Sequence.CAPTION_FORMAT_SUBTITLE);
// or Sequence.CAPTION_FORMAT_708, or the 2-arg form on older builds.
```
Workflow: build a corrected `.srt` in code → `app.project.importFiles([path], 1, bin, 0)` → locate the resulting `ProjectItem` (poll briefly; import is async) → `seq.createCaptionTrack(item, 0, format)`.

**Critical gotchas, all verified in production:**
- **`createCaptionTrack()` only ADDS a track — confirmed against the official docs, no `removeCaptionTrack()`/replace variant exists in the documented DOM.** If a caption track already exists, the result is TWO overlapping tracks, not a replacement. See `reverse-engineering-qe-dom.md`'s "Discovering Available QE Methods" section for an undocumented, unverified QE escape hatch (`removeVideoTrack`/`removeAudioTrack` confirmed to exist by naming symmetry; a `removeCaptionTrack`-shaped method is plausible but must be checked via `qe.reflect.methods` before relying on it, and its success verified by re-reading the track count afterward, not trusted from a return value).
- **Premiere parses an imported `.srt`'s content ONCE, at import time** — it does not notice the file changing on disk afterward. Re-running an import against the SAME file path silently reuses the stale first-ever-imported content. Always import a uniquely-named temp copy (e.g. append a timestamp) if the workflow might run more than once against evolving content.
- **A +1 frame timing nudge is needed** when round-tripping through `createCaptionTrack()` specifically (not needed for a plain `.srt` export) — empirically, captions built this way land 1 frame early without it.
- **Range-limited caption editing has a structural ceiling:** since only whole-track add is possible, "edit just the captions in this TC range" can only be approximated as "add a new track containing just the corrected range" (old track's matching entries remain underneath, need manual removal) OR "add a new track containing everything, with just the range's text corrected" (only safe if the old track was actually removed first — otherwise this duplicates every untouched entry). Neither is a true partial in-place edit.

---

## Export Captions

### Via Media Encoder

```bash
File → Export → Media
Choose codec: include captions option
Select format: SRT, VTT, or CEA-608
```

### ExtendScript (Limited)

```javascript
var seq = app.project.activeSequence;
var outputPath = "/tmp/captions.srt";

app.encoder.encodeFile(seq, 
  app.encoder.getExportPresets()[0], 
  outputPath, true, true);
```

---

## Parse SRT Captions (External)

```python
import re

def parse_srt(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    blocks = content.split('\n\n')
    captions = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            caption = {
                'index': lines[0],
                'timecode': lines[1],
                'text': '\n'.join(lines[2:])
            }
            captions.append(caption)
    
    return captions

captions = parse_srt('captions.srt')
for cap in captions:
    print(cap)
```

---

## Accessibility Best Practices

- Caption all dialogue
- Include speaker names
- Describe important audio cues [SOUND EFFECT]
- Use clear, readable fonts
- Sufficient contrast (white on black preferred)

---

## Sources

- Adobe Captions: https://support.adobe.com/en-us/HT208197
