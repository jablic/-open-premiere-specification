---
id: xml-fcpxml
title: XML, FCPXML & FCP7 XML (xmeml)
category: interop
status: current
stability: active
doc_status: complete
introduced: "Long-standing interchange"
deprecated: null
eol: null
min_premiere_version: null
api_namespace: none
languages: [python, xml, extendscript, javascript]
tags: [fcpxml, fcp7-xml, xmeml, otio, markers, base64, essential-graphics, timecode, parsing, lxml, elementtree]
related: [markers, essential-graphics-mogrt-text, sequences-tracks-trackitems, automation, import, uxp]
supersedes: []
superseded_by: []
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://fcp.cafe/developer-case-studies/fcpxml/
  - https://community.adobe.com/t5/premiere-pro-discussions/reading-graphics-text-base64-string-from-premiere-xml-file/m-p/14231060
  - https://opentimelineio.readthedocs.io/
  - https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
---

# XML, FCPXML & FCP7 XML (xmeml)

> Premiere imports and exports legacy **FCP7 XML (xmeml)** and **FCPXML** for interchange with
> Final Cut Pro, DaVinci Resolve, and custom pipelines. **Premiere 25.6+** adds **OTIO**
> import/export via UXP `ProjectConverter`. XML is a useful **read-back channel** for state the live
> API won't expose — but it is **lossy** on round-trip, especially for Essential Graphics text.

## TL;DR
- Export active sequence: **`sequence.exportAsFinalCutProXML(path)`** (ExtendScript) or UXP **`exportAsFinalCutProXML`** (async).
- Import: **`sequence.importAsFinalCutProXML(path)`** (ExtendScript) or UXP **`ProjectConverter`** (25.6+).
- **Markers** are straightforward — `<marker>` elements with `<name>`, `<comment>`, `<in>`, `<out>` in **frames**.
- **Essential Graphics / title text** is hard — nested `<filter>/<effect>`, often **Base64-encoded** in `<data>` nodes; frequently **unrecoverable** once flattened.
- **Media paths:** resolve `<file id="…">` → `<pathurl>` (`file://localhost/...`); later `<clipitem>` nodes reference by `id` only.
- **OTIO** (25.6+): modern interchange; prefer for new pipelines when UXP is available.
- Runnable parser: `Examples/python/parse_premiere_fcpxml.py`.

## Status & Lifecycle
- **FCP7 XML / FCPXML:** `current` — long-standing interchange; no EOL announced. Behavior varies by Premiere version and export options.
- **OTIO:** `current`, introduced **Premiere 25.6** (Dec 2025) via UXP `ProjectConverter`. Preferred for new cross-app pipelines where supported.
- **ExtendScript export/import:** `legacy`, EOL **2026-09** — still works today; plan UXP migration.
- XML is **not** a full project serialization format — treat it as a controlled interchange layer, not source of truth (`Archive/pkc-legacy/spec_src/serialization/SER-0001-premiere-xml.yaml`).

## Architecture

### Format landscape
```
                    ┌─────────────────────────────────────┐
  Premiere sequence │  exportAsFinalCutProXML(path)        │
                    └──────────────┬──────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
        FCP7 XML (xmeml)     FCPXML (1.x DTD)      OTIO (.otio)  ← 25.6+ UXP only
              │                    │                    │
              └─────────── parse / transform ──────────┘
                          Python / OTIO / Resolve / FCP
```

Premiere's **`exportAsFinalCutProXML`** produces **FCP7-compatible xmeml** (not Apple FCPX `.fcpxml` — the name is historical). Third-party tools and OpenTimelineIO's `fcp_xml` adapter consume this dialect.

