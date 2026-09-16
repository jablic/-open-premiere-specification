---
id: export-rendering-media-encoder
title: Export, Rendering & Media Encoder
category: workflow
status: legacy
stability: frozen
doc_status: complete
introduced: "CC era"
deprecated: "API work stopped (2024)"
eol: "2026-09"
min_premiere_version: null
api_namespace: app
languages: [extendscript, javascript-es3]
tags: [export, encoder, media-encoder, ame, epr, preset, encodeSequence, encodeFile, encodeProjectItem, hevc, h265, batch, watch-folder, exportAsMediaDirect, bridgetalk]
related: [extendscript-core, sequences-tracks-trackitems, automation, uxp, 00-technology-status-matrix]
supersedes: []
superseded_by: [uxp]
sources:
  - https://ppro-scripting.docsforadobe.dev/
  - https://community.adobe.com/questions-729/premiere-25-5-0-app-encoder-export-methods-don-t-work-for-h265-presets-1419698
  - https://community.adobe.com/questions-729/cep-understanding-presets-in-the-encoder-object-1387923
  - https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
  - https://github.com/qmasingarbe/pymiere/blob/master/example_and_documentation.md
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
---

# Export, Rendering & Media Encoder

> One pipeline, two exits: render **inside Premiere** (`sequence.exportAsMediaDirect`) or queue jobs to
> **Adobe Media Encoder** (`app.encoder.encode*`, async). Presets are `.epr` XML files.
> **HEVC/H.265 via the encoder API is intentionally blocked since Premiere 25.5.**

## TL;DR
- **AME queue:** `app.encoder.encodeSequence / encodeFile / encodeProjectItem` → returns a **job-ID string** (or `"0"`/`0` on failure) and queues to AME.
- **Direct render (no AME):** `sequence.exportAsMediaDirect(outputPath, presetPath, workAreaType)`.
- **Presets are `.epr`** (XML). Bundle a curated set — system preset paths differ per machine/version.
- **CRITICAL — HEVC/H.265 blocked since 25.5, by design:** the `encode*` calls return a non-zero job id but **queue nothing** and throw no error. **H.264 works.** Render HEVC manually in AME or via an external encoder.
- **Detect AME** before queueing: `BridgeTalk.getStatus("ame")`. Encoder runs **asynchronously** — bind events in ExtendScript, not from Python.

## Status & Lifecycle
- **Status:** ExtendScript encoder API is `legacy/frozen`, EOL **2026-09**.
- **HEVC block:** introduced in **Premiere 25.5.0**. Adobe (Bruce Bullis): PPro and AME **specifically
  disallow programmatic H.265 generation**, and this is "unlikely to change." It worked through **24.6.8**;
  broke at 25.5 (this also forced HEVC encode tests out of third-party benchmarks).
- **Replacement:** UXP Encoder + `Preset` object API. See `00-technology-status-matrix`.

## Architecture

```
                         ┌───────────────────────────────┐
  Sequence / File /      │  app.encoder.encode*()         │   async, returns job-ID string
  ProjectItem  ─────────►│  (queues a job)                ├──────────────►  Adobe Media Encoder
                         └───────────────────────────────┘                 (separate app/process)
                                                                                  │
                         ┌───────────────────────────────┐                        ▼
  Sequence  ────────────►│ sequence.exportAsMediaDirect() │   renders INSIDE Premiere (no AME)
                         └───────────────────────────────┘   → output file written directly

  Preset (.epr XML)  ── selects format + settings for either path
```

- **AME path** is asynchronous and out-of-process: you queue, AME encodes, you (optionally) listen for events.
- **Direct path** keeps everything in Premiere — simpler for single renders, no AME dependency, but no AME queue features (watch folders, multiplexing AME presets, etc.).
- **Render-and-replace / smart rendering** are project/render-queue concepts; the renderer (Mercury GPU vs Software) is a project setting and is **not** meaningfully script-controllable.

## API Surface

### `app.encoder` — queue to AME
| Call | Signature | Returns |
|---|---|---|
| `encodeSequence` | `(sequence, outputPath, presetPath, workAreaType, removeOnCompletion)` | job-ID string / `0` |
| `encodeFile` | `(inputFilePath, outputPath, presetPath, removeOnCompletion, workAreaType[, sourceInPoint, sourceOutPoint])` | job-ID string / `0` |
| `encodeProjectItem` | `(projectItem, outputPath, presetPath, workAreaType, removeOnCompletion)` | job-ID string / `0` |
| `launchEncoder()` | — | launches AME if needed |
| `startBatch()` | — | starts processing the AME queue |
| `setSidecarXMPEnabled(0\|1)` | toggle sidecar XMP | |
| `setEmbeddedXMPEnabled(0\|1)` | toggle embedded XMP | |

