---
id: automation
title: Automation (pymiere, BridgeTalk, CLI)
category: interop
status: legacy
stability: frozen
doc_status: complete
introduced: null
deprecated: "rides on ExtendScript (EOL 2026-09)"
eol: "2026-09"
min_premiere_version: null
api_namespace: app
languages: [python, extendscript, javascript-es3]
tags: [automation, pymiere, bridgetalk, ole, com, applescript, jsx, headless, batch]
related: [extendscript-core, export-rendering-media-encoder, ai-integration, reverse-engineering-qe-dom, cep, xml-fcpxml]
supersedes: []
superseded_by: [uxp]
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://github.com/qmasingarbe/pymiere
  - https://pypi.org/project/pymiere/
  - https://github.com/qmasingarbe/pymiere/blob/master/example_and_documentation.md
  - https://github.com/qmasingarbe/pymiere/blob/master/demo_ui.py
  - https://extendscript.docsforadobe.dev/extendscript-tools/bridgetalk.html
  - https://ppro-scripting.docsforadobe.dev/
---

# Automation (pymiere, BridgeTalk, CLI)

> External drivers for Premiere automation: Python via **pymiere**, inter-app **BridgeTalk**,
> platform glue (**OLE/COM** on Windows, **AppleScript** on macOS), and command-line **`.jsx`**
> execution. All paths ultimately reach the ExtendScript DOM inside a **running** Premiere process.
> There is **no headless mode**.

## TL;DR
- **pymiere** mirrors the ExtendScript DOM in Python over an HTTP bridge to the **Pymiere Link** CEP extension; requires Premiere running and the extension installed.
- **Unmaintained but functional** — README last broadly tested through **Premiere 23.1 (2023)**; pin your Premiere version.
- Cross-platform glue: Windows **OLE/COM** (`DoScript`), macOS **AppleScript**/`osascript`, **BridgeTalk** for inter-Adobe-app messaging.
- **`TICKS_PER_SECONDS = 254016000000`** — use `pymiere.wrappers.time_from_seconds()` / `timecode_from_seconds()` at boundaries.
- **No headless Premiere** — GUI app must be running; pymiere can *launch* Premiere but cannot drive it without a UI session.
- Inherits ExtendScript **EOL 2026-09**; UXP scripting is the forward path (`uxp`).

## Status & Lifecycle
- **Status:** `legacy` — all automation paths ride on ExtendScript, which Adobe froze in 2024 and supports through **September 2026**.
- **pymiere:** explicitly **unmaintained** since ~2023; newer Premiere API members may not be wrapped in Python.
- **BridgeTalk / OLE / AppleScript / CLI `.jsx`:** long-standing patterns, no new Adobe investment; still work on current builds but are brittle across versions.
- **Replacement:** UXP scripting (25.6+) for in-process automation; external Python pipelines should plan a UXP SDK path or isolate transport behind an adapter. See `00-technology-status-matrix`.

## Architecture

### pymiere stack
```
Python script (pymiere)
    │  HTTP POST (requests library) — typically localhost
    ▼
Pymiere Link CEP extension (Node.js mini-server inside Premiere)
    │  CSInterface.evalScript(extendScriptCode, callback)
    ▼
ExtendScript engine (ES3, synchronous, in-process)
    │  app / qe DOM
    ▼
Premiere Pro (GUI application — must be running)
```

**Step-by-step:**
1. Python call (property get, method invoke) → pymiere serializes to ExtendScript source string.
2. pymiere POSTs the script to **Pymiere Link** over HTTP.
3. Pymiere Link executes it via `evalScript` inside Premiere.
4. Return value JSON-encoded back to Python; pymiere hydrates Python proxy objects.

**Entry points:**
| Module | Purpose |
|---|---|
| `pymiere.objects.app` | Official DOM mirror (`project`, `activeSequence`, `encoder`, …) |
| `pymiere.objects.qe` | QE DOM mirror (after `app.enableQE()` on the ExtendScript side) |
| `pymiere.wrappers.*` | Higher-level helpers (`time_from_seconds`, `has_media_encoder`, `get_system_sequence_presets`, …) |
| `pymiere.exe_utils.*` | Process detection / launch (`is_premiere_running`, `start_premiere`) |