### FCP7 xmeml document tree (annotated)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<xmeml version="4">                          <!-- root; version attribute varies -->
  <sequence id="sequence-1">                  <!-- one sequence per export (typical) -->
    <name>My Sequence</name>
    <duration>3600</duration>                 <!-- frames -->
    <rate>
      <timebase>25</timebase>                 <!-- fps (integer) -->
      <ntsc>FALSE</ntsc>                      <!-- TRUE → 23.976 / 29.97 drop patterns -->
    </rate>
    <timecode>
      <rate>...</rate>
      <string>00:00:00:00</string>
      <frame>0</frame>
    </timecode>
    <media>
      <video>
        <format>...</format>
        <track TL.SQTrackTargeting="1">       <!-- targeting attrs appear on some exports -->
          <clipitem id="clipitem-1">
            <name>interview.mov</name>
            <duration>900</duration>
            <rate><timebase>25</timebase><ntsc>FALSE</ntsc></rate>
            <start>0</start>                  <!-- timeline in-point (frames) -->
            <end>900</end>                    <!-- timeline out-point (frames) -->
            <in>100</in>                      <!-- source media in (frames) -->
            <out>1000</out>                   <!-- source media out (frames) -->
            <file id="file-1">                <!-- master file definition -->
              <name>interview.mov</name>
              <pathurl>file://localhost/Volumes/Media/interview.mov</pathurl>
              <rate>...</rate>
              <timecode>...</timecode>
            </file>
            <filter>                          <!-- effects stack -->
              <effect>
                <name>AE.ADBE Text</name>     <!-- or DisplayName / effectid -->
                <effectid>AE.ADBE Text</effectid>
                <effectcategory>graphic</effectcategory>
                <effecttype>filter</effecttype>
                <mediatype>video</mediatype>
                <parameter>...</parameter>
                <data>BASE64_PAYLOAD_HERE</data>  <!-- Essential Graphics blob -->
              </effect>
            </filter>
            <marker>                          <!-- clip-level marker -->
              <name>Fix audio</name>
              <comment>noise at cut</comment>
              <in>450</in>
              <out>-1</out>                   <!-- -1 = point marker -->
            </marker>
          </clipitem>
          <generatoritem>                     <!-- titles, color mattes, MOGRT-like generators -->
            ...
          </generatoritem>
        </track>
      </video>
      <audio>
        <track>
          <clipitem>...</clipitem>
        </track>
      </audio>
    </media>
    <marker>                                  <!-- sequence-level marker -->
      <name>Act 1</name>
      <in>0</in>
      <out>900</out>
    </marker>
  </sequence>
</xmeml>
```

**Key structural rules:**
- Time positions in xmeml are predominantly **integer frame counts**, not seconds or ticks.
- `<clipitem>` on the timeline references media via nested `<file id="…">` or `<file id="file-1"/>` (reference-only).
- `<generatoritem>` holds synthetic media (titles, adjustment layers rendered as generators).
- `<filter>` / `<effect>` stacks mirror Premiere's effect components; Essential Graphics appear here with `graphic` category and AE matchNames.
- Sequence settings (raster, pixel aspect) live under `<sequence><media><video><format>` and `<sequence>` attributes depending on export version.

### Markers in XML
| Element | Parent | Fields | Notes |
|---|---|---|---|
| `<marker>` | `<sequence>` | `<name>`, `<comment>`, `<in>`, `<out>` | Sequence markers |
| `<marker>` | `<clipitem>`, `<generatoritem>` | same | Clip markers (timeline-local frames) |
| `<in>` / `<out>` | inside `<marker>` | integer frames | `<out>-1</out>` = point marker (no span) |

Convert frames → timecode using the nearest ancestor `<rate><timebase>` (usually the sequence rate). Drop-frame sequences set `<ntsc>TRUE</ntsc>` — simple `frames / fps` division is wrong for 29.97 DF; use a proper DF calculator for broadcast timecode.

Mapping to live API (`markers`):
| XML | ExtendScript |
|---|---|
| `<in>` frames | `marker.start.seconds` (convert via fps) |
| `<name>` | `marker.name` |
| `<comment>` | `marker.comment` |
| sequence vs clip scope | `sequence.markers` vs `projectItem.getMarkers()` |

### Base64 graphics text
Essential Graphics, Live Text, and some title effects serialize internal AE/Premiere property blobs as **Base64** inside `<data>` or `<value>` nodes within `<filter>/<effect>`.

Detection heuristics (see `Examples/python/parse_premiere_fcpxml.py`):
1. Find `<clipitem>` or `<generatoritem>` with `<filter>/<effect>`.
2. Match effect names hinting at graphics: `AE.ADBE Text`, `graphic`, `livetype`, `mogrt`, `title`.
3. Read `<data>` / `<value>` text nodes; attempt Base64 decode (UTF-8, UTF-16-LE fallbacks).
4. Extract printable string runs from decoded binary — **best-effort only**.

Adobe staff have confirmed on the community forums that **Essential Graphics text is frequently unrecoverable once flattened to FCPXML/xmeml**. The export loses the editable Source Text JSON structure that the live API exposes (`essential-graphics-mogrt-text`). Treat XML text extraction as forensic/debug, not production.

### pathurl resolution
Media linkage uses indirection:

```
<file id="file-1">                         ← master definition (has pathurl)
  <pathurl>file://localhost/Volumes/X/clip.mov</pathurl>
</file>

<clipitem>                                 ← timeline instance
  <file id="file-1"/>                      ← reference only, no pathurl