> `removeOnCompletion`: remove the queued item from AME when done. Exact extra flags (e.g. whether AME
> renders immediately vs waits for `startBatch`) vary by version — **verify on the target build**. `confidence: medium`.

### `workAreaType` constants
| Constant | Meaning |
|---|---|
| `app.encoder.ENCODE_ENTIRE` | whole sequence/clip |
| `app.encoder.ENCODE_IN_TO_OUT` | sequence in/out points |
| `app.encoder.ENCODE_WORK_AREA` | work-area bar |

### Encoder events (bind in ExtendScript)
`app.encoder.bind(eventName, handlerFn)` with events:
`"onEncoderJobQueued"`, `"onEncoderJobComplete"`, `"onEncoderJobError"`, `"onEncoderJobProgress"`.
(Event names per the PProPanel sample; confirm on your version. `confidence: medium`.) From **Python/pymiere
you cannot bind to these** — AME is async and out-of-process; do event handling on the ExtendScript side.

### Direct render from a Sequence
| Call | Signature | Notes |
|---|---|---|
| `sequence.exportAsMediaDirect` | `(outputFilePath, presetPath, workAreaType)` | renders in Premiere, no AME |
| `sequence.getExportFileExtension` | `(presetPath)` | resolve container extension from a preset |

### Presets (`.epr`)
- XML files describing format + parameters. **System presets** ship on disk inside the AME/Premiere
  install (search for `*.epr`); **custom presets** are exported from the AME export dialog.
- Pass an **absolute path** to the `.epr`. Bundle the presets you depend on with your extension rather
  than hardcoding install paths (which differ across machines and versions).

### AME presence detection
- `BridgeTalk.getStatus("ame")` → `"ISNOTINSTALLED"` / `"ISNOTRUNNING"` / running.
- pymiere: `pymiere.wrappers.has_media_encoder()`.

## Working Examples

### 1. Queue an H.264 export to AME, with completion/error handling
```js
// ExtendScript (ES3) — Premiere 14.x+   (run AME availability check first; see Example 4)
function queueSequenceExport(outputPath, eprPath) {
    var seq = app.project && app.project.activeSequence;
    if (!seq) { return { ok: false, err: "No active sequence" }; }

    // Bind events BEFORE queueing so nothing is missed.
    try {
        app.encoder.bind("onEncoderJobComplete", function (jobID, outPath) {
            $.writeln("DONE " + jobID + " -> " + outPath);
        });
        app.encoder.bind("onEncoderJobError", function (jobID, errorMsg) {
            $.writeln("ERROR " + jobID + ": " + errorMsg);
        });
    } catch (eBind) { /* event names vary by version; degrade gracefully */ }

    app.encoder.launchEncoder();   // ensure AME is up

    // ENCODE_ENTIRE; removeOnCompletion = 1 (clear from queue when done).
    var jobID = app.encoder.encodeSequence(
        seq, outputPath, eprPath, app.encoder.ENCODE_ENTIRE, 1
    );

    if (jobID === 0 || jobID === "0" || !jobID) {
        return { ok: false, err: "Failed to queue (bad preset/path, or blocked codec — see HEVC note)" };
    }
    app.encoder.startBatch();      // begin processing
    return { ok: true, jobID: String(jobID) };
}
```

### 2. Direct render from Premiere (no AME dependency)
```js
// ExtendScript (ES3)
function renderDirect(outputPath, eprPath) {
    var seq = app.project && app.project.activeSequence;
    if (!seq) { return { ok: false, err: "No active sequence" }; }
    try {
        seq.exportAsMediaDirect(outputPath, eprPath, app.encoder.ENCODE_ENTIRE);
        return { ok: true };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

### 3. HEVC guard — refuse the blocked path early, with a clear message
```js
// ExtendScript (ES3)
// Heuristic: inspect the .epr (or its filename) for HEVC/H.265 before attempting to queue,
// because encodeSequence will silently no-op for HEVC on Premiere 25.5+.
function isLikelyHevcPreset(eprPath) {
    var f = new File(eprPath);
    if (!f.exists) { return false; }
    var name = decodeURI(f.name).toLowerCase();
    if (name.indexOf("hevc") !== -1 || name.indexOf("h265") !== -1 || name.indexOf("h.265") !== -1) {
        return true;
    }
    // Optional: open and scan the XML for HEVC GUIDs/strings.
    if (f.open("r")) { var s = f.read().toLowerCase(); f.close(); return s.indexOf("hevc") !== -1; }
    return false;
}

