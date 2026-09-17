---
id: reverse-engineering-qe-dom
title: Reverse Engineering & the QE DOM
category: scripting
status: undocumented
stability: frozen
doc_status: complete
introduced: "Internal QA tool"
deprecated: "No work planned"
eol: null
min_premiere_version: null
api_namespace: qe
languages: [extendscript, javascript-es3]
tags: [qe-dom, undocumented, reverse-engineering, matchname, effects, ripple, speed, app.enableQE, reflect]
related: [extendscript-core, sequences-tracks-trackitems, essential-graphics-mogrt-text, automation, uxp, 00-technology-status-matrix]
supersedes: []
superseded_by: []
confidence: medium
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://ppro-scripting.docsforadobe.dev/application/application/#appenableqe
  - https://vakago-tools.com/premiere-pro-qe-api/
  - https://vakago-tools.com/extendscript-tutorial-adding-effect-to-a-clip-in-premiere-pro/
  - https://community.adobe.com/questions-529/match-name-for-source-text-property-30308
  - https://github.com/tmoroney/auto-subs
  - https://github.com/aenhancers/types-for-adobe-extras/blob/3bc960265b61830b07193b27d4e48304e9352542/Premiere/12.0/qeDom.d.ts
  - https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
---

# Reverse Engineering & the QE DOM

> **Undocumented, unsupported, frozen.** `app.enableQE()` unlocks the global `qe` object — Adobe's
> internal Quality-Engineering DOM. Last resort only; flag risk to the user. **Not available in UXP.**

## TL;DR
- Call **`app.enableQE()`** once per session → global **`qe`** (`qe.project`, `qe.source`, …).
- Parallel tree to the official `app` DOM with ops the documented API lacks: **effects by name**, **ripple/roll/slide/slip**, **clip speed/reverse**, **`exportFramePNG`**, **`newSequence(name, presetPath)`**, **`undo()`**.
- **Always operate on QE track items** (`qe.project.getActiveSequence().getVideoTrackAt(n).getItemAt(m)`), not `app.project.activeSequence` track items — they are different object types.
- Discover methods via **`qe.reflect.methods`** / **`qe.project.reflect.methods`** (or ExtendScript Developer Tools inspect).
- **No UXP port.** When ExtendScript EOLs (2026-09), QE-only workflows need Adobe to add UXP APIs or accept manual UI steps.

## Status & Lifecycle
- **Origin:** internal QA/automation surface; exposed to ExtendScript via `app.enableQE()` since at least CC era.
- **Official stance:** Adobe (Bruce Bullis, forums): **no additional work planned** on the unsupported, undocumented QE DOM. Treat as **frozen and brittle**.
- **`status: undocumented`** — works today on many builds, may break silently on the next release.
- **ExtendScript only** — UXP has no `enableQE()` equivalent (`uxp`).
- **Confidence:** `medium` for methods observed across community samples + `qeDom.d.ts` (Premiere 12.0 typings); re-verify on target build.

## Architecture

### Relationship to the official `app` DOM
```
app.enableQE()  ──►  global qe  (QEApplication)
                         │
                         ├── qe.project  (QEProject)     ← mirrors app.project
                         │      ├── getActiveSequence() → Sequence (QE)
                         │      ├── getVideoEffectByName(name)
                         │      ├── newSequence(name, presetPath)
                         │      └── undo() / redo()
                         │
                         ├── qe.source   (QESource)       ← Source Monitor
                         │      └── player (QEPlayer)
                         │
                         └── qe.reflect.methods           ← discovery

app.project.activeSequence  ──►  Sequence (app DOM)   ← DIFFERENT TYPE
                                      ≠ qe.project.getActiveSequence()
```

The **app DOM** and **QE DOM** describe the same edit, but objects are **not interchangeable**. You cannot pass an `app` TrackItem to `addVideoEffect()` — you must resolve the corresponding **QETrackItem**.

### Object tree (QE side)
```
qe.project (QEProject)
├── getActiveSequence() → Sequence (QE)
│   ├── CTI: Time { timecode, ticks, secs, frames }
│   ├── getVideoTrackAt(i) → Track
│   │   └── getItemAt(j) → QETrackItem
│   │         ├── addVideoEffect(VideoEffect)
│   │         ├── addTransition(...)
│   │         ├── rippleDelete()
│   │         ├── roll(offset, ...), slide(...), slip(...)
│   │         ├── setSpeed(factor, '', reverse, p3, ripple)
│   │         ├── setReverse(bool)
│   │         └── getComponentAt(k) → QEComponent { matchName, name }
│   ├── getAudioTrackAt(i) → Track
│   └── exportFramePNG(timecode, path)
├── getVideoEffectList() → string[]
├── getVideoTransitionList() → string[]
└── getBinAt(i) / getItemAt(i) → project panel items (QE view)
```