</clipitem>
```

**Resolution algorithm:**
1. First pass: build `dict[id → pathurl]` from every `<file>` that contains `<pathurl>`.
2. Second pass: for each `<clipitem>` / `<generatoritem>`, read `<file id="…">` (attribute or child) and look up path.
3. Normalize `pathurl`:
   - Strip `file://localhost` prefix.
   - URL-decode (`%20` → space).
   - On Windows exports, paths may appear as `/C/Users/...` — map to `C:\Users\...`.
4. Fallback: match `<clipitem><name>` to `<file><name>` when `id` linkage is broken (common after manual XML edits).

**Gotcha:** Offline/unlinked media may export with empty or stale `pathurl`. Relink in Premiere before export for reliable paths.

### OTIO (25.6+)
OpenTimelineIO provides a schema-stable, JSON-based timeline model. Premiere 25.6+ exposes:

| UXP API | Purpose |
|---|---|
| `ProjectConverter` | Import/export OTIO, FCPXML, AAF |
| `exportAsFinalCutProXML` | FCP7 XML export (async) |
| OTIO import | Bring external timelines into Premiere bins/sequences |

Python-side OTIO:
```python
# Python 3 — requires opentimelineio
import opentimelineio as otio

timeline = otio.adapters.read_from_file("export.xml", adapter_name="fcp_xml")
for clip in timeline.find_clips():
    print(clip.name, clip.source_range.start_time, clip.source_range.duration)
```

OTIO preserves timing and track structure more predictably than hand-rolled xmeml parsing, but **still won't recover MOGRT Source Text JSON**. Use OTIO for edit decision lists (EDLs), conform, and VFX pulls; use live API for text/effects manipulation.

## API Surface

### ExtendScript (legacy, EOL 2026-09)
| Call | Returns | Notes |
|---|---|---|
| `sequence.exportAsFinalCutProXML(path)` | `boolean` | Exports active sequence to xmeml path |
| `sequence.importAsFinalCutProXML(path)` | `boolean` | Imports sequence from xmeml |
| `app.project.activeSequence` | `Sequence` | Must be set before export |

```js
// ExtendScript (ES3)
var seq = app.project.activeSequence;
if (!seq) { throw new Error("No active sequence"); }
var out = "/tmp/my_sequence.xml";   // absolute path; use Folder.fsName on macOS/Windows
var ok = seq.exportAsFinalCutProXML(out);
if (!ok) { throw new Error("exportAsFinalCutProXML returned false"); }
```

### UXP (25.6+, current)
| Call | Notes |
|---|---|
| `await sequence.exportAsFinalCutProXML(path)` | Async FCP7 XML export |
| `ProjectConverter` | OTIO / FCPXML / AAF import-export — see UXP reference |
| `await project.importFiles(...)` | General media import (not XML interchange) |

Verify exact signatures against `@adobe/premierepro` types for your build — UXP interchange APIs expanded across 25.6–26.0.

### Python parsing (stdlib)
| Function | Purpose |
|---|---|
| `ET.parse(path).getroot()` | Load xmeml |
| `root.iter("marker")` | All markers (sequence + clip) |
| `root.iter("clipitem")` / `"generatoritem"` | Timeline items |
| `base64.b64decode(blob)` | Decode graphics payloads |
| Custom `id → pathurl` map | Resolve media paths |

Full runnable example: `Examples/python/parse_premiere_fcpxml.py`.

## Working Examples

### 1. ExtendScript — export then parse in Python
```js
// ExtendScript (ES3) — export active sequence
(function () {
    var seq = app.project.activeSequence;
    if (!seq) { $.writeln("No active sequence"); return; }
    var f = new File(Folder.desktop.fsName + "/sequence_export.xml");
    var ok = seq.exportAsFinalCutProXML(f.fsName);
    $.writeln(ok ? "Exported: " + f.fsName : "Export failed");
})();
```

```bash
python3 Examples/python/parse_premiere_fcpxml.py ~/Desktop/sequence_export.xml > markers.json
```

### 2. Python — marker extraction with timecode
```python
import xml.etree.ElementTree as ET

def first_timebase(root):
    for rate in root.iter("rate"):
        tb = rate.findtext("timebase")
        if tb and tb.strip().isdigit():
            return int(tb.strip())
    return 25

def frames_to_tc(frames, fps):
    try:
        f = int(frames)
    except (TypeError, ValueError):
        return ""
    if f < 0:
        return ""
    s, ff = divmod(f, fps)
    h, rem = divmod(s, 3600)
    m, ss = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{ss:02d}:{ff:02d}"

tree = ET.parse("export.xml")
root = tree.getroot()
fps = first_timebase(root)

for m in root.iter("marker"):
    print({
        "name": (m.findtext("name") or "").strip(),
        "comment": (m.findtext("comment") or "").strip(),
        "in_frames": m.findtext("in"),
        "out_frames": m.findtext("out"),
        "timecode_in": frames_to_tc(m.findtext("in"), fps),
    })
```