**Installation prerequisites:**
1. `pip install pymiere`
2. Install **Pymiere Link** CEP extension (`pymiere_link.zxp`) — verify under `Window > Extensions > Pymiere Link`.
3. Premiere Pro running with a project open (for most operations).

### BridgeTalk (inter-Adobe-app)
`BridgeTalk` is an ExtendScript global for messaging between Creative Cloud applications (Premiere ↔ Media Encoder ↔ After Effects, etc.). Runs **inside** an ExtendScript context — not directly from Python.

```
ExtendScript in Premiere
    │  BridgeTalk.bringToFront("ame")
    │  BridgeTalk.getStatus("ame")
    │  bt = new BridgeTalk(); bt.target = "ame"; bt.body = "..."; bt.send()
    ▼
Target Adobe app (separate process)
```

Common uses: check whether AME is installed/running before queueing encodes (`export-rendering-media-encoder`), send jobs cross-app, bring another host to front.

### Windows OLE/COM automation
On Windows, external processes can drive Premiere via **COM Automation** without pymiere:

```
External process (Python win32com, PowerShell, VBScript)
    │  CreateObject("Premiere.Application")  or  GetObject(, "Premiere.Application")
    │  app.DoScript(jsxSource, scriptLanguage, undoString)
    ▼
Premiere Pro COM server → ExtendScript engine
```

- **ProgID** varies by version: `"Premiere.Application"`, `"PremierePro.Application"`, or version-suffixed variants — probe on the target machine.
- `DoScript` executes ExtendScript source synchronously; Premiere must already be running (or COM may launch it, depending on install/registration).
- Returns a string; errors surface as COM exceptions or `"EvalScript error."`-style failures.
- **Fragile:** COM registration breaks across major upgrades; not officially documented for server/batch use.

### macOS AppleScript / osascript
On macOS, external automation typically uses **AppleScript** through `osascript`:

```
Terminal / Python subprocess
    │  osascript -e 'tell application "Adobe Premiere Pro 2025" to ...'
    ▼
Premiere AppleScript dictionary → do script "..." language javascript
    ▼
ExtendScript engine
```

- App name string must match the installed version (`"Adobe Premiere Pro 2025"`, etc.).
- `do script` with `language javascript` runs ExtendScript (not modern JS).
- AppleScript can also open documents, activate the app, and query basic state — but DOM depth is limited compared to full ExtendScript.
- **Fragile:** app name changes every year; sandbox/Gatekeeper can block unsigned automation unless the user grants Accessibility permissions.

### Command-line `.jsx` execution
Adobe ships **ExtendScript Toolkit (ESTK)** historically for running `.jsx` files; ESTK is **deprecated and dead on modern macOS** (32-bit). Current practical CLI paths:

| Platform | Mechanism | Notes |
|---|---|---|
| Windows | COM `DoScript` with file contents | Most reliable CLI-style path on Windows |
| macOS | `osascript` + `do script` with file contents read in Python/shell | Requires correct app name string |
| Either | pymiere / CEP panel `evalScript` | Not truly "CLI" but scriptable from terminal via Python |
| Either | `-script` flag (undocumented / version-variable) | Some builds accept `Adobe Premiere Pro.exe -script path.jsx` on Windows — **not guaranteed**, test per version |

**Recommended pattern:** keep `.jsx` logic in standalone files; external driver reads the file as UTF-8 and passes contents to `DoScript` (Windows) or AppleScript `do script` (macOS). Do **not** rely on a single cross-platform CLI invocation without per-OS branching.

## API Surface

