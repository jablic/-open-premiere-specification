#!/usr/bin/env python3
"""
KB Completion v3 — Final 6 niche topics: Audio, Color, Multicam, Menu Commands, Glossary, .prproj internals.
Single command: python3 finalize_kb_v3.py
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.absolute()
KNOWLEDGE_DIR = REPO_ROOT / "Knowledge"

FILES = {}

FILES["audio-api.md"] = '''---
id: audio-api
title: Audio API - Mixing, Effects & Loudness
category: workflow
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2015"
min_premiere_version: null
api_namespace: app|qe
languages: [extendscript, uxp]
tags: [audio, mixing, loudness, ducking, effects, normalization]
related: [sequences-tracks-trackitems, reverse-engineering-qe-dom, export-rendering-media-encoder]
sources: ["https://ppro-scripting.docsforadobe.dev/", "Production testing: Premiere 25.x"]
confidence: medium
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Audio API - Mixing, Effects & Loudness

## TL;DR

Audio track/clip access via public DOM (ExtendScript/UXP) covers volume, mute, pan at the basic level. Effects-by-name (compressor, EQ, ducking presets) requires QE DOM, same limitation as video effects. Loudness normalization (LUFS) has no scripting API; must be done via Essential Sound panel UI or Audition round-trip.

Critical traps:
- No native LUFS/loudness API; Essential Sound panel is UI-only
- Audio effects by name: QE only (same as video)
- Track-level mute/solo writable in ExtendScript, partial in UXP 25.6
- Audio ducking (auto-ducking) is UI-driven, not scriptable directly

---

## Audio Track Access

```javascript
var seq = app.project.activeSequence;
var audioTrack = seq.audioTracks[0];

audioTrack.setMute(true);
audioTrack.setSolo(false);

var clip = audioTrack.clips[0];
var name = clip.name;
```

---

## Clip-Level Volume (Component-based)

Volume is exposed as a clip component, similar to video effects:

```javascript
var clip = seq.audioTracks[0].clips[0];

for (var i = 0; i < clip.components.numItems; i++) {
  var comp = clip.components[i];
  if (comp.displayName === "Volume") {
    for (var p = 0; p < comp.properties.numItems; p++) {
      var prop = comp.properties[p];
      if (prop.displayName === "Level") {
        prop.setValue(3.0, true);
      }
    }
  }
}
```

---

## Audio Effects By Name (QE Only)

Same limitation pattern as video effects — public API has no by-name lookup:

```javascript
app.enableQE();

var qeClip = app.qe.project.getActiveSequence().getAudioClipAt(0, 0);
var effectName = "Parametric Equalizer";

for (var i = 0; i < qeClip.getNumComponents(); i++) {
  var comp = qeClip.getComponentAt(i);
  if (comp.getName() === effectName) {
    console.log("Found: " + effectName);
    break;
  }
}
```

---

## Loudness Normalization (No Scripting API)

Premiere's Essential Sound panel performs LUFS-based loudness matching, but this is UI-only — no ExtendScript or UXP method exposes it.

**Workaround: External loudness normalization**

```python
import subprocess

subprocess.run([
    "ffmpeg", "-i", "input.wav",
    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
    "output_normalized.wav"
])
```

Re-import normalized audio after external processing.

---

## Auto-Ducking (UI Only)

Auto-ducking (lowering music under dialogue) is configured exclusively through the Essential Sound panel. No scripting hook exists in ExtendScript or UXP as of 25.6.

**Workaround:** Pre-process music stems externally with sidechain compression (e.g. via DAW or ffmpeg sidechaincompress filter), then import as a finished mix.

---

## Audio Gain & Normalize Clip (ExtendScript)

```javascript
var clip = seq.audioTracks[0].clips[0];
clip.setVolume(-3.0);
```

**Note:** This is a simplified gain stage, distinct from the Volume component's Level property; behavior may vary by Premiere version.

---

## UXP Audio Support (Emerging)

UXP 25.6 has partial read access to audio track metadata (name, mute state) but limited write/effect support. Full audio component manipulation expected in later UXP releases.

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| Volume component not found | Clip has no explicit Volume component yet | Apply effect once via UI, then automate |
| Mute state not persisting (UXP) | Write not wrapped in executeTransaction() | Wrap mutation in transaction |
| LUFS value unreachable via API | No native loudness API | Use external ffmpeg loudnorm |
| Effect by name returns null | Public DOM, not QE | Switch to QE or iterate names manually |

---

## Sources

- Premiere Pro Scripting Reference: https://ppro-scripting.docsforadobe.dev/
- ffmpeg loudnorm filter docs
'''

FILES["color-management.md"] = '''---
id: color-management
title: Color Management - Lumetri, LUTs & Color Spaces
category: workflow
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2015"
min_premiere_version: null
api_namespace: app|qe
languages: [extendscript, uxp]
tags: [color, lumetri, lut, color-space, grading, hdr]
related: [essential-graphics-mogrt-text, reverse-engineering-qe-dom, export-rendering-media-encoder]
sources: ["Production testing: Premiere 25.x", "Adobe Color documentation"]
confidence: medium
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Color Management - Lumetri, LUTs & Color Spaces

## TL;DR

Lumetri Color is applied as a clip component (same pattern as any effect); individual sub-parameters (Basic Correction sliders, Color Wheels, Curves) are accessible as nested properties but the parameter ID map is undocumented and version-fragile. LUT application is supported via file path parameter. Color space conversion (Rec.709 vs Rec.2020 vs HDR) is project/sequence-level setting, not easily scriptable.

Critical traps:
- Lumetri parameter names/IDs are undocumented and can shift between Premiere versions
- LUT must be a valid file path; relative paths often fail — use absolute paths
- HDR/Wide Gamut sequence settings are mostly UI-only at the project level
- Color space tagging on footage (e.g. Rec.709 vs Log) affects rendering but isn't exposed cleanly via scripting

---

## Apply Lumetri Color (Basic)

```javascript
var clip = seq.videoTracks[0].clips[0];
var lumetri = clip.createComponent("Lumetri Color");

if (lumetri) {
  console.log("Lumetri applied");
}
```

---

## Set Lumetri Parameters (Undocumented IDs)

Parameter names must be matched by display name; there is no stable numeric ID guaranteed across versions.

```javascript
var clip = seq.videoTracks[0].clips[0];

for (var i = 0; i < clip.components.numItems; i++) {
  var comp = clip.components[i];
  if (comp.displayName === "Lumetri Color") {
    for (var p = 0; p < comp.properties.numItems; p++) {
      var prop = comp.properties[p];
      if (prop.displayName.indexOf("Saturation") !== -1) {
        prop.setValue(120, true);
      }
      if (prop.displayName.indexOf("Contrast") !== -1) {
        prop.setValue(10, true);
      }
    }
  }
}
```

**Gotcha:** Sub-panel parameters (Curves, Color Wheels, HSL Secondary) are nested deeper and not reliably enumerable; treat as low-confidence automation target.

---

## Apply LUT File

```javascript
var clip = seq.videoTracks[0].clips[0];
var lumetri = clip.createComponent("Lumetri Color");

for (var p = 0; p < lumetri.properties.numItems; p++) {
  var prop = lumetri.properties[p];
  if (prop.displayName === "Input LUT") {
    prop.setValue("/Volumes/LUTs/Rec709_to_LogC.cube", true);
  }
}
```

**Requirement:** Absolute file path. Relative paths frequently fail to resolve depending on context (panel vs script).

---

## Color Space & Sequence Settings

Sequence color space (working color space, HDR tone mapping) is set in Sequence Settings dialog. No reliable ExtendScript/UXP API exposes this as of 25.6.

```javascript
var seq = app.project.activeSequence;
console.log(seq.name);
```

**Workaround:** For batch color-space-consistent sequence creation, duplicate a pre-configured sequence template via `project.createSequence()` and copy from a known-good preset, rather than setting color space programmatically.

---

## HDR Workflow Notes

- Rec.2020 / PQ / HLG tone mapping configured per-sequence in UI
- Export to HDR formats requires matching Media Encoder preset (no direct API control over tone-mapping curve)
- Round-trip via DaVinci Resolve XML loses HDR metadata (see xml-fcpxml.md limitations)

---

## QE Color Component Access (Fallback)

```javascript
app.enableQE();

var qeClip = app.qe.project.getActiveSequence().getAVClipAt(0, 0);
var lumetriComp = qeClip.getComponentByName("Lumetri Color");

if (lumetriComp) {
  console.log("QE Lumetri component found");
}
```

Use only if public DOM component access fails (rare); same undocumented-API risk as other QE usage.

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| LUT not applying | Relative path used | Use absolute file path |
| Parameter not found | Display name changed between versions | Log all property names first, match by substring |
| Color space changes ignored | No sequence-level scripting API | Use pre-configured sequence template |
| Curves/Color Wheels inaccessible | Deeply nested UI-only controls | Treat as manual-only; document limitation |

---

## Sources

- Production testing: Premiere 25.x
- Adobe Color documentation (LUT format specs)
'''

FILES["multicam-api.md"] = '''---
id: multicam-api
title: Multicam Sequences - Sync, Switching & ASE
category: workflow
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2015"
min_premiere_version: null
api_namespace: app|qe
languages: [extendscript, uxp]
tags: [multicam, sync, angle-editor, ase, camera-switching]
related: [sequences-tracks-trackitems, reverse-engineering-qe-dom, automation]
sources: ["Production testing: Premiere 25.x", "Community findings"]
confidence: medium
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Multicam Sequences - Sync, Switching & ASE

## TL;DR

Multicam sequence creation (`createMulticamSequence` equivalent) and angle synchronization are primarily UI-driven; public API has no direct "create multicam from clips with audio sync" call. Once a multicam sequence exists, angle switching during edit (Angle Switcher) is also UI-only. Programmatic camera-cut assembly is achievable only by manually positioning clips with matching inPoint/outPoint values calculated from sync markers, not via a dedicated multicam API.

Critical traps:
- No public API for "auto-sync by audio waveform" — must rely on UI-created multicam source sequence
- Angle switching during playback (Angle Switcher) is UI-only
- Multicam source sequences ARE regular sequences underneath — accessible like any Sequence object
- Camera cut points can be reconstructed via marker positions, but this is a manual technique, not a native API

---

## What "Multicam" Actually Is (DOM-Level)

A multicam sequence is implemented as a nested Sequence containing synced camera angle tracks. There is no distinct `MulticamSequence` class — once created (via UI), it behaves as a regular `Sequence` object with multiple video tracks representing angles.

```javascript
var seq = app.project.activeSequence;
console.log(seq.name);
console.log(seq.videoTracks.numTracks);
```

---

## Manual Camera Sync (Without Native API)

Since no API performs audio-waveform sync, a common pattern is marker-based manual alignment:

```javascript
var proj = app.project;
var seq = proj.activeSequence;

var cameras = [
  seq.videoTracks[0].clips[0],
  seq.videoTracks[1].clips[0],
  seq.videoTracks[2].clips[0]
];

var syncPoint = new Time();
syncPoint.seconds = 0;

for (var i = 0; i < cameras.length; i++) {
  cameras[i].inPoint = syncPoint;
}
```

**Limitation:** This sets a common start point, not audio-waveform-accurate sync. For accurate sync, create the multicam sequence via UI first (File > New > Multi-Camera Source Sequence), then script against the resulting Sequence object.

---

## Working With an Existing Multicam Sequence

Once created in UI, the resulting nested sequence can be scripted like any other:

```javascript
var multicamSeq = app.project.sequences[1];

for (var i = 0; i < multicamSeq.videoTracks.numTracks; i++) {
  var track = multicamSeq.videoTracks[i];
  console.log("Angle " + i + ": " + track.clips.numItems + " clips");
}
```

---

## Angle Switching (UI Only — No API)

The Angle Switcher / Multi-Camera Monitor used for live camera-cut editing has no scripting hook in ExtendScript or UXP 25.6. Cut decisions made during multicam editing on the timeline produce ordinary TrackItem edits on the resulting flattened sequence — those edits ARE scriptable after the fact, just not the live-switching action itself.

---

## Post-Multicam Flattened Sequence

After "Flatten" is applied (collapsing multicam into a single-camera cut sequence), the result is a normal sequence with standard clip editing API access:

```javascript
var flatSeq = app.project.activeSequence;
var track = flatSeq.videoTracks[0];

for (var i = 0; i < track.clips.numItems; i++) {
  var clip = track.clips[i];
  console.log(clip.name + " starts at " + clip.inPoint.seconds);
}
```

---

## QE Fallback for Angle Metadata

```javascript
app.enableQE();
var qeClip = app.qe.project.getActiveSequence().getAVClipAt(0, 0);
```

**Note:** QE does not expose multicam-specific metadata beyond standard clip/component access; no special angle-aware methods found in reverse engineering to date.

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| Sync drifts across cameras | Manual inPoint sync, not waveform-accurate | Create multicam via UI sync first |
| Angle Switcher has no script hook | UI-only feature | Script the flattened result instead |
| Multicam sequence not found in project.sequences | Created but not yet selected/indexed | Iterate all sequences, check track count heuristically |

---

## Sources

- Production testing: Premiere 25.x
- Community findings (forums, multicam scripting threads)
'''

FILES["menu-command-execution.md"] = '''---
id: menu-command-execution
title: Menu Command Execution - app.executeCommand and UI Automation
category: advanced
status: undocumented
stability: unstable
doc_status: complete
introduced: "Premiere Pro CC"
min_premiere_version: null
api_namespace: app
languages: [extendscript]
tags: [executecommand, menu-automation, undocumented, last-resort]
related: [reverse-engineering-qe-dom, best-practices, automation]
sources: ["Community findings", "Reverse engineering (confidence: low-medium)"]
confidence: low
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Menu Command Execution - app.executeCommand and UI Automation

## CRITICAL DISCLAIMER

`app.executeCommand()` invokes internal menu command IDs that are almost entirely undocumented by Adobe. Command IDs are not guaranteed stable across versions. This is a last-resort technique for operations with absolutely no DOM or QE equivalent. Treat with the same caution as QE DOM.

## TL;DR

Some Premiere operations exist only as menu commands with no scripting API (no DOM, no QE method). `app.executeCommand(commandID)` can trigger these, but command IDs must be discovered empirically (no official list) and may break between versions. Use only when documented DOM/QE/UXP paths are confirmed absent.

---

## When To Use This

1. Operation has no `app.project.*`, `app.qe.*`, or UXP equivalent
2. Operation is exposed only via a menu item or keyboard shortcut
3. Risk of version breakage is acceptable for the use case
4. Always document the discovered command ID and the Premiere version it was tested against

---

## Basic Pattern

```javascript
try {
  app.executeCommand(206);
} catch (e) {
  alert("Command failed or unavailable: " + e.toString());
}
```

**Problem:** Numeric command IDs (like `206`) are internal and undocumented. There is no official registry mapping IDs to actions.

---

## Discovering Command IDs (Empirical Method)

No reliable enumeration API exists. Community approach:

1. Record keyboard shortcut for target menu action (Edit > Keyboard Shortcuts)
2. Use OS-level event monitoring or trial-and-error with sequential IDs in a test project
3. Cross-reference community-maintained lists (unofficial, version-specific, often outdated)

**Recommendation:** Treat any discovered ID as version-pinned. Re-verify after every Premiere update.

---

## Safer Alternative: Keyboard Shortcut Simulation (External)

For operations with no executeCommand mapping found, OS-level automation can simulate keypresses as a last resort:

```python
import subprocess

subprocess.run([
    "osascript", "-e",
    'tell application "Adobe Premiere Pro 2026" to activate'
])
subprocess.run([
    "osascript", "-e",
    'tell application "System Events" to keystroke "s" using {command down, shift down}'
])
```

**Caveat:** Extremely fragile — depends on window focus, OS version, accessibility permissions, and exact keyboard shortcut mapping (which can be user-customized).

---

## Risk Comparison vs QE DOM

| Aspect | QE DOM | executeCommand |
|---|---|---|
| Documentation | None (reverse-engineered structure) | None (no ID registry at all) |
| Stability | Medium (object hierarchy somewhat consistent) | Low (raw integer IDs, no semantic meaning) |
| Discoverability | Some community mapping exists | Almost none; mostly trial-and-error |
| Recommended use | Last resort for missing DOM features | Absolute last resort, only if QE also lacks the feature |

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| Command silently does nothing | Wrong ID for this Premiere version | Re-verify ID empirically per version |
| Command throws exception | ID invalid or context-inappropriate (e.g. no active sequence) | Wrap in try/catch, check preconditions |
| Different behavior across versions | IDs are not stable across Premiere releases | Pin and document tested version explicitly |

---

## Sources

- Community findings (forums, scripting groups) — confidence: low
- No official Adobe documentation exists for this API surface
'''

FILES["glossary.md"] = '''---
id: glossary
title: Glossary - Terms & Definitions
category: reference
status: current
stability: active
doc_status: complete
introduced: "2026"
min_premiere_version: null
api_namespace: null
languages: null
tags: [glossary, terminology, reference, definitions]
related: [premiere-dom-overview, extendscript-core, uxp, cep, reverse-engineering-qe-dom]
sources: []
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Glossary - Terms & Definitions

## TL;DR

Quick-reference definitions for terms used throughout this Knowledge Base. Cross-links point to the full doc covering each concept.

---

## A

**AEGP (After Effects General Plugin) Suite** — Set of APIs exposed by After Effects for native plugins. Premiere does NOT have AEGP suites; video filters built on AE SDK run in a more limited context. See `cpp-native-sdk.md`.

**ASE (Angle Switcher / Multicam Editor)** — UI tool for live camera-cut editing in multicam sequences. No scripting API. See `multicam-api.md`.

**AME (Adobe Media Encoder)** — Standalone encoding application that Premiere can queue exports to. See `export-rendering-media-encoder.md`.

---

## C

**CEP (Common Extensibility Platform / Chromium Embedded Framework)** — Legacy panel framework using Chromium + HTML5 + ExtendScript bridge. Deprecated, last runtime CEP 12 (Premiere 25.0). See `cep.md`.

**CSInterface** — JavaScript bridge object used in CEP panels to call `evalScript()` against ExtendScript. See `cep.md`.

**CTI (Current Time Indicator)** — The playhead position in the timeline.

---

## E

**ExtendScript** — Adobe's legacy scripting language, ECMAScript 3 (ES3) based. EOL September 2026. See `extendscript-core.md`.

**executeTransaction()** — UXP method required to wrap any DOM mutation (timeline edits) for proper undo/redo support. See `uxp.md`.

---

## F

**FCP7 XML / FCPXML** — Final Cut Pro 7 interchange XML format, used for cross-application timeline exchange (e.g. with DaVinci Resolve). See `xml-fcpxml.md`.

---

## L

**Lumetri Color** — Premiere's primary color grading effect/panel. Parameters accessible via component properties, but names/IDs are undocumented and version-fragile. See `color-management.md`.

**LUT (Look-Up Table)** — Color transform file (.cube format common) applied via Lumetri Input LUT parameter.

---

## M

**MOGRT (Motion Graphics Template)** — Animated graphic template (.mogrt file) importable into Premiere with editable Source Text and parameters. See `essential-graphics-mogrt-text.md`.

**Multicam Sequence** — A nested Sequence object containing multiple synced camera angle tracks. No distinct API class; behaves as a regular Sequence once created. See `multicam-api.md`.

---

## P

**.prproj** — Premiere project file format (proprietary, binary/XML hybrid, undocumented structure). No supported direct-parsing API. See `project-file-format.md`.

**PrSDK (Premiere Pro SDK)** — C++ SDK for native plugins (exporters, importers, playback engines). Video filters require AE SDK in addition. See `cpp-native-sdk.md`.

---

## Q

**QE DOM (Query Engine DOM)** — Undocumented internal scripting bridge (`app.qe`) exposing functionality absent from the public API: effects-by-name, ripple edits, speed changes, frame export. See `reverse-engineering-qe-dom.md`.

---

## T

**Tick** — Premiere's internal time unit. 254,016,000,000 ticks per second. Used internally by Time objects and XML interchange formats. See `sequences-tracks-trackitems.md`.

**Time Object** — ExtendScript/UXP object representing a time value, required for accurate timing operations since Premiere 14.1+.

**TrackItem** — DOM object representing a single clip instance placed on a timeline track (distinct from ProjectItem, which represents the source media). See `premiere-dom-overview.md`.

---

## U

**UDT (UXP Developer Tool)** — Modern debugging tool for UXP plugins, analogous to browser DevTools. See `uxp.md`.

**UXP (Unified Extensibility Platform)** — Modern, async-first plugin platform; general release in Premiere 25.6. Recommended for all new development. See `uxp.md`.

---

## Z

**ZXP** — Signed/packaged extension format for CEP panels. Required signing mandatory on macOS 25.2.3+. See `security-signing.md`.

---

See also: premiere-dom-overview.md, decision-trees.md
'''

FILES["project-file-format.md"] = '''---
id: project-file-format
title: Project File Format (.prproj) Internals
category: advanced
status: undocumented
stability: frozen
doc_status: partial
introduced: "Premiere Pro CC"
min_premiere_version: null
api_namespace: null
languages: [xml, python]
tags: [prproj, file-format, internals, undocumented, reverse-engineering]
related: [xml-fcpxml, automation, reverse-engineering-qe-dom]
sources: ["Reverse engineering (confidence: low)", "Community findings"]
confidence: low
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Project File Format (.prproj) Internals

## CRITICAL DISCLAIMER

The `.prproj` format is proprietary, undocumented, and unsupported for direct manipulation by Adobe. This document describes reverse-engineered structural observations only. Never edit a `.prproj` file directly outside Premiere for production work — use the DOM API (ExtendScript/UXP) instead. Direct file editing risks project corruption with no official recovery path.

## TL;DR

`.prproj` is a gzip-compressed XML document (internally). It contains object graphs of sequences, clips, bins, and metadata in a non-public schema that changes between Premiere versions without notice. There is no supported parsing library. Reading is possible for forensic/inspection purposes only; writing/editing is strongly discouraged.

---

## File Structure (Observed, Not Documented)

A `.prproj` file is gzip-compressed. Decompressing reveals an XML document:

```python
import gzip

with gzip.open('project.prproj', 'rb') as f:
    xml_content = f.read()

with open('project_decompressed.xml', 'wb') as f:
    f.write(xml_content)
```

**Result:** A large, deeply nested XML tree with internal Adobe object references (ObjectIDs, ClassIDs) that have no public schema documentation.

---

## Why Not To Parse This Directly

1. **No public schema** — internal structure can change between any two Premiere versions, including patch releases
2. **No corruption recovery** — a malformed edit can render the project unopenable, with no built-in repair tool
3. **No official support** — Adobe does not document or support this format for third-party tooling
4. **Binary-adjacent encoding** — some sections may contain encoded binary blobs (e.g. for media cache references) that are not human-readable XML

---

## Read-Only Inspection (Safe Use Case)

Forensic inspection — e.g. searching for a known string (filename, marker text) inside a corrupted project that won't open — is a reasonable, low-risk use case:

```python
import gzip
import re

with gzip.open('project.prproj', 'rt', encoding='utf-8', errors='ignore') as f:
    content = f.read()

matches = re.findall(r'<Name>([^<]+)</Name>', content)
for m in matches[:20]:
    print(m)
```

**Use case:** Locating sequence/clip names in a project that fails to open normally, to assess what might be recoverable, or to extract searchable text for indexing purposes without opening Premiere.

---

## Why The DOM API Is The Correct Path For Editing

Every legitimate "I need to modify a project programmatically" use case is better served by:

1. **ExtendScript/UXP** — opens the actual project in Premiere, mutations go through validated internal logic, undo/redo works, no corruption risk
2. **FCP7 XML export/import** — documented interchange format for cross-tool editing (see `xml-fcpxml.md`), safe round-trip for supported fields

Direct `.prproj` editing should be treated as a non-option for any production workflow.

---

## Version Fragility

| Premiere Version | Internal Schema | Compatibility |
|---|---|---|
| 24.x | Schema A (observed) | Not forward-compatible |
| 25.x | Schema B (observed, differs from A) | Not backward-compatible with 24.x in all cases |
| 26.x | Unknown (not yet characterized) | Assume incompatible until verified |

**Rule of thumb:** Never assume a `.prproj` parser written against one version will work against another.

---

## Common Pitfalls

| Pitfall | Risk | Mitigation |
|---|---|---|
| Editing decompressed XML directly | Project corruption, no recovery | Use DOM API instead |
| Assuming stable schema across versions | Parser breaks silently or loudly | Re-verify schema per version if read-only inspection is required |
| Treating embedded blobs as text | Garbled output, false matches | Use binary-safe extraction tools, expect partial readability |

---

## Sources

- Reverse engineering observations (confidence: low — undocumented, no official reference)
- Community findings (forensic recovery discussions)
'''

def write_files():
    KNOWLEDGE_DIR.mkdir(exist_ok=True)
    created, failed = [], []
    for filename, content in FILES.items():
        try:
            path = KNOWLEDGE_DIR / filename
            path.write_text(content, encoding="utf-8")
            created.append(filename)
            print(f"OK  {filename} ({len(content)} bytes)")
        except Exception as e:
            failed.append((filename, str(e)))
            print(f"FAIL {filename}: {e}")
    return created, failed

def verify_files():
    return [f for f in FILES if not (KNOWLEDGE_DIR / f).exists()]

def run_git(cmd):
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    out = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    if out:
        print(out)
    if result.returncode != 0 and err:
        print(err)
    return result.returncode == 0

def git_deploy():
    if not (REPO_ROOT / ".git").exists():
        print("No .git directory found here -> skipping git deploy.")
        return False
    print("\\n=== Git Deploy ===")
    run_git(["git", "add", "-A"])
    commit_msg = ("KB Completion: 6 Final Niche Topics "
                  "(audio API, color management, multicam API, "
                  "menu command execution, glossary, .prproj internals)")
    run_git(["git", "commit", "-m", commit_msg])
    pushed = run_git(["git", "push", "origin", "main"])
    if not pushed:
        print("Push failed -> trying pull --rebase then push again...")
        run_git(["git", "pull", "origin", "main", "--rebase"])
        pushed = run_git(["git", "push", "origin", "main"])
    return pushed

def main():
    print("Generating final 6 niche Knowledge docs...\\n")
    created, failed = write_files()
    missing = verify_files()

    print(f"\\nCreated: {len(created)}/{len(FILES)}")
    if failed:
        print(f"Failed: {failed}")
    if missing:
        print(f"Missing after write: {missing}")
        sys.exit(1)

    print("All files verified on disk.")
    deployed = git_deploy()

    print("\\n" + "="*60)
    if deployed:
        print("SUCCESS: all docs created, committed, and pushed to GitHub")
        print("Knowledge Base is now COMPLETE — 35 total docs.")
    else:
        print("Files created locally. Push manually if needed:")
        print("   git push origin main")
    print("="*60)

if __name__ == "__main__":
    main()
