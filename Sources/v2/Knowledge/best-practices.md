---
id: best-practices
title: Best Practices (Production)
category: meta
status: current
stability: active
doc_status: complete
introduced: null
deprecated: null
eol: null
min_premiere_version: null
api_namespace: none
languages: [extendscript, javascript, typescript]
tags: [best-practices, error-handling, version-aware, validation, utf-8, non-destructive]
related: [extendscript-core, essential-graphics-mogrt-text, export-rendering-media-encoder, uxp, 00-technology-status-matrix, premiere-dom-overview, captions]
supersedes: []
superseded_by: []
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://ppro-scripting.docsforadobe.dev/
  - https://developer.adobe.com/premiere-pro/uxp/
---

# Best Practices (Production)

> Cross-cutting rules every generated script, panel, and agent answer must follow. These encode the
> PKC (Premiere Knowledge Corpus) safety model: validate before mutate, preserve serialized data,
> distinguish object scopes, and never invent APIs.

## TL;DR
- **Validate the whole chain** before any mutation: project → sequence → track → clip → component → property → JSON parse → setValue.
- **Never invent API methods.** If it is not in the Knowledge docs or official reference, it does not exist.
- **Distinguish object scopes:** ProjectItem (project panel) ≠ TrackItem (timeline instance) ≠ MOGRT file ≠ MOGRT instance.
- **Sequence does not own media** — relink and path changes happen on ProjectItem.
- **Caption and MOGRT text are serialized JSON** — preserve unknown fields; never regenerate from plain text.
- **Backup or duplicate** before batch/destructive timeline edits.
- **Version-gate** every version-dependent behavior (Time objects, color ranges, HEVC block, fontTextRunLength).
- **UTF-8 everywhere** for non-ASCII text (Cyrillic, CJK, emoji).

## Status & Lifecycle
- `current` guidance applicable across ExtendScript, CEP, UXP, and Python interop.
- ExtendScript-specific rules remain valid through **EOL 2026-09**; UXP rules apply from **25.6+**.
- See `00-technology-status-matrix` for technology selection.

## PKC Agent Rules (mandatory)

These rules originate from the PKC specification (`Archive/pkc-legacy/spec_src/rules/`). Every agent
and code generator must enforce them.

| Rule ID | Rule | Severity |
|---|---|---|
| **RULE-AI-0001** | **No fake APIs.** Do NOT invent methods like `sequence.captions`, `project.exportCaptions()`, `trackItem.setText()`, or any member not in the official DOM. | critical |
| **RULE-AI-0002** | **Preserve object identity.** Do not equate objects by display name alone. Two clips named "Interview" are not the same object. | critical |
| **RULE-AI-0003** | **Declare API layer.** Every code answer must state whether it uses ExtendScript, UXP, CEP, QE, XML, Python, or hybrid. | error |
| **RULE-AI-0004** | **Do not port AE assumptions.** After Effects scripting patterns (layers, comps, `app.project.item()`) do not transfer to Premiere unless explicitly verified. | error |
| **RULE-AI-0005** | **Prefer official API before QE.** QE-dependent workflows are fallback/experimental only — flag risk to the user. | warning |
| **RULE-AI-0006** | **ProjectItem vs TrackItem.** Source-level changes (relink, rename in panel, metadata) target ProjectItem. Timeline edits (trim, move, effect values on instance) target TrackItem. | error |
| **RULE-AI-0007** | **Version-gate API usage.** Version-dependent code must include compatibility checks or explicit version notes. | error |
| **RULE-AI-0008** | **No silent destructive edits.** Batch timeline mutations require backup, duplicate sequence, XML export, or explicit rollback guidance. | error |
| **RULE-MOGRT-0001** | **MOGRT source vs instance.** The `.mogrt` file on disk ≠ the TrackItem on the timeline ≠ the ProjectItem in the bin. Text patching happens on the **timeline TrackItem's ComponentParam**. | error |
| **RULE-CAP-0001** | **Caption is not plain text.** Caption editing must preserve timing, style runs, metadata, and run lengths. | critical |
| **RULE-SER-0001** | **Preserve unknown fields.** Serializers must preserve unknown JSON/XML fields and ordering on round-trip. | critical |
| **RULE-SAFE-0001** | **Backup before destructive operations.** Production workflows must duplicate sequence or export XML before batch mutation. | critical |
| **RULE-EXT-0001** | **Do not promise ExtendScript future.** Treat ExtendScript as legacy/maintenance for new long-lived extensions. | warning |

### Object scope cheat sheet

```
.mogrt file on disk          → import via importMGT() / importFiles()
ProjectItem in bin          → project panel node; owns media path reference
TrackItem on timeline       → edit instance; owns components/properties
Component on TrackItem        → effect or MOGRT module
ComponentParam              → editable value (Source Text = JSON string)
Sequence                      → owns tracks/markers; does NOT own media files
ProjectItem.getMediaPath()    → relink here, NOT on TrackItem
```