### pymiere core
| Symbol | Type / value | Notes |
|---|---|---|
| `pymiere.objects.app` | Proxy root | Same shape as ExtendScript `app` |
| `pymiere.objects.qe` | Proxy root | QE DOM; call `.inspect()` to dump methods |
| `TICKS_PER_SECONDS` | `254016000000` | In `pymiere.wrappers`; Adobe-confirmed ticks/sec |
| `time_from_seconds(n)` | `Time` proxy | Construct a Time object |
| `timecode_from_seconds(n, seq)` | `string` | Timecode string for QE ops |
| `timecode_from_time(time, seq)` | `string` | Time object → timecode |
| `has_media_encoder()` | `bool` | AME installed and reachable |
| `get_system_sequence_presets(...)` | `string` path | Locate installed `.sqpreset` files |
| `check_active_sequence()` | `(bool, bool)` | Project open + active sequence |
| `get_item_recursive(item, ...)` | `list` | Walk bin tree |
| `is_premiere_running()` | `(bool, pid)` | Process probe |
| `start_premiere()` | `int` pid | Launch if not running; waits for CEP panels |

### TICKS_PER_SECONDS and time conversion
Premiere's internal time unit is **ticks**. One second = **254,016,000,000** ticks.

```python
# Python (pymiere)
from pymiere.wrappers import TICKS_PER_SECONDS, time_from_seconds

ticks = int(5.0 * TICKS_PER_SECONDS)          # 5 seconds → ticks
t = time_from_seconds(5.0)                    # Time proxy for API calls
seconds = t.seconds                           # read back
```

Tick values exceed 32-bit integer range; the ExtendScript API often exchanges them as strings. Prefer computing in **seconds** or **frames** in Python and converting at the API boundary. See `sequences-tracks-trackitems` for frame ↔ second patterns.

### BridgeTalk (ExtendScript)
| Call | Returns | Purpose |
|---|---|---|
| `BridgeTalk.getStatus("ame")` | `"ISNOTINSTALLED"` / `"ISNOTRUNNING"` / running | AME availability |
| `BridgeTalk.getStatus("premierepro")` | status string | Premiere status from another app |
| `BridgeTalk.bringToFront(appId)` | — | Focus target app |
| `new BridgeTalk()` + `.target` + `.body` + `.send()` | — | Send script/message to another host |

Host IDs include `"premierepro"`, `"ame"`, `"aftereffects"`. Exact strings vary — confirm in ExtendScript docs for your suite version.

## Working Examples

### 1. pymiere — basic project inspection
```python
# Python 3 — requires Premiere running + Pymiere Link installed
import pymiere
from pymiere.wrappers import check_active_sequence

ok_proj, ok_seq = check_active_sequence(crash=False)
if not ok_proj:
    raise RuntimeError("Open a Premiere project first.")

proj = pymiere.objects.app.project
print("Project:", proj.name)
print("Sequences:", proj.sequences.numSequences)

if ok_seq:
    seq = proj.activeSequence
    print("Active sequence:", seq.name)
    print("Video tracks:", seq.videoTracks.numTracks)
    for i in range(seq.videoTracks.numTracks):
        track = seq.videoTracks[i]
        print(f"  V{i}: {track.clips.numItems} clips")
```

### 2. pymiere — import media and insert on timeline
```python
import pymiere
from pymiere.wrappers import time_from_seconds

project = pymiere.objects.app.project
media_path = r"/absolute/path/to/clip.mp4"   # macOS: "/Users/..."

success = project.importFiles(
    [media_path],
    suppressUI=True,
    targetBin=project.getInsertionBin(),
    importAsNumberedStills=False,
)
if not success:
    raise RuntimeError("importFiles returned False")

items = project.rootItem.findItemsMatchingMediaPath(media_path, ignoreSubclips=False)
if not items:
    raise RuntimeError("Imported item not found in bin.")

project.activeSequence.videoTracks[0].insertClip(items, time_from_seconds(0))
```

