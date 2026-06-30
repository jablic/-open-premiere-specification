---
id: xml-fcpxml
title: XML & FCP7 XML Export Format
category: interop
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CS6"
min_premiere_version: null
api_namespace: null
languages: [xml, python, javascript]
tags: [xml, fcp7, interchange, interop, parsing]
related: [export-rendering-media-encoder, automation]
sources: [
  "FCP7 XML specification (legacy but stable)",
  "Production testing: Premiere 25.x",
  "Community tools (fcpxml-parser, etc.)"
]
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# XML & FCP7 XML Export Format

## TL;DR

**FCP7 XML = interchange format for Premiere ↔ Final Cut Pro 7.** Export timeline as XML, edit in other tools, re-import. **Format:** XML tree with sequences, clips, markers, timing. **Ticks = 254,016,000,000/second.** **Parsing:** Use standard XML libs (Python `xml.etree`, JavaScript DOM). **Limited:** No effects, color grading, or complex metadata preserved.

**Critical traps:**
- Ticks must be converted to timecode (frame-rate dependent)
- Marker data embedded as Base64-encoded blobs
- Clips have absolute paths (may break on different systems)
- No effect data (effects lost on re-import)

---

## FCP7 XML Structure

### Root Element: `xmeml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xmeml version="5">
  <project>
    <name>My Project</name>
    <sequence>
      <name>Timeline 1</name>
      <timebase>30</timebase>
      <ntsc>true</ntsc>
      <duration>3600</duration>
      
      <media>
        <video>
          <track>
            <clipitem>
              <name>Clip 1</name>
              <duration>1500</duration>
              <in>0</in>
              <out>1500</out>
              ...
            </clipitem>
          </track>
        </video>
        <audio>
          ...
        </audio>
      </media>
      
      <marker>
        <name>Scene A</name>
        <in>450</in>
        <out>450</out>
        <comment>Custom data here</comment>
      </marker>
    </sequence>
  </project>
</xmeml>
```

---

## Duration & Timecode Conversion

### Ticks to Timecode

**Ticks = 254,016,000,000 ticks/second** (Premiere internal).

FCP7 XML uses **frame-relative timing** (depends on frame rate).

```python
TICKS_PER_SECOND = 254016000000

def ticks_to_seconds(ticks):
    return ticks / TICKS_PER_SECOND

def seconds_to_timecode(seconds, fps):
    frames = int(seconds * fps)
    hours = frames // (fps * 3600)
    minutes = (frames % (fps * 3600)) // (fps * 60)
    secs = (frames % (fps * 60)) // fps
    frame = frames % fps
    return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frame:02d}"

ticks = 762048000000
seconds = ticks_to_seconds(ticks)
timecode = seconds_to_timecode(seconds, fps=30)
print(timecode)
```

---

## Marker Data & Base64

Markers often contain Base64-encoded custom data:

```xml
<marker>
  <name>Important</name>
  <in>1500</in>
  <comment>eyJkYXRhIjogImN1c3RvbSJ9</comment>
</marker>
```

Decode with:

```python
import base64
import json

encoded = "eyJkYXRhIjogImN1c3RvbSJ9"
decoded = base64.b64decode(encoded).decode('utf-8')
data = json.loads(decoded)
print(data)
```

---

## Parsing FCP7 XML (Python)

```python
import xml.etree.ElementTree as ET
import base64

def parse_fcp7_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    sequences = []
    for seq in root.findall('.//sequence'):
        seq_data = {
            'name': seq.findtext('name', 'Untitled'),
            'timebase': int(seq.findtext('timebase', '30')),
            'clips': [],
            'markers': []
        }
        
        for clipitem in seq.findall('.//clipitem'):
            clip = {
                'name': clipitem.findtext('name'),
                'duration': int(clipitem.findtext('duration', '0')),
                'in': int(clipitem.findtext('in', '0')),
                'out': int(clipitem.findtext('out', '0'))
            }
            seq_data['clips'].append(clip)
        
        for marker in seq.findall('.//marker'):
            marker_data = {
                'name': marker.findtext('name'),
                'in': int(marker.findtext('in', '0')),
                'comment': marker.findtext('comment', '')
            }
            try:
                decoded = base64.b64decode(marker_data['comment']).decode('utf-8')
                marker_data['data'] = decoded
            except:
                pass
            seq_data['markers'].append(marker_data)
        
        sequences.append(seq_data)
    
    return sequences

result = parse_fcp7_xml('export.xml')
for seq in result:
    print(f"Sequence: {seq['name']}")
    print(f"  Clips: {len(seq['clips'])}")
    print(f"  Markers: {len(seq['markers'])}")
```

---

## Limitations

| Feature | Supported | Notes |
|---|---|---|
| Clips & timing | ✅ | Yes, with ticks |
| Markers | ✅ | Yes, can embed data |
| Audio tracks | ✅ | Yes |
| Speed/duration | ✅ | Yes |
| Effects | ❌ | Not preserved |
| Color grading | ❌ | Not preserved |
| Keyframes | ❌ | Not preserved |
| Nested sequences | ⚠️ | Limited support |

---

## Export from Premiere

```javascript
var proj = app.project;
var seq = proj.activeSequence;

var exportPath = "/tmp/export.xml";
var xmemlDoc = seq.exportAsXML();
```

**Note:** Full API limited in ExtendScript. Use CEP panel for GUI export.

---

## Re-import into Premiere

1. Export XML from timeline
2. Edit XML externally
3. File → Import → XML
4. Premiere reconstructs clips + timing
5. **Effects lost** (must re-apply)

---

## Sources

- FCP7 XML spec (archived): https://support.apple.com/en-us/HT201685
- Community parser: https://github.com/num3ric/python-fcpxml