**Sequence does not own source media.** Removing a clip from a timeline (`trackItem.remove`) does not
delete the source file or ProjectItem. Relink operations (`changeMediaPath`) affect the **ProjectItem**
and propagate to all timeline instances referencing it. Always report which instances will be affected
before relinking a shared ProjectItem.

## Architecture

This is a checklist doc — no runtime architecture. The validation chain mirrors the DOM hierarchy
documented in `premiere-dom-overview`:

```
app.project          ✓ exists?
  └─ activeSequence  ✓ exists?
       └─ videoTracks[vIdx] / audioTracks[aIdx]  ✓ index in range?
            └─ clips[i] (TrackItem)  ✓ found?
                 └─ components  ✓ has items?
                      └─ properties.getParamForDisplayName(name)  ✓ non-null?
                           └─ getValue()  ✓ non-empty?
                                └─ JSON.parse(raw)  ✓ valid JSON?
                                     └─ mutate known keys only
                                          └─ setValue(JSON.stringify(blob), true)  ✓ success?
```

## API Surface

N/A — this doc defines patterns, not API members. Refer to `premiere-dom-overview` for the object map.

## Working Examples

### 1. Validation chain helpers (ExtendScript)

```js
// ExtendScript (ES3) — Premiere 14.x+
// Reusable guards returning { ok:Boolean, err:String, ...refs }

function requireProject() {
    if (!app.project) { return { ok: false, err: "No project open." }; }
    return { ok: true, project: app.project };
}

function requireActiveSequence() {
    var r = requireProject();
    if (!r.ok) { return r; }
    var seq = r.project.activeSequence;
    if (!seq) { return { ok: false, err: "No active sequence." }; }
    return { ok: true, project: r.project, sequence: seq };
}

function requireVideoTrack(seq, trackIndex) {
    if (!seq || !seq.videoTracks) { return { ok: false, err: "No video tracks." }; }
    if (trackIndex < 0 || trackIndex >= seq.videoTracks.numTracks) {
        return { ok: false, err: "Video track index out of range: " + trackIndex +
            " (numTracks=" + seq.videoTracks.numTracks + ")" };
    }
    return { ok: true, track: seq.videoTracks[trackIndex] };
}

function requireClipOnTrack(track, clipName) {
    if (!track || !track.clips) { return { ok: false, err: "Track has no clips collection." }; }
    var clips = track.clips;
    for (var i = 0; i < clips.numItems; i++) {
        if (clips[i].name === clipName) {
            return { ok: true, trackItem: clips[i], index: i };
        }
    }
    return { ok: false, err: "Clip not found on track: " + clipName };
}

function requireMogrtParam(trackItem, paramDisplayName) {
    if (!trackItem) { return { ok: false, err: "No trackItem." }; }
    var comp = trackItem.getMGTComponent ? trackItem.getMGTComponent() : null;
    if (!comp) { return { ok: false, err: "TrackItem has no MGT component (not a MOGRT?)." }; }
    var name = paramDisplayName || "Source Text";
    var param = comp.properties.getParamForDisplayName(name)
             || comp.properties.getParamForDisplayName("Text");
    if (!param) { return { ok: false, err: "Param not found: " + name }; }
    var raw = param.getValue();
    if (raw == null || raw === "") { return { ok: false, err: "Param value is empty." }; }
    return { ok: true, component: comp, param: param, rawValue: raw };
}

function parseJsonSafe(raw, label) {
    label = label || "value";
    try {
        return { ok: true, data: JSON.parse(raw) };
    } catch (e) {
        return { ok: false, err: "JSON.parse failed on " + label + ": " + String(e) };
    }
}

// Compose the full chain:
function validateMogrtEditChain(clipName, vTrackIndex) {
    var r = requireActiveSequence();
    if (!r.ok) { return r; }
    r = requireVideoTrack(r.sequence, vTrackIndex);
    if (!r.ok) { return r; }
    r = requireClipOnTrack(r.track, clipName);
    if (!r.ok) { return r; }
    r = requireMogrtParam(r.trackItem, "Source Text");
    if (!r.ok) { return r; }
    r = parseJsonSafe(r.rawValue, "Source Text");
    if (!r.ok) { return r; }
    return { ok: true, trackItem: r.trackItem, param: r.param, blob: r.data };
}
```

### 2. Version-aware helpers

