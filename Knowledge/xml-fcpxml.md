---
id: xml-fcpxml
title: XML, FCPXML & FCP7 XML (xmeml)
category: interop
status: current
stability: active
doc_status: partial
introduced: "Long-standing interchange"
deprecated: null
eol: null
min_premiere_version: null
api_namespace: none
languages: [python, xml, extendscript]
tags: [fcpxml, fcp7-xml, xmeml, otio, markers, base64, essential-graphics, timecode, parsing, lxml, elementtree]
related: [markers, essential-graphics-mogrt-text, sequences-tracks-trackitems, automation]
supersedes: []
superseded_by: []
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://fcp.cafe/developer-case-studies/fcpxml/
  - https://community.adobe.com/t5/premiere-pro-discussions/reading-graphics-text-base64-string-from-premiere-xml-file/m-p/14231060
  - https://opentimelineio.readthedocs.io/
---

# XML, FCPXML & FCP7 XML (xmeml)

## TL;DR
- Premiere imports/exports legacy **FCP7 XML (xmeml)** and **FCPXML**; **25.6+ adds OTIO**. **Partially seeded.**
- **Markers** are easy (`<marker>` tags). **Essential Graphics text** is hard — nested `<filter>/<effect>`, frequently **Base64-encoded in `<data>` tags**, and may be unrecoverable once flattened.
- Export via `sequence.exportAsFinalCutProXML(path)` (ExtendScript) or UXP `exportAsFinalCutProXML`.

## Status & Lifecycle
- Interchange format, `current`. Useful as a read-back channel for state the live API won't expose (e.g. track targeting). See `00-technology-status-matrix`.

## Architecture
`xmeml` document → `<sequence>` → `<media>` → `<video>/<audio>` → `<track>` → `<clipitem>`/`<generatoritem>` → `<filter>/<effect>` + `<marker>`. Media via `<file id>` → `<pathurl>`. **STUB: annotated tree.**

## API Surface
**Markers:** `<marker>` children of `<clipitem>`/`<sequence>`: `<name>`, `<comment>`, `<in>`, `<out>` (frames). **Media:** `<file id>` → `<pathurl>` (`file://localhost/...`), `<rate>/<timebase>` + `<ntsc>`, `<timecode>`. **Graphics text:** nested `<filter>/<effect>`, often Base64 in `<data>`; matchName `AE.ADBE Text`/DisplayName `Text` in the effect `InstanceName`. **STUB.**

## Working Examples
```python
# Python — markers + best-effort graphics-text from an FCP7 XML export
import xml.etree.ElementTree as ET, base64, re
root = ET.parse('export.xml').getroot()
for m in root.iter('marker'):
    name = (m.findtext('name') or '').strip()
    tc_in = m.findtext('in')
    # frames -> timecode via sequence <timebase>
```
**STUB: full marker+caption extractor with Base64 decode + regex cleanup, frame→TC.**

## Limitations
Adobe staff note Essential Graphics text is effectively **unrecoverable once flattened to FCPXML** — round-trip the live API instead when you need reliable text. FCPXML version matters (1.5–1.14; DTD-versioned). **STUB.**

## Common Errors & Gotchas
In Premiere XML the `<pathurl>` is often only on the first/master `<clipitem>` for a `file id`; later clipitems reference by `id` only — resolve by matching `<name>`. **STUB.**

## Workarounds
Use `opentimelineio.adapters.fcp_xml`; for OTIO use UXP `ProjectConverter` (25.6+). **STUB.**

## Migration
**STUB.**

## Cross-References
- `markers`
- `essential-graphics-mogrt-text`
- `sequences-tracks-trackitems`
- `automation`

## Sources
- https://fcp.cafe/developer-case-studies/fcpxml/
- https://community.adobe.com/t5/premiere-pro-discussions/reading-graphics-text-base64-string-from-premiere-xml-file/m-p/14231060
- https://opentimelineio.readthedocs.io/