### 3. pymiere — place MOGRT and patch text
```python
import json
import pymiere
from pymiere.wrappers import time_from_seconds

seq = pymiere.objects.app.project.activeSequence
mogrt_path = r"/absolute/path/to/lower-third.mogrt"

clip = seq.importMGT(
    path=mogrt_path,
    time=time_from_seconds(1.0),
    videoTrackIndex=1,
    audioTrackIndex=1,
)
component = clip.getMGTComponent()
if component is None:
    # Premiere-native MOGRT type — fall back to components list
    component = next(c for c in clip.components if c.displayName)

for prop in component.properties:
    if prop.displayName in ("Source Text", "Text"):
        blob = json.loads(prop.getValue())
        new_text = "Updated from Python"
        blob["textEditValue"] = new_text
        blob["fontTextRunLength"] = [len(new_text)]   # CRITICAL — see essential-graphics-mogrt-text
        prop.setValue(json.dumps(blob), True)
        break
```

See `essential-graphics-mogrt-text` for the full Source Text JSON contract.

### 4. pymiere — batch export to Media Encoder
```python
import pymiere
from pymiere.wrappers import has_media_encoder

if not has_media_encoder():
    raise RuntimeError("Adobe Media Encoder not available.")

pymiere.objects.app.encoder.launchEncoder()
project = pymiere.objects.app.project
EPR = r"/path/to/H264-Match-Source.epr"   # use H.264 — HEVC blocked 25.5+ (export-rendering-media-encoder)
OUT_DIR = r"/path/to/exports"

for i in range(project.sequences.numSequences):
    project.openSequence(project.sequences[i].sequenceID)
    seq = project.activeSequence
    out = f"{OUT_DIR}/{seq.name}.mp4"
    job_id = pymiere.objects.app.encoder.encodeSequence(
        seq, out, EPR,
        pymiere.objects.app.encoder.ENCODE_ENTIRE,
        removeOnCompletion=False,
    )
    print(f"Queued {seq.name}: job_id={job_id}")

pymiere.objects.app.encoder.startBatch()
```

**Note:** pymiere returns immediately; AME encodes asynchronously. You **cannot** bind AME completion events from Python — do that in ExtendScript (`export-rendering-media-encoder`).

### 5. pymiere — QE razor cut
```python
import pymiere
from pymiere.wrappers import timecode_from_time

seq = pymiere.objects.app.project.activeSequence
pymiere.objects.app.enableQE()   # must be called on ExtendScript side; pymiere forwards it

playhead = seq.getPlayerPosition()
tc = timecode_from_time(playhead, seq)
track = pymiere.objects.qe.project.getActiveSequence().getVideoTrackAt(0)
track.razor(tc)
```

### 6. Windows COM — run a `.jsx` file from Python
```python
# Windows only — requires pywin32: pip install pywin32
import win32com.client

jsx_path = r"C:\scripts\my-script.jsx"
with open(jsx_path, encoding="utf-8") as f:
    source = f.read()

app = win32com.client.Dispatch("Premiere.Application")
# scriptLanguage: 1246775072 = JavaScript (ExtendScript)
result = app.DoScript(source, 1246775072, "Python automation")
print(result)
```

Save `.jsx` files as **UTF-8** for Cyrillic safety (`extendscript-core`).

### 7. macOS — run ExtendScript via osascript
```bash
# Replace app name with your installed version string
osascript <<'APPLESCRIPT'
tell application "Adobe Premiere Pro 2025"
    activate
    do script "var seq = app.project.activeSequence; seq.name;" language javascript
end tell
APPLESCRIPT
```

From Python:
```python
import subprocess

jsx = 'app.project.activeSequence.name'
app_name = "Adobe Premiere Pro 2025"
script = f'tell application "{app_name}" to do script "{jsx}" language javascript'
result = subprocess.check_output(["osascript", "-e", script], text=True)
print(result.strip())
```

Escape embedded quotes in `jsx` before passing to AppleScript.

### 8. BridgeTalk — guard AME before queueing (ExtendScript)
```js
// ExtendScript (ES3) — run inside Premiere, not from Python directly
function ameReady() {
    var status = BridgeTalk.getStatus("ame");
    if (status === "ISNOTINSTALLED") { return false; }
    return true;
}

if (!ameReady()) {
    $.writeln("AME not available");
} else {
    app.encoder.launchEncoder();
    // ... encodeSequence calls
}
```