### Mapping app ↔ QE track items
There is **no official cross-reference API**. Production patterns:
1. **Index-based:** same `(trackIndex, itemIndex)` on both trees (fragile if gaps/empties differ).
2. **Name + time:** match `trackItem.name` + start ticks (collisions possible).
3. **Selection:** if the user selected the clip, read selection from app DOM, then locate in QE by scanning tracks.

> QE `getItemAt(i)` includes **Empty** gap items (`type === "Empty"`). Skip them when mirroring app clips.

## API Surface

### Bootstrap
| Call | Returns | Notes |
|---|---|---|
| `app.enableQE()` | `boolean` | Must call before any `qe.*` access. Idempotent in practice but re-call after major host events if refs go stale. |

### `qe.project` (QEProject) — selected members
| Method | Signature / returns | Purpose |
|---|---|---|
| `getActiveSequence()` | `Sequence` (QE) | Active sequence in QE tree |
| `getVideoEffectByName(name, matchName?)` | `VideoEffect` | **`true` 2nd arg** matches internal effect name (e.g. `'AE.ADBE Gaussian Blur 2'`) |
| `getVideoEffectList(type?, matchName?)` | `string[]` | All installed video effect names |
| `getVideoTransitionByName(name, ?)` | object | Transition lookup |
| `getVideoTransitionList(?)` | `string[]` | |
| `getAudioEffectByName(name, channelType?, ?)` | object | Audio effects |
| `getAudioEffectList(?)` | `string[]` | |
| `newSequence(name, presetPath)` | `boolean` | Create sequence from `.sqpreset` — **more reliable than documented app API** |
| `importFiles(paths, suppressUI, ?)` | `boolean` | QE-side import |
| `undo()` / `redo()` | `boolean` | QE undo stack (separate from app undo in some builds) |
| `save()` | `boolean` | |

### `QETrackItem` — edit operations missing from app DOM
| Method | Purpose | Notes |
|---|---|---|
| `addVideoEffect(effect)` | Apply effect to clip | `effect` from `getVideoEffectByName` |
| `addAudioEffect(effect)` | Audio effect | |
| `addTransition(transition, toStart, inDur?, offset?, align?, singleSided?, alignToVideo?)` | Add transition | |
| `rippleDelete()` | Ripple delete clip | |
| `roll(offset, ?, ?)` | Roll edit | Time string offset |
| `slide(offset, ?)` | Slide edit | |
| `slip(offset, ?)` | Slip edit | |
| `setSpeed(factor, '', isReversed, p3, ripple)` | Speed + optional reverse | `factor`: 1.0 = 100%; see Example 4 |
| `setReverse(bool)` | Reverse clip | |
| `setFrameBlend(bool)` | Frame blending | |
| `remove(ripple, alignToVideo)` | Delete (non-ripple option) | |
| `removeEffects(...)` | Remove effects | **Reported broken in some builds** |
| `getComponentAt(index)` | QE component | exposes `matchName` |
| `move(...)`, `moveToTrack(...)` | Move clip | |

**Avoid:** `startPercent` / `endPercent` properties on QETrackItem — documented in community typings as **crash Premiere**.

### `Sequence` (QE) — selected members
| Method | Purpose |
|---|---|
| `exportFramePNG(timecode, filePath)` | Export single frame — **async internally** (returns before file exists) |
| `exportFrameJPEG/TIFF/Targa/DPX(...)` | Other still formats |
| `CTI.timecode` | Current time indicator string |
| `addTracks(numVideo, videoIndex, numAudio, ...)` | Add tracks |
| `razor()`, `lift()`, `extract()` | Timeline ops |
| `renderPreview()`, `renderAll()` | Render |

### `exportFramePNG` contract
| Parameter | Type | Notes |
|---|---|---|
| `timecode` | `string` | Timecode (`'00:00:46:13'`) **or** frame number string (`'1117'`) |
| `filePath` | `string` | **`File.fsName`** — native path with platform separator; **include filename, no extension added automatically in all builds** |