```js
// ExtendScript (ES3) — gate version-dependent behavior

function majorVersion() {
    return parseInt(String(app.version).split(".")[0], 10);
}

function requiresTimeObject() {
    // New-World scripting: Time objects mandatory from ~14.1
    var parts = String(app.version).split(".");
    var major = parseInt(parts[0], 10);
    var minor = parseInt(parts[1] || "0", 10);
    return (major > 14) || (major === 14 && minor >= 1);
}

function timeAtSeconds(s) {
    var t = new Time();
    t.seconds = s;
    return t;
}

function normalizeFillColor(r, g, b, a) {
    // fillColor in Source Text JSON: 0–255 on older, 0.0–1.0 on newer builds
    // Gate conservatively: treat 25+ as normalized floats
    if (majorVersion() >= 25) {
        return [r / 255, g / 255, b / 255, (a != null ? a : 255) / 255];
    }
    return [r, g, b, (a != null ? a : 255)];
}

function isHevcBlocked() {
    // HEVC programmatic export blocked since 25.5
    var parts = String(app.version).split(".");
    var major = parseInt(parts[0], 10);
    var minor = parseInt(parts[1] || "0", 10);
    return (major > 25) || (major === 25 && minor >= 5);
}

function updateMogrtTextSafe(trackItem, newText) {
    var r = requireMogrtParam(trackItem, "Source Text");
    if (!r.ok) { return r; }
    r = parseJsonSafe(r.rawValue, "Source Text");
    if (!r.ok) { return r; }
    var blob = r.data;
    blob.textEditValue = String(newText);
    blob.fontTextRunLength = [String(newText).length];   // MANDATORY — see essential-graphics-mogrt-text
    try {
        r.param.setValue(JSON.stringify(blob), true);
        return { ok: true, err: "" };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

### 3. Non-destructive backup before batch edits

```js
// ExtendScript (ES3) — duplicate active sequence before mutation

function backupActiveSequence(suffix) {
    suffix = suffix || "_BACKUP";
    var r = requireActiveSequence();
    if (!r.ok) { return r; }
    var seq = r.sequence;
    var originalName = seq.name;
    try {
        seq.clone();                                    // duplicates in project
        // After clone(), activeSequence may switch — find the clone by name pattern
        var proj = app.project;
        var backupName = originalName + suffix;
        for (var i = 0; i < proj.sequences.numSequences; i++) {
            if (proj.sequences[i].name === backupName ||
                proj.sequences[i].name.indexOf(originalName + suffix) === 0) {
                return { ok: true, backupSequence: proj.sequences[i], originalName: originalName };
            }
        }
        return { ok: true, err: "clone() succeeded but backup sequence name not confirmed — verify manually" };
    } catch (e) {
        return { ok: false, err: "clone() failed: " + String(e) };
    }
}