### 3. Python — pathurl index and clip resolution
```python
import xml.etree.ElementTree as ET
from urllib.parse import unquote

def build_file_index(root):
    index = {}
    for f in root.iter("file"):
        fid = f.get("id")
        pathurl = f.findtext("pathurl")
        if fid and pathurl:
            path = unquote(pathurl.replace("file://localhost", ""))
            index[fid] = path
    return index

def clip_media_path(clipitem, index):
    f = clipitem.find("file")
    if f is None:
        return None
    fid = f.get("id")
    if fid and fid in index:
        return index[fid]
    # inline pathurl on clipitem (rare)
    pathurl = f.findtext("pathurl")
    if pathurl:
        return unquote(pathurl.replace("file://localhost", ""))
    return None

root = ET.parse("export.xml").getroot()
files = build_file_index(root)
for ci in root.iter("clipitem"):
    path = clip_media_path(ci, files)
    print(ci.findtext("name"), "→", path)
```

### 4. Python — best-effort Base64 text mining
See full implementation in `Examples/python/parse_premiere_fcpxml.py` (`extract_text_elements`, `_try_base64_text`). Minimal sketch:

```python
import base64, re, xml.etree.ElementTree as ET

HINT = re.compile(r"(graphic|text|title|livetype|mogrt)", re.I)

root = ET.parse("export.xml").getroot()
for item in list(root.iter("clipitem")) + list(root.iter("generatoritem")):
    for fx in item.iter("effect"):
        name = fx.findtext("name") or ""
        if not HINT.search(name):
            continue
        for node in fx.iter("data"):
            if not node.text:
                continue
            try:
                raw = base64.b64decode(re.sub(r"\s+", "", node.text))
                text = raw.decode("utf-8", errors="ignore")
                strings = re.findall(r"[ -~]{4,}", text)
                if strings:
                    print(item.findtext("name"), strings[:3])
            except Exception:
                pass
```

### 5. pymiere — export from Python pipeline
```python
import pymiere

seq = pymiere.objects.app.project.activeSequence
out = "/tmp/export.xml"
if not seq.exportAsFinalCutProXML(out):
    raise RuntimeError("export failed")
# hand off to parse_premiere_fcpxml.py or OTIO adapter
```

### 6. OTIO — read Premiere FCP7 export
```python
import opentimelineio as otio

tl = otio.adapters.read_from_file("export.xml", adapter_name="fcp_xml")
print("Tracks:", len(tl.tracks))
for track in tl.tracks:
    print(f"  {track.name} ({track.kind}) — {len(track)} clips")
    for item in track:
        if isinstance(item, otio.schema.Clip):
            print(f"    {item.name}: {item.source_range.duration.value} frames")
```

## Limitations

### Round-trip and data loss (critical)
| Data | Export fidelity | Round-trip risk |
|---|---|---|
| Cuts, tracks, basic clip placement | High | Low–medium (check frame rate / start timebase) |
| Sequence + clip markers | High | Low |
| Media paths | Medium | **High** if files move; `pathurl` is absolute |
| Transitions | Medium | Medium — effect params may remap |
| Color / Lumetri grades | Low–medium | **High** — often flattened or omitted |
| Essential Graphics / MOGRT text | **Very low** | **Very high** — text often unrecoverable |
| Speed / time remapping | Medium | Medium — XML representation varies |
| Nested sequences | Medium | Medium — flattening surprises |
| Audio gain / keyframes | Low–medium | High |
| Track targeting / mute / lock | Sometimes in attrs | Not in live API — **why you'd parse XML** |

**Adobe guidance:** for reliable MOGRT/text/state manipulation, use the **live scripting API** (`essential-graphics-mogrt-text`), not XML round-trip.

### Format-specific
- **FCPXML version matters** for Apple FCPX-native `.fcpxml` (DTD 1.5–1.14). Premiere's `exportAsFinalCutProXML` emits **FCP7 xmeml**, not FCPX DTD — do not assume FCPX tools consume it without testing.
- **NTSC / drop-frame:** `<ntsc>TRUE</ntsc>` changes effective frame rate; naive `frames/fps` timecode is wrong for 29.97 DF.
- **Large projects:** xmeml exports can be huge (every effect param expanded). Stream-parse (`iterparse`) for production scale.
- **Import side effects:** `importAsFinalCutProXML` creates new sequences/bins; it does not merge into the active sequence in place.
- **OTIO coverage:** newer and cleaner, but not every Premiere feature has an OTIO mapping yet — verify on your build.