Full guarded batch pattern: `Examples/extendscript/batch-export-guarded.jsx`.

### 9. Export FCP7 XML for external parsing
```python
import pymiere

seq = pymiere.objects.app.project.activeSequence
out_path = r"/tmp/sequence_export.xml"
ok = seq.exportAsFinalCutProXML(out_path)
if not ok:
    raise RuntimeError("exportAsFinalCutProXML failed")
# Parse with Examples/python/parse_premiere_fcpxml.py — see xml-fcpxml
```

## Limitations

### Hard walls
- **No headless Premiere.** pymiere, COM, AppleScript, and BridgeTalk all require the GUI application. `start_premiere()` launches the UI; there is no batch renderer without a logged-in desktop session.
- **No AME event binding from Python.** Encoder callbacks (`encoder.bind(...)`) exist only in ExtendScript. pymiere cannot subscribe to encode-complete events — poll output files, write ExtendScript event handlers, or use AME's own scripting API separately.
- **Synchronous blocking.** ExtendScript runs on Premiere's main thread. Long Python-driven loops block the UI — chunk work and yield, or accept UI freeze during batch ops.
- **pymiere unmaintained.** Newer Premiere 24.x/25.x API members may exist in ExtendScript but not in the autogenerated Python mirror. Workaround: send raw ExtendScript via pymiere's lower-level eval if exposed, or drop to COM/AppleScript with hand-written `.jsx`.
- **Pymiere Link is a CEP extension.** Inherits CEP loading/degradation issues on modern Premiere builds (`cep`, `00-technology-status-matrix`). If Pymiere Link fails to load, pymiere HTTP calls fail.
- **COM/AppleScript fragility.** ProgIDs and app name strings change yearly; automation permissions (macOS Accessibility, Windows UAC) can block unattended runs.
- **CLI `-script` flag unreliable.** Do not build production pipelines on an undocumented launch flag without version pinning and CI verification.
- **QE via pymiere is crash-prone.** QE is undocumented; calling `pymiere.objects.qe` methods can hard-crash Premiere (`reverse-engineering-qe-dom`).

### Inherited ExtendScript ceilings
Everything in `extendscript-core` §Limitations applies: ES3 only, no native JSON in host (Pymiere Link bundles json2), `EvalScript error.` swallows stack traces unless host code wraps try/catch, frozen API with permanent gaps.

## Common Errors & Gotchas

- **Symptom:** `Connection refused` / HTTP error from pymiere. **Cause:** Premiere not running, or Pymiere Link not installed/loaded. **Fix:** Start Premiere; verify `Window > Extensions > Pymiere Link` exists; reinstall `pymiere_link.zxp`.
- **Symptom:** `No sequence is currently opened in the UI`. **Cause:** Project open but no active sequence. **Fix:** `project.openSequence(sequenceID)` before timeline ops.
- **Symptom:** `importFiles` returns `True` but item is `None`. **Cause:** `importFiles` returns boolean, not the item. **Fix:** `findItemsMatchingMediaPath` afterward (`import`).
- **Symptom:** MOGRT text renders blank after Python edit. **Cause:** `fontTextRunLength` not updated. **Fix:** Set to `[len(newText)]` (`essential-graphics-mogrt-text`).
- **Symptom:** `encodeSequence` returns job ID but nothing queues (25.5+). **Cause:** HEVC/H.265 preset — programmatically blocked. **Fix:** Use H.264 preset (`export-rendering-media-encoder`).
- **Symptom:** COM `DoScript` fails after upgrade. **Cause:** ProgID/registration changed. **Fix:** Re-register or update ProgID string; prefer pymiere/CEP bridge.
- **Symptom:** AppleScript "Application isn't running." **Cause:** Wrong app name string for installed version. **Fix:** Match exact name from `/Applications` or `system_profiler SPApplicationsDataType`.
- **Symptom:** Tick/time off-by-one frame. **Cause:** Integer tick math overflow or frame-rate mismatch. **Fix:** Compute in seconds; use `time_from_seconds`; see `sequences-tracks-trackitems`.
- **Symptom:** pymiere attribute missing on new Premiere build. **Cause:** Unmaintained autogen mirror. **Fix:** Pin Premiere version; extend mirror manually; or use raw `.jsx` transport.