function exportSequenceXmlBackup(seq, folderPath) {
    if (!seq) { return { ok: false, err: "No sequence." }; }
    var f = new File(folderPath + "/" + seq.name.replace(/[^\w\-]/g, "_") + ".xml");
    try {
        var ok = seq.exportAsFinalCutProXML(f.fsName);
        return ok ? { ok: true, path: f.fsName } : { ok: false, err: "exportAsFinalCutProXML returned false" };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

### 4. UTF-8 file I/O (Cyrillic, CJK, emoji)

```js
// ExtendScript (ES3) — always set encoding BEFORE open

function readUtf8(path) {
    var f = new File(path);
    f.encoding = "UTF-8";
    if (!f.open("r")) { return { ok: false, err: "Cannot open: " + path }; }
    var text = f.read();
    f.close();
    return { ok: true, text: text };
}

function writeUtf8(path, text) {
    var f = new File(path);
    f.encoding = "UTF-8";
    f.lineFeed = "Unix";
    if (!f.open("w")) { return { ok: false, err: "Cannot write: " + path }; }
    f.write(text);
    f.close();
    return { ok: true };
}

// MOGRT text with non-ASCII: set via JSON blob — the string itself is UTF-8 safe
// if the .jsx source file is saved as UTF-8 and json2.js handles unicode escapes.
```

### 5. CEP return envelope (mandatory for panels)

```js
// ExtendScript (ES3) — host-side pattern for CEP evalScript
//@include "json2.js"
function hostOp(argsJson) {
    try {
        var args = JSON.parse(argsJson);
        // ... validated operation ...
        return JSON.stringify({ ok: true, result: {} });
    } catch (e) {
        return JSON.stringify({ ok: false, err: String(e) });
    }
}
```

```js
// CEP client — always parse defensively
cs.evalScript('hostOp(' + JSON.stringify(JSON.stringify(args)) + ')', (raw) => {
    let res;
    try { res = JSON.parse(raw); }
    catch { res = { ok: false, err: "Bad host return: " + raw }; }
    if (!res.ok) { console.error(res.err); return; }
    // use res.result
});
```

### 6. UXP transaction wrapper

```js
// UXP — Premiere 25.6+
const ppro = require('premierepro');

async function mutateSafely(undoLabel, actionFn) {
    const project = await ppro.Project.getActiveProject();
    if (!project) { throw new Error("No project open."); }
    await project.executeTransaction(async (compoundAction) => {
        await actionFn(compoundAction);
    }, undoLabel || "Script edit");
}
```

## Limitations

These are process limits, not API limits:
- Validation helpers cannot catch every stale reference — re-fetch from `app.project` between long batches.
- `clone()` naming is version-dependent — verify the backup sequence exists before proceeding.
- Version gates based on `app.version` string parsing can fail on beta builds — test on target.
- UTF-8 in ExtendScript depends on the script file being saved as UTF-8 **and** `f.encoding = "UTF-8"` on File I/O.

## Common Errors & Gotchas

### Version-aware musts

| Behavior | Version gate | Rule |
|---|---|---|
| `start`/`end`/`inPoint`/`outPoint` | 14.1+ | Pass `Time` objects, not raw numbers |
| `fillColor` in Source Text JSON | ~25+ | 0.0–1.0 floats; older builds use 0–255 |
| `fontTextRunLength` | all MOGRT versions | MUST equal `[newText.length]` after any text change |
| HEVC/H.265 via `app.encoder` | **25.5+** | **Blocked by design** — use H.264 or manual AME |
| ExtendScript EOL | **2026-09** | New work → UXP (25.6+) |
| CEP 12 | 25.0+ | Last runtime — build UXP in parallel |
| MOGRT text via UXP | 25.6+ | **No parity yet** — ExtendScript/CEP for text injection |
| Source Text caching bug | various | Force render or panel refresh after `setValue(..., true)` |

### Object confusion traps

- **Symptom:** MOGRT text won't update. **Cause:** calling `getValue`/`setValue` on ProjectItem instead of timeline TrackItem. **Fix:** locate the TrackItem after `importMGT`.
- **Symptom:** relink breaks unrelated sequences. **Cause:** relinking a shared ProjectItem without checking all referencing TrackItems. **Fix:** enumerate instances first; require user review.
- **Symptom:** caption styling lost after edit. **Cause:** replacing caption JSON with plain text. **Fix:** parse, mutate minimal keys, preserve unknown fields (`captions`, `SER-0002`).
- **Symptom:** `JSON is undefined`. **Cause:** ambient global JSON (unreliable). **Fix:** bundle json2.js.

### Runtime discipline

- **ExtendScript = ES3:** no `let`/`const`, arrows, template literals, native `JSON`.
- **UXP = async:** `await` every DOM method; wrap mutations in `executeTransaction`.
- **Collections:** `.numItems` + `[i]` — never `.forEach` or `.length`.
- **Label code blocks:** `// ExtendScript (ES3) — Premiere 25.x` or `// UXP — Premiere 25.6+`.

## Workarounds

| Problem | Workaround | Confidence |
|---|---|---|
| MOGRT text cache stale after setValue | Force sequence render or toggle panel focus | medium |
| Need MOGRT text on UXP | Dual-build: ExtendScript fallback for <25.6 and text ops | high |
| Batch edit with no undo safety | `clone()` + XML export before loop | high |
| Non-ASCII in generated .jsx | UTF-8 File I/O + UTF-8 script source | high |
| Unknown caption/MOGRT JSON keys | Round-trip: parse → mutate known keys only → stringify | high |

## Migration

- **New extensions (2026+):** default to UXP. Keep ExtendScript/CEP fallback only while install base includes <25.6.
- **Validation helpers:** port guards to async (`await project.getActiveSequence()`); keep the same chain logic.
- **JSON:** drop json2.js in UXP; keep it in ExtendScript forever.
- **Transactions:** every UXP mutation needs `executeTransaction` with a human-readable undo string.
- **PKC rules apply unchanged** across runtimes — object scopes and serialization rules are runtime-agnostic.

## Cross-References
- `premiere-dom-overview` — full object tree and collection patterns
- `extendscript-core` — ES3 runtime, json2, CEP bridge, UTF-8
- `essential-graphics-mogrt-text` — Source Text JSON, fontTextRunLength, color normalization
- `captions` — caption serialization constraints
- `export-rendering-media-encoder` — HEVC guard, AME availability
- `sequences-tracks-trackitems` — ProjectItem vs TrackItem, Time objects
- `uxp` — executeTransaction, async patterns
- `00-technology-status-matrix` — version/EOL authority
- `examples-index` → `Examples/` — runnable guarded samples

## Sources
- Premiere Pro Scripting Guide: https://ppro-scripting.docsforadobe.dev/
- UXP Premiere Pro docs: https://developer.adobe.com/premiere-pro/uxp/
- PKC rules (archived): `Archive/pkc-legacy/spec_src/rules/`