**Not synchronous:** Adobe PProPanel sample + typings warn export frame functions return before the PNG is fully written. Poll for file existence or `$.sleep()`.

### Discovery via reflection
```js
// ExtendScript (ES3) — Premiere (any version with QE)
app.enableQE();

// Top-level QE methods (string listing — format varies by version)
if (qe.reflect && qe.reflect.methods) {
    $.writeln(qe.reflect.methods);
}

// Project-level methods
if (qe.project.reflect && qe.project.reflect.methods) {
    $.writeln(qe.project.reflect.methods);
}
```

**Better tooling:** Vakago **ExtendScript Developer Tools** v1.1.6+ inspects any ExtendScript object (including `qe`) with live method signatures. pymiere exposes QE via `pymiere.objects.qe` with an `inspect()` helper (`automation`).

### matchName catalog

`matchName` is the internal stable id for an effect/component (shared with After Effects). `displayName` is UI-facing and can change with locale. Use `matchName` for automation; use `displayName` for human debugging.

| matchName | displayName (typical) | Context | Notes |
|---|---|---|---|
| `AE.ADBE Text` | `Text` / `Source Text` | MOGRT / EG text layer | Source Text JSON lives under this component's properties |
| `AE.ADBE Gaussian Blur 2` | `Gaussian Blur` | Video effect | QE: `getVideoEffectByName('AE.ADBE Gaussian Blur 2', true)` |
| `ADBE Lumetri` | `Lumetri Color` | Video effect | Color grading |
| `ADBE Opacity` | `Opacity` | Intrinsic | |
| `ADBE Motion` | `Motion` | Intrinsic | Position/scale/rotation |
| `ADBE Crop` | `Crop` | Video effect | |
| `ADBE Drop Shadow` | `Drop Shadow` | Video effect | |
| `ADBE Fast Blur` | `Fast Blur` | Video effect | Legacy blur |
| `ADBE Dropdown Control` | `Dropdown Menu Control` | MOGRT control | Essential Property dropdown |
| `AE.ADBE Slider Control` | `Slider Control` | MOGRT control | |
| `AE.ADBE Checkbox Control` | `Checkbox Control` | MOGRT control | |
| `AE.ADBE Color Control` | `Color Control` | MOGRT control | |
| `AE.ADBE Point Control` | `Point Control` | MOGRT control | |

**Discovery on a live clip (app DOM):**
```js
// ExtendScript (ES3)
function listComponentMatchNames(trackItem) {
    var out = [];
    var comps = trackItem.components;
    for (var i = 0; i < comps.numItems; i++) {
        out.push({
            matchName: comps[i].matchName,
            displayName: comps[i].displayName
        });
    }
    return out;
}
```

**After Effects helper:** run `rd_GimmePropPath` (redef.com) on a layer to print matchNames for every property.