## Common Errors & Gotchas

- **Symptom:** Parsed marker timecode off by hours. **Cause:** Used wrong `<timebase>` (clip rate vs sequence rate). **Fix:** Prefer sequence-level `<rate><timebase>`; walk up from marker parent.
- **Symptom:** `pathurl` is `None` for most clips. **Cause:** Only the master `<file id>` carries `pathurl`; others reference by id. **Fix:** Build id index first (§pathurl resolution).
- **Symptom:** `%20` or `%D0%` in paths. **Cause:** URL-encoded `pathurl`. **Fix:** `urllib.parse.unquote`.
- **Symptom:** Windows path `/C/Users/...` fails `os.path.exists`. **Cause:** FCP7 `file://localhost` convention. **Fix:** Strip prefix, convert `/C/` → `C:/`.
- **Symptom:** Base64 decode returns garbage/no text. **Cause:** Essential Graphics flattened to opaque binary. **Fix:** Use live API; accept best-effort only.
- **Symptom:** `exportAsFinalCutProXML` returns `false`. **Cause:** No active sequence, bad path, or permission error. **Fix:** Verify `activeSequence`, use absolute writable path.
- **Symptom:** Re-imported sequence missing effects. **Cause:** Interchange loss / unsupported effect mapping. **Fix:** Don't rely on XML for effect fidelity; bake or relink in Premiere.
- **Symptom:** OTIO import fails on 25.5. **Cause:** OTIO requires **25.6+** UXP. **Fix:** Upgrade or stay on xmeml + OTIO Python adapter.

## Workarounds

- **Need track targeting / mute state:** export FCP7 XML, parse track attributes (`TL.SQTrackTargeting`, etc.) — one of the few ways to read this state. `confidence: medium`.
- **Need marker pipeline to VFX/CSV:** export XML, run `parse_premiere_fcpxml.py`, or parse markers from live API (`markers`). `confidence: high`.
- **Need conform/EDL across apps:** prefer **OTIO** (25.6+) or OpenTimelineIO `fcp_xml` adapter over hand-rolled xmeml. `confidence: high`.
- **Need MOGRT text programmatically:** **never** round-trip XML — use ExtendScript/CEP Source Text JSON (`essential-graphics-mogrt-text`, `Examples/extendscript/update-mogrt-text.jsx`). `confidence: high`.
- **Need automated export from Python:** pymiere `exportAsFinalCutProXML` (`automation`). `confidence: medium`.
- **Validate before re-import:** diff exported XML against known-good samples; never treat XML as authoritative project backup. `confidence: high`.

## Migration

| Task | Legacy path | Modern path (25.6+) |
|---|---|---|
| Export timeline | ExtendScript `exportAsFinalCutProXML` | UXP `await sequence.exportAsFinalCutProXML` |
| Import timeline | ExtendScript `importAsFinalCutProXML` | UXP `ProjectConverter` |
| Cross-app interchange | xmeml + hand parser | OTIO via `ProjectConverter` or OTIO Python |
| Marker extraction | xmeml parse | UXP marker API (preferred) or XML export |
| Text/MOGRT | Live API only | Live API only — **no XML migration path** |

ExtendScript XML export/import EOL follows **2026-09**. Move export triggers to UXP; keep Python parsers for xmeml as long as downstream tools require FCP7 format.

## Cross-References
- `markers` — live marker API; frame vs seconds gotchas
- `essential-graphics-mogrt-text` — why XML text extraction fails; Source Text JSON contract
- `sequences-tracks-trackitems` — ticks/timebase; `exportAsFinalCutProXML` on Sequence
- `automation` — pymiere-driven export; Python pipeline glue
- `import` — `importAsFinalCutProXML` vs media import
- `uxp` — `ProjectConverter`, OTIO, async export
- `Examples/python/parse_premiere_fcpxml.py` — markers + Base64 text (runnable)
- `Examples/extendscript/update-mogrt-text.jsx` — correct approach for text (not XML)

## Sources
- FCPXML developer reference: https://fcp.cafe/developer-case-studies/fcpxml/
- Adobe community — Base64 graphics text in Premiere XML: https://community.adobe.com/t5/premiere-pro-discussions/reading-graphics-text-base64-string-from-premiere-xml-file/m-p/14231060
- OpenTimelineIO adapters: https://opentimelineio.readthedocs.io/
- Premiere UXP reference: https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