## Workarounds

- **Isolate transport from business logic.** Keep Premiere mutations in `.jsx` files (or a small set of host functions); Python/COM/AppleScript only passes JSON args and reads JSON results. Makes a future UXP port mechanical. `confidence: high`.
- **Pin Premiere + pymiere versions** in production; test upgrades in a VM before rolling. `confidence: high`.
- **For read-only state the API won't expose** (track targeting, some effect params), export FCP7 XML and parse externally (`xml-fcpxml`, `Examples/python/parse_premiere_fcpxml.py`). `confidence: medium`.
- **For AME completion tracking**, run an ExtendScript event binder inside a CEP panel or injected `.jsx`, writing status to a temp JSON file Python polls. `confidence: medium`.
- **For server/batch on Windows**, COM `DoScript` with a dedicated launcher `.bat` that starts Premiere detached (`pymiere.exe_utils.start_premiere(use_bat=True)`). Still requires interactive desktop session — not cloud headless. `confidence: low`.
- **For effects/transitions/razor**, use QE via `pymiere.objects.qe` accepting crash risk, or pre-render operations into `.jsx` executed in ExtendScript only. `confidence: low`.

## Migration

| Current pattern | UXP target (25.6+) |
|---|---|
| pymiere Python → HTTP → CEP → evalScript | Python → Cursor SDK / external orchestrator → UXP plugin or UXP Scripting `.js` |
| COM / AppleScript `DoScript` | UXP Scripting entry point (single JS runtime, no bridge) |
| BridgeTalk to AME | UXP Encoder API + `Preset` object |
| `pymiere.wrappers.time_from_seconds` | `TickTime.createWithSeconds()` / `TickTime.TICKS_PER_SECOND` |
| `pymiere.objects.qe` | No UXP equivalent — gap; file feature requests |

Concrete steps:
1. Inventory every ExtendScript call your Python pipeline makes.
2. Mark each against UXP reference — several MOGRT/QE operations have **no UXP parity yet**.
3. Keep `.jsx` host functions as the source of truth until UXP catches up; swap transport only.
4. Plan migration before **2026-09** ExtendScript EOL.

## Cross-References
- `extendscript-core` — ES3 rules, json2.js, ticks, evalScript error envelopes
- `cep` — how Pymiere Link (a CEP panel) loads and debugs
- `export-rendering-media-encoder` — AME queue, HEVC block, BridgeTalk status checks
- `essential-graphics-mogrt-text` — MOGRT Source Text JSON from pymiere
- `reverse-engineering-qe-dom` — `pymiere.objects.qe` capabilities and crash risk
- `xml-fcpxml` — FCP7 XML export/import as a read-back channel
- `ai-integration` — agent/MCP patterns that also require GUI Premiere
- `Examples/extendscript/batch-export-guarded.jsx` — guarded AME batch (ExtendScript)
- `Examples/python/parse_premiere_fcpxml.py` — parse XML exported via pymiere

## Sources
- pymiere repository: https://github.com/qmasingarbe/pymiere
- pymiere PyPI: https://pypi.org/project/pymiere/
- pymiere examples: https://github.com/qmasingarbe/pymiere/blob/master/example_and_documentation.md
- pymiere Qt demo UI: https://github.com/qmasingarbe/pymiere/blob/master/demo_ui.py
- BridgeTalk reference: https://extendscript.docsforadobe.dev/extendscript-tools/bridgetalk.html
- Premiere Scripting Guide: https://ppro-scripting.docsforadobe.dev/
