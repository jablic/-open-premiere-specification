---
id: captions
title: Captions & Subtitles
category: workflow
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro 2020"
min_premiere_version: "20.0"
api_namespace: app
languages: [extendscript, uxp, python]
tags: [captions, subtitles, accessibility, cea-608, srt, batch-operations, automation]
related: [export-rendering-media-encoder, automation, batch-effects-captions]
sources: [
  "Adobe Captions documentation",
  "Production workflows (Premiere 25.x)",
  "Examples/uxp/batch-effects-captions.jsx"
]
confidence: high
last_verified: "2026-07-01"
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

## Caption Track Architecture

### Timeline Structure (ExtendScript)

```javascript
var seq = app.project.activeSequence;

// Check if caption track exists
if (seq.captionTracks && seq.captionTracks.length > 0) {
  var captionTrack = seq.captionTracks[0];
  
  for (var i = 0; i < captionTrack.captions.length; i++) {
    var caption = captionTrack.captions[i];
    var startTime = caption.startTime;  // ticks
    var endTime = caption.endTime;      // ticks
    var text = caption.text;
  }
}
```

**Key Properties:**
- `sequence.captionTracks[]` - array of caption tracks
- `captionTrack.captions[]` - array of caption objects
- `caption.startTime` - start in ticks (1/254016000 second)
- `caption.endTime` - end in ticks
- `caption.text` - caption text string
- `caption.metadata` - custom caption metadata (if applicable)

---

## Read Captions (ExtendScript)

### Batch Read from Timeline

```javascript
function readCaptions(sequence) {
  if (!sequence || !sequence.captionTracks || sequence.captionTracks.length === 0) {
    return [];
  }
  
  var allCaptions = [];
  var captionTrack = sequence.captionTracks[0];
  
  for (var i = 0; i < captionTrack.captions.length; i++) {
    var caption = captionTrack.captions[i];
    allCaptions.push({
      index: i,
      startTime: caption.startTime,
      endTime: caption.endTime,
      duration: caption.endTime - caption.startTime,
      text: caption.text,
      timestamp: formatTicks(caption.startTime)
    });
  }
  
  return allCaptions;
}

function formatTicks(ticks) {
  var seconds = ticks / 254016000;
  var hours = Math.floor(seconds / 3600);
  var mins = Math.floor((seconds % 3600) / 60);
  var secs = Math.floor(seconds % 60);
  var ms = Math.floor((seconds % 1) * 1000);
  
  return pad(hours) + ":" + pad(mins) + ":" + pad(secs) + "," + padMs(ms);
}

function pad(n) {
  return (n < 10 ? "0" : "") + n;
}

function padMs(n) {
  return (n < 100 ? (n < 10 ? "00" : "0") : "") + n;
}
```

---

## Create Captions (ExtendScript)

### Batch Create from JSON

```javascript
function batchCreateCaptions(sequence, captionSpecs) {
  if (!sequence || !sequence.captionTracks || sequence.captionTracks.length === 0) {
    return { success: false, error: "No caption track in sequence" };
  }
  
  var captionTrack = sequence.captionTracks[0];
  var created = [];
  var errors = [];
  
  for (var i = 0; i < captionSpecs.length; i++) {
    var spec = captionSpecs[i];
    
    try {
      // Convert seconds to ticks
      var startTicks = Math.round(spec.start_sec * 254016000);
      var endTicks = Math.round(spec.end_sec * 254016000);
      
      // Create caption object (API varies by Premiere version)
      var caption = captionTrack.createCaption(startTicks, endTicks);
      caption.text = spec.text || "";
      
      created.push({
        text: spec.text,
        startTime: startTicks,
        endTime: endTicks
      });
    } catch (e) {
      errors.push({
        text: spec.text,
        error: e.toString()
      });
    }
  }
  
  return {
    success: errors.length === 0,
    created: created.length,
    errors: errors
  };
}

// Usage:
var captions = [
  { start_sec: 0, end_sec: 2, text: "Speaker: Hello, world!" },
  { start_sec: 2, end_sec: 4, text: "Speaker: This is a caption." },
  { start_sec: 4, end_sec: 6, text: "[MUSIC PLAYING]" }
];

var result = batchCreateCaptions(app.project.activeSequence, captions);
alert("Created: " + result.created + " captions, Errors: " + result.errors.length);
```

**Version Note:** Caption API availability varies significantly across Premiere versions. Test with target version before deployment.

---

## Create Caption (Premiere UI)

Manual creation: Sequence → Sequence Settings → Captions → Enable → Click timeline to add.

---

## Export Captions

### Via Media Encoder

```bash
File → Export → Media
Choose codec: include captions option
Select format: SRT, VTT, or CEA-608
```

### ExtendScript Caption Export

```javascript
function exportCaptionsToSRT(sequence, outputPath) {
  if (!sequence || !sequence.captionTracks || sequence.captionTracks.length === 0) {
    return { success: false, error: "No captions in sequence" };
  }
  
  var captionTrack = sequence.captionTracks[0];
  var srtContent = "";
  
  for (var i = 0; i < captionTrack.captions.length; i++) {
    var caption = captionTrack.captions[i];
    var index = i + 1;
    var start = formatSRTTime(caption.startTime);
    var end = formatSRTTime(caption.endTime);
    
    srtContent += index + "\n";
    srtContent += start + " --> " + end + "\n";
    srtContent += caption.text + "\n";
    srtContent += "\n";
  }
  
  try {
    var file = new File(outputPath);
    file.open("w");
    file.write(srtContent);
    file.close();
    
    return { success: true, captions: captionTrack.captions.length, path: outputPath };
  } catch (e) {
    return { success: false, error: e.toString() };
  }
}

function formatSRTTime(ticks) {
  var seconds = ticks / 254016000;
  var hours = Math.floor(seconds / 3600);
  var mins = Math.floor((seconds % 3600) / 60);
  var secs = Math.floor(seconds % 60);
  var ms = Math.floor((seconds % 1) * 1000);
  
  return pad(hours) + ":" + pad(mins) + ":" + pad(secs) + "," + padMs(ms);
}

function pad(n) { return (n < 10 ? "0" : "") + n; }
function padMs(n) { return (n < 100 ? (n < 10 ? "00" : "0") : "") + n; }
```

### UXP Caption Support (Emerging, 25.6+)

Caption API in UXP is limited. Recommended approach: use ExtendScript via async bridge.

```javascript
const { application } = require("premierepro");

(async () => {
  try {
    const proj = await application.activeProject;
    const seq = await proj.activeSequence;
    
    if (!seq || !seq.captionTracks) {
      console.log("No captions in sequence");
      return;
    }
    
    const captionTrack = await seq.captionTracks[0];
    const captions = await captionTrack.captions;
    
    for (let i = 0; i < captions.length; i++) {
      const caption = await captions[i];
      const text = await caption.text;
      console.log(`Caption ${i}: ${text}`);
    }
  } catch (e) {
    console.error("Error:", e.toString());
  }
})();
```

---

## Format Conversion & Import

### Parse & Import SRT

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