function guardedQueue(outputPath, eprPath) {
    var major = parseInt(app.version.split(".")[0], 10);
    var minor = parseInt(app.version.split(".")[1] || "0", 10);
    var hevcBlocked = (major > 25) || (major === 25 && minor >= 5);
    if (hevcBlocked && isLikelyHevcPreset(eprPath)) {
        return { ok: false, err: "HEVC programmatic export is blocked on Premiere 25.5+. " +
                                 "Use an H.264 preset, or render HEVC manually in AME." };
    }
    return queueSequenceExport(outputPath, eprPath);
}
```

### 4. Verify AME is available before queueing
```js
// ExtendScript (ES3)
function ameAvailable() {
    try {
        var status = BridgeTalk.getStatus("ame");   // "ISNOTINSTALLED" | "ISNOTRUNNING" | running
        if (status === "ISNOTINSTALLED") { return { ok: false, err: "Adobe Media Encoder not installed" }; }
        return { ok: true, status: String(status) };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

### 5. Batch-export every sequence in the project
```js
// ExtendScript (ES3)
function batchExportAllSequences(outDir, eprPath) {
    var results = [];
    var seqs = app.project.sequences;                // SequenceCollection
    for (var i = 0; i < seqs.numSequences; i++) {
        var seq = seqs[i];
        app.project.openSequence(seq.sequenceID);    // make active
        var active = app.project.activeSequence;
        var safeName = active.name.replace(/[^\w\-]+/g, "_");
        var outPath = outDir + "/" + safeName + active.getExportFileExtension(eprPath);
        var jobID = app.encoder.encodeSequence(active, outPath, eprPath, app.encoder.ENCODE_ENTIRE, 1);
        results.push({ name: active.name, queued: !(jobID === 0 || jobID === "0") });
    }
    app.encoder.startBatch();
    return results;
}
```

## Limitations
- **HEVC/H.265 programmatic export is disabled (25.5+)** and "unlikely to change." No flag re-enables it.
- **No event binding from Python/pymiere** — AME is async/out-of-process; bind on the ExtendScript side.
- **Renderer/GPU selection is not script-controllable** — it's a project setting.
- **Preset portability:** system `.epr` paths differ per machine/version — bundle your own.
- **Direct render lacks AME queue features** (watch folders, AME-side multiplexing).

## Common Errors & Gotchas
- **Symptom:** HEVC export does nothing; a non-zero job id is returned; no error thrown (25.5+).
  **Cause:** intentional codec block. **Fix:** use H.264 programmatically, or render HEVC manually in AME (Example 3).
- **Symptom:** `encode*` returns `0`/`"0"`. **Cause:** bad preset/output path, unsupported codec, or AME missing.
  **Fix:** validate `.epr` path + output dir; check `ameAvailable()` (Example 4).
- **Symptom:** export silently never starts. **Cause:** queued but `startBatch()` not called.
  **Fix:** call `app.encoder.startBatch()` after queueing.
- **Symptom:** events never fire. **Cause:** wrong event name for this version, or bound after queueing.
  **Fix:** bind before queueing; confirm event names on the target build.
- **Symptom:** Cyrillic filenames mangled in output path. **Cause:** encoding. **Fix:** ensure UTF-8 (see `extendscript-core`).

## Workarounds
- **HEVC output:** render H.264 then transcode with an external encoder (e.g. ffmpeg) post-export, or
  render HEVC manually in the AME UI. `confidence: high`.
- **Preset discovery:** ship a `/presets` folder with your extension and reference by relative→absolute
  path at runtime. `confidence: high`.
- **Progress from Python:** poll output-file size / AME log instead of binding events. `confidence: medium`.

## Migration
Target: UXP **Encoder** + **`Preset`** object API.
- `app.encoder.encode*` → UXP encoder methods (async — `await`).
- `.epr` selection → UXP `Preset` objects.
- Keep the HEVC guard regardless of runtime — the block is in PPro/AME, not the language layer.
- Isolate the transport so only the encoder calls change when porting. See `00-technology-status-matrix`.

## Cross-References
- `extendscript-core` — runtime, validation, UTF-8 path handling
- `sequences-tracks-trackitems` — the Sequence you export; `exportAsMediaDirect`, `getExportFileExtension`
- `automation` — pymiere export caveats (no event binding), `has_media_encoder()`
- `uxp` — the async encoder replacement
- `00-technology-status-matrix` — EOL + HEVC-block version authority

## Sources
- Premiere Pro Scripting Guide (Encoder, exportAsMediaDirect): https://ppro-scripting.docsforadobe.dev/
- Adobe community — H.265 encoder methods blocked in 25.5 (Bruce Bullis): https://community.adobe.com/questions-729/premiere-25-5-0-app-encoder-export-methods-don-t-work-for-h265-presets-1419698
- Adobe community — understanding presets in the Encoder object: https://community.adobe.com/questions-729/cep-understanding-presets-in-the-encoder-object-1387923
- Adobe-CEP PProPanel sample (encoder.bind patterns): https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
- pymiere (has_media_encoder, async caveat): https://github.com/qmasingarbe/pymiere/blob/master/example_and_documentation.md