**Community catalogs:** [vakago-tools.com QE API](https://vakago-tools.com/premiere-pro-qe-api/), [ppro.api](https://vidjuheffex.github.io/ppro.api/) — verify against your installed effect list via `getVideoEffectList()`.

## Working Examples

### 1. Safe QE bootstrap module (isolate all QE usage)
```js
// ExtendScript (ES3) — Premiere 14.x+
// Keep every QE call behind this module so it can be disabled per version.

var QEDOM = (function () {
    var enabled = false;

    function ensureEnabled() {
        if (enabled) { return true; }
        if (typeof app.enableQE !== 'function') {
            return false;
        }
        enabled = !!app.enableQE();
        return enabled;
    }

    function getQEProject() {
        if (!ensureEnabled()) { return null; }
        return qe.project;
    }

    function getActiveQESequence() {
        var proj = getQEProject();
        if (!proj) { return null; }
        return proj.getActiveSequence();
    }

    return {
        ensureEnabled: ensureEnabled,
        getQEProject: getQEProject,
        getActiveQESequence: getActiveQESequence
    };
})();
```

### 2. Apply video effect by name (canonical pattern)
```js
// ExtendScript (ES3) — Premiere 14.x+  (UNDOCUMENTED — version-fragile)

var BLUR_MATCH = 'AE.ADBE Gaussian Blur 2'; // use matchName with 2nd arg true

function applyEffectToClipByMatchName(vTrackIndex, itemIndex, effectMatchName) {
    if (!QEDOM.ensureEnabled()) {
        return { ok: false, err: 'QE DOM not available' };
    }

    var qeSeq = QEDOM.getActiveQESequence();
    if (!qeSeq) { return { ok: false, err: 'No active QE sequence' }; }

    var effect = qe.project.getVideoEffectByName(effectMatchName, true);
    if (!effect) {
        return { ok: false, err: 'Effect not found: ' + effectMatchName };
    }

    var track = qeSeq.getVideoTrackAt(vTrackIndex);
    if (!track) { return { ok: false, err: 'No video track at index ' + vTrackIndex }; }

    var qeClip = track.getItemAt(itemIndex);
    if (!qeClip || qeClip.type === 'Empty') {
        return { ok: false, err: 'No clip at track ' + vTrackIndex + ' item ' + itemIndex };
    }

    var applied = qeClip.addVideoEffect(effect);
    return { ok: !!applied, err: applied ? '' : 'addVideoEffect returned false' };
}

// Usage: first non-empty clip on V1
var result = applyEffectToClipByMatchName(0, 0, BLUR_MATCH);
if (!result.ok) { $.writeln(result.err); }
```

### 3. Apply effect to a MOGRT (must use QE track item)
```js
// ExtendScript (ES3) — MOGRT on timeline
// The app-DOM trackItem accepts importMGT; effects on the MOGRT layer need the QE item.

function applyEffectToMogrtClip(appTrackItem, effectMatchName) {
    if (!QEDOM.ensureEnabled()) { return { ok: false, err: 'QE disabled' }; }

    // Resolve QE clip by scanning for matching name (simple strategy)
    var qeSeq = QEDOM.getActiveQESequence();
    if (!qeSeq) { return { ok: false, err: 'No QE sequence' }; }

    var targetName = appTrackItem.name;
    var qeClip = null;
    var vTracks = qeSeq.numVideoTracks;
    var t, i, item;

    for (t = 0; t < vTracks; t++) {
        var track = qeSeq.getVideoTrackAt(t);
        for (i = 0; i < track.numItems; i++) {
            item = track.getItemAt(i);
            if (item && item.type !== 'Empty' && item.name === targetName) {
                qeClip = item;
                break;
            }
        }
        if (qeClip) { break; }
    }

    if (!qeClip) { return { ok: false, err: 'QE clip not found for ' + targetName }; }

    var effect = qe.project.getVideoEffectByName(effectMatchName, true);
    if (!effect) { return { ok: false, err: 'Effect missing' }; }

    return { ok: !!qeClip.addVideoEffect(effect), err: '' };
}
```

See `essential-graphics-mogrt-text` for text blob editing (app DOM) vs effect application (QE DOM).

### 4. Set clip speed and reverse
```js
// ExtendScript (ES3) — UNDOCUMENTED
// setSpeed(speedFactor, unusedString, isReversed, p3, ripple)
// speedFactor: 1.0 = 100%, 0.5 = 50%, 2.0 = 200%

function setClipSpeed(vTrackIndex, itemIndex, speedFactor, reverse, ripple) {
    if (!QEDOM.ensureEnabled()) { return { ok: false, err: 'QE disabled' }; }

    var qeSeq = QEDOM.getActiveQESequence();
    if (!qeSeq) { return { ok: false, err: 'No sequence' }; }

    var qeClip = qeSeq.getVideoTrackAt(vTrackIndex).getItemAt(itemIndex);
    if (!qeClip || qeClip.type === 'Empty') {
        return { ok: false, err: 'Invalid clip' };
    }

    var ok = qeClip.setSpeed(
        speedFactor,
        '',
        !!reverse,
        true,   // p3 — observe on target build via reflect if behavior differs
        !!ripple
    );
    return { ok: !!ok, err: ok ? '' : 'setSpeed failed' };
}

// 150% speed, reversed, with ripple
var r = setClipSpeed(0, 1, 1.5, true, true);
```

Alternative: `qeClip.setReverse(true)` separately if `setSpeed` reverse flag misbehaves on your build.

### 5. Ripple delete via QE
```js
// ExtendScript (ES3) — UNDOCUMENTED
function rippleDeleteClip(vTrackIndex, itemIndex) {
    if (!QEDOM.ensureEnabled()) { return false; }

    var qeSeq = QEDOM.getActiveQESequence();
    if (!qeSeq) { return false; }

    var qeClip = qeSeq.getVideoTrackAt(vTrackIndex).getItemAt(itemIndex);
    if (!qeClip || qeClip.type === 'Empty') { return false; }

    return !!qeClip.rippleDelete();
}
```

For roll/slide/slip, the first argument is typically a **time offset string** in the sequence timebase — inspect with `qeClip.reflect.methods` on your build:
```js
// ExtendScript (ES3) — verify signature on target version before production use
// qeClip.roll('+00:00:02:00', false, false);
// qeClip.slide('-00:00:01:00', false);
// qeClip.slip('+00:00:00:12', false);
```

### 6. Export current frame as PNG (PProPanel pattern)
```js
// ExtendScript (ES3) — Premiere 14.x+  (UNDOCUMENTED)
// WARNING: exportFramePNG is NOT synchronous — wait for file after call.

function exportCurrentFramePng(outputFolderFsName) {
    if (!QEDOM.ensureEnabled()) { return { ok: false, err: 'QE disabled' }; }

    var qeSeq = QEDOM.getActiveQESequence();
    if (!qeSeq) { return { ok: false, err: 'No active sequence' }; }

    var timecode = qeSeq.CTI.timecode; // e.g. "00;00;12;15" — semicolons on some locales
    var sep = $.os.indexOf('Windows') >= 0 ? '\\' : '/';
    var outPath = outputFolderFsName + sep + 'frame_' + timecode.replace(/[;:]/g, '_') + '.png';

    qeSeq.exportFramePNG(timecode, outPath);

    // Poll for file (export is async internally)
    var f = new File(outPath);
    var attempts = 40;
    while (attempts-- > 0) {
        if (f.exists) { return { ok: true, path: outPath, err: '' }; }
        $.sleep(100);
    }
    return { ok: false, err: 'PNG not written within timeout: ' + outPath };
}
```

Adobe sample also exports by numeric frame string: `sequence.exportFramePNG('1117', path)`.

### 7. Create sequence from preset (QE-only reliability)
```js
// ExtendScript (ES3) — UNDOCUMENTED  (confidence: medium)
function createSequenceFromPresetQE(name, sqPresetPath) {
    if (!QEDOM.ensureEnabled()) { return false; }

    // sqPresetPath: absolute path to .sqpreset file
    var f = new File(sqPresetPath);
    if (!f.exists) { return false; }

    return !!qe.project.newSequence(name, f.fsName);
}
```

Prefer this over documented `app.project.newSequence()` / broken preset args when automation must match a known preset exactly.

### 8. Dump installed video effects (build effect map once)
```js
// ExtendScript (ES3)
function dumpVideoEffectsToLog() {
    if (!QEDOM.ensureEnabled()) { return; }
    var list = qe.project.getVideoEffectList();
    for (var i = 0; i < list.length; i++) {
        $.writeln(i + ': ' + list[i]);
    }
}
```

Run once per major Premiere version — effect names shift when Adobe renames or bundles Lumetri/etc.

## Limitations

- **Unsupported:** Adobe will not fix QE bugs or document signatures. No SLA, no forum support from engineering.
- **ExtendScript only:** no path from UXP (`uxp`). Plan for ExtendScript EOL **2026-09** (`00-technology-status-matrix`).
- **Version fragile:** method signatures, effect names, and behavior change between releases without notice.
- **Stale references:** `qe.project` and child objects go stale after project switch, close, or sometimes sequence activation — re-fetch every operation batch.
- **App/QE object mismatch:** passing app DOM objects into QE methods fails or corrupts state.
- **Empty track items:** QE indexes include `type === "Empty"` gaps — index parity with app DOM is not guaranteed.
- **`removeEffects` broken** on some builds (per community typings).
- **`startPercent` / `endPercent`** on QETrackItem crash Premiere — do not touch.
- **MOGRT text editing** is still app DOM (Source Text JSON) — QE is for effects on the MOGRT layer, not replacing text blob workflow.
- **Undo integration:** `qe.project.undo()` may not always align with Edit → Undo stack — test on target build.
- **exportFramePNG timing:** must poll/wait; no completion callback.
- **Locale/timecode:** `CTI.timecode` may use `;` vs `:` separators — normalize in filenames, pass original to export call.

## Common Errors & Gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `qe is undefined` | `enableQE()` not called or failed | Call `app.enableQE()` first; check return value |
| `addVideoEffect` silently fails | Used app TrackItem instead of QETrackItem | Resolve QE clip via `qe.project.getActiveSequence()...` |
| Effect not found | Wrong name; need matchName mode | `getVideoEffectByName(name, true)` with `AE.ADBE …` matchName |
| Wrong clip gets effect | Index includes Empty items | Skip `type === 'Empty'`; match by name/time |
| Stale QE sequence after project switch | Cached `qe.project` reference | Re-call `enableQE()` + re-fetch `qe.project` after `app.openDocument` / project close |
| `exportFramePNG` returns but no file | Async export | Poll `File.exists` + `$.sleep` |
| Premiere crash on QE call | Touched `startPercent`/`endPercent` or wrong arg count | Use reflect to verify signature; remove crash properties |
| Speed change wrong direction | `setSpeed` reverse flag vs `setReverse` | Try separate `setReverse(true)` |
| pymiere QE call no-op | QE not enabled in host session | Ensure host `.jsx` calls `enableQE()` first |
| Worked in 24.x, breaks in 25.x | Adobe changed internal QE surface | Version-gate QE module; maintain per-version effect maps |

## Workarounds

- **Isolate QE:** single module (Example 1) with `ensureEnabled()` — swap for no-op stubs when QE fails or version unsupported.
- **Prefer documented APIs first:** only drop to QE when the operation truly has no app/UXP path (see decision table below).
- **Version pin:** test automation against explicit Premiere builds; block unsupported versions in UI.
- **Effect map cache:** dump `getVideoEffectList()` per major version; map display names → matchNames for your pipeline.
- **exportFramePNG alternative:** render still via Media Encoder / FCPXML+external tool — heavier but supported paths (`export-rendering-media-encoder`).
- **Speed/ripple without QE:** no good documented alternative — manual edit or wait for UXP API.
- **Track Adobe UXP additions:** several QE ops may eventually land in UXP (`SequenceEditor` already covers insert/overwrite/remove) — re-check `uxp` each release.

### When to use QE vs documented API
| Need | Documented app DOM | UXP 25.6+ | QE DOM |
|---|---|---|---|
| Insert/overwrite clip | `insertClip` / `overwriteClip` | `SequenceEditor` actions | Overkill |
| Import media | `importFiles` | `project.importFiles` | Possible but unnecessary |
| MOGRT text JSON | `getValue`/`setValue` | **No parity** | **No** — stay app DOM |
| Effect by name | **No** | Partial (effect refs) | **Yes** |
| Clip speed / reverse | **No** | **No** | **Yes** |
| Ripple delete / trim tools | **No** | **No** | **Yes** |
| Export single frame PNG | **No** | **No** | **Yes** |
| Sequence from preset | Unreliable | `createSequenceWithPresetPath` | **Often more reliable** |
| Undo specific script action | **No** | `executeTransaction` | `qe.project.undo()` |

## Migration

- **No 1:1 UXP replacement** for most QE operations as of 25.6. UXP adds `SequenceEditor`, effects APIs, and converters but **not** QE parity for speed, ripple trim, or `exportFramePNG`.
- **ExtendScript EOL 2026-09:** QE-dependent tools must either (a) pressure Adobe for UXP APIs, (b) move ops to manual/UI-assisted workflow, or (c) accept breakage when ExtendScript is removed.
- **Track UXP changelog** each release — port QE call sites when an official API appears; delete QE fallback once verified.
- **Do not port QE to UXP** — it does not exist there. CEP panels that used QE via `evalScript` must keep an ExtendScript host until UXP covers the feature.

## Cross-References
- `extendscript-core` — ES3 runtime, `app.enableQE()` entry, validation patterns
- `sequences-tracks-trackitems` — app DOM hierarchy; Time/ticks; insert/overwrite
- `essential-graphics-mogrt-text` — Source Text JSON (app DOM) vs QE for MOGRT effects
- `uxp` — current platform; explicit QE gap
- `automation` — pymiere QE access (`pymiere.objects.qe`)
- `export-rendering-media-encoder` — supported export alternatives to `exportFramePNG`
- `00-technology-status-matrix` — QE status row, decision guide
- `debugging` — ExtendScript Developer Tools for QE inspect

## Sources
- https://ppro-scripting.docsforadobe.dev/application/application/#appenableqe
- https://vakago-tools.com/premiere-pro-qe-api/
- https://vakago-tools.com/extendscript-tutorial-adding-effect-to-a-clip-in-premiere-pro/
- https://community.adobe.com/questions-529/match-name-for-source-text-property-30308
- https://github.com/tmoroney/auto-subs
- https://github.com/aenhancers/types-for-adobe-extras/blob/3bc960265b61830b07193b27d4e48304e9352542/Premiere/12.0/qeDom.d.ts
- https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
