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
confidence: medium
last_verified: "2026-06-30"
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
