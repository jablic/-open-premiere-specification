---
id: essential-graphics-mogrt-text
title: Essential Graphics, MOGRT, Text & Fonts
category: data-format
status: mixed
stability: unstable
doc_status: complete
introduced: "Essential Graphics ~Premiere 2017; MOGRT scripting ~2018; empty graphic layers 2020+"
deprecated: "Legacy Titles deprecated / not scriptable"
eol: null
min_premiere_version: null
api_namespace: app
languages: [extendscript, javascript-es3, json]
tags: [essential-graphics, mogrt, source-text, fontTextRunLength, fonts, text, justification, fillColor, importMGT, getMGTComponent, caching-bug, legacy-titles]
related: [extendscript-core, sequences-tracks-trackitems, reverse-engineering-qe-dom, captions, xml-fcpxml, uxp, automation]
supersedes: []
superseded_by: []
sources:
  - https://ppro-scripting.docsforadobe.dev/
  - https://community.adobe.com/t5/premiere-pro-discussions/extendscript-modifying-mogrt-text-using-cep-panel/td-p/11186245
  - https://community.adobe.com/t5/premiere-pro-discussions/programmatically-change-a-motion-graphics-text-font-size/m-p/12205513
  - https://community.adobe.com/t5/premiere-pro-discussions/premiere-pro-extendscript-changing-the-text-of-a-mogrt/m-p/14788591
  - https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
---

# Essential Graphics, MOGRT, Text & Fonts

> The most common — and most fragile — production automation in Premiere. **There is no API to
> create a text layer from scratch.** Author a `.mogrt` in After Effects, import it, and patch the
> Source Text JSON blob. Get `fontTextRunLength` wrong and text renders blank or half-styled.

## TL;DR
- **No from-scratch title API** (ExtendScript or UXP). Workflow = author `.mogrt` → `importMGT()` → patch JSON.
- **Source Text is a JSON string**: `getValue()` → `JSON.parse` → mutate → `setValue(JSON.stringify(obj), true)`.
- **`fontTextRunLength` MUST equal `[newText.length]`** whenever the text changes, or styling corrupts/blanks.
- **Four distinct, never-interchangeable types:** Essential Graphics, MOGRT, **Legacy Titles (NOT scriptable)**, Captions.
- **MOGRT must be authored in After Effects** with **"Allow font/style editing"** checked, or font/style fields silently no-op.
- **Color RGBA normalization differs by version** (0–255 vs 0.0–1.0). **HEVC export of these is unrelated** — see `export-rendering-media-encoder`.

## Status & Lifecycle
- **Essential Graphics panel** arrived ~Premiere 2017; **MOGRT scripting** (`importMGT`, Source Text JSON) ~2018.
- **Empty graphic layer** creation in the DOM exists from **Premiere 2020+**, but practical text
  authoring from scratch remains unreliable — the import-a-MOGRT pattern is the supported route.
- **Legacy Titles:** `deprecated`, removed from the modern UI, and **not programmatically editable**. Do not target them.
- **UXP parity:** as of 25.6, UXP does **not** expose MOGRT text-blob manipulation at parity with
  ExtendScript. Text-injection tooling still lives on ExtendScript/CEP for now (see `uxp` gaps).

## Architecture
```
ProjectItem (.mogrt asset)
   └─ importMGT(path, time, vTrackIndex, aTrackIndex)  ──► TrackItem on timeline
         └─ components[]            (Component, has .matchName e.g. "AE.ADBE Text")
               └─ properties[]      (ComponentParam, has .displayName e.g. "Source Text"/"Text")
                     └─ getValue()  ──► JSON STRING  (the "Source Text" blob)
```
- The **blob** is the contract. Its keys depend on what the AE author exposed to Essential Properties
  and on the AE renderer. Treat unknown keys as opaque — **preserve them**, never drop them.
- To apply an **effect** to a MOGRT's own controls you must use the **QE** track item, not the
  app-DOM one (see `reverse-engineering-qe-dom`).

## API Surface

### Placement / lookup
| Call | Returns | Notes |
|---|---|---|
| `sequence.importMGT(path, time, vTrackIndex, aTrackIndex)` | `TrackItem` | `path` absolute; `time` a `Time` object/seconds per version; indices 0-based |
| `sequence.importMGTFromLibrary(libraryName, mgtName, time, vIdx, aIdx)` | `TrackItem` | from a CC Library |
| `trackItem.getMGTComponent()` | `Component` / null | convenience accessor for the MOGRT's text/controls component |
| `component.properties.getParamForDisplayName(name)` | `ComponentParam` | preferred over manual iteration |
| `param.getValue()` / `param.setValue(value, updateUI)` | string / void | pass `updateUI = true` to force panel refresh |

### Source Text JSON blob — known keys
| Key | Type | Meaning / rule |
|---|---|---|
| `textEditValue` | string | The visible text string |
| **`fontTextRunLength`** | number[] | **MUST be `[textEditValue.length]`** after any text change. Drives which run the styling applies to |
| `fontEditValue` | string[] | PostScript font name(s), e.g. `["Subscribe-Regular"]` |
| `fontSizeEditValue` | number[] | Point size(s). **Setting this can hard-crash Premiere in some builds — test carefully** |
| `fontFSBoldValue` / `fontFSItalicValue` | bool[] | Faux/real bold/italic flags |
| `fontFSAllCapsValue` / `fontFSSmallCapsValue` | bool[] | Caps flags |
| `capPropTextRunCount` | number | Run count metadata (keep consistent with run arrays) |
| `capPropFontEdit` | bool | Whether font editing is permitted on this run |
| fill color | number[] | RGBA `[r,g,b,a]` — **0–255 on older, 0.0–1.0 on newer builds** (version-gate) |
| justification | number | `0 = left`, `1 = right`, `2 = center` |

> Captured real blob shape (illustrative):
> `{"capPropFontEdit":true,"fontEditValue":["Subscribe-Regular"],"fontSizeEditValue":[104],`
> `"fontTextRunLength":[14],"textEditValue":"easy to adjust"}`

## Working Examples

### 1. Production-safe text + font update (the canonical pattern)
```js
// ExtendScript (ES3) — Premiere 14.x+   (bundle json2.js)
//@include "json2.js"

// Returns { ok:Boolean, err:String } so a CEP/UXP caller can branch.
function updateMogrtText(trackItem, newText, opts) {
    opts = opts || {};
    try {
        if (!trackItem) { return { ok: false, err: "No trackItem" }; }

        var comp = trackItem.getMGTComponent ? trackItem.getMGTComponent() : null;
        if (!comp) { return { ok: false, err: "Not an AE-authored MOGRT / no MGT component" }; }

        // Display name varies: "Source Text", "Text", or a custom Essential Property name.
        var param = comp.properties.getParamForDisplayName("Source Text")
                 || comp.properties.getParamForDisplayName("Text");
        if (!param) { return { ok: false, err: "Source Text param not exposed" }; }

        var raw = param.getValue();
        if (raw == null || raw === "") { return { ok: false, err: "Empty Source Text value" }; }

        var blob;
        try { blob = JSON.parse(raw); }
        catch (e) { return { ok: false, err: "Source Text not JSON (Premiere-authored graphic?): " + String(e) }; }

        // --- mutate ---
        blob.textEditValue = String(newText);
        blob.fontTextRunLength = [String(newText).length];   // <-- THE mandatory line

        if (opts.fontPostScriptName) { blob.fontEditValue = [String(opts.fontPostScriptName)]; }
        // fontSizeEditValue is risky on some builds — only set if explicitly requested.
        if (typeof opts.fontSize === "number") { blob.fontSizeEditValue = [opts.fontSize]; }

        // --- serialize + apply (true => refresh UI/panel) ---
        param.setValue(JSON.stringify(blob), true);
        return { ok: true, err: "" };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

### 2. Import a MOGRT then set its text
```js
// ExtendScript (ES3) — Premiere 14.x+
function placeLowerThird(mogrtPath, atSeconds, vTrackIndex, text) {
    var seq = app.project && app.project.activeSequence;
    if (!seq) { return { ok: false, err: "No active sequence" }; }

    var t = new Time();
    t.seconds = atSeconds;                       // New-World scripting wants Time objects

    // Windows path gotcha: importMGT has historically needed escaped/normalized separators.
    var item = seq.importMGT(mogrtPath, t.ticks, vTrackIndex, 0);
    if (!item) { return { ok: false, err: "importMGT returned null (bad path / unsupported MOGRT)" }; }

    return updateMogrtText(item, text, {});
}
```

### 3. Version-correct fill color
```js
// ExtendScript (ES3)
// Newer Premiere expects normalized 0..1; older expects 0..255. Gate on major version.
function rgbaForVersion(r255, g255, b255, a255) {
    var major = parseInt(app.version.split(".")[0], 10);
    if (major >= 24) { // normalized era (verify per project)
        return [r255/255, g255/255, b255/255, (a255==null?255:a255)/255];
    }
    return [r255, g255, b255, (a255==null?255:a255)];
}
```

## Limitations
- **No from-scratch creation API** for Essential Graphics text or Legacy Titles. Import a MOGRT.
- **Legacy Titles are not scriptable at all** — neither read nor write of their text.
- **Premiere-authored graphics** (made in the EGL panel, not AE) typically expose only Opacity/Motion;
  their text param's `getValue()` may return a single non-ASCII char — the known "unsupported" case.
- **AE author controls availability:** if "Allow font/style editing" was unchecked in AE, font/size/style
  fields will not apply no matter what you write to the blob.
- **Target-workstation fonts are a hard dependency** — a font named in `fontEditValue` that isn't
  installed falls back or renders blank.

## Common Errors & Gotchas
- **Symptom:** text updates but Program Monitor doesn't change (only Essential Graphics/Effect Controls does).
  **Cause:** the **Source-Text caching bug**. **Fixes:** pass `true` to `setValue`; always update
  `fontTextRunLength`; nudge the clip (click off/on); render the timeline. (See history below.)
- **Symptom:** styling drops or only part of the string is styled. **Cause:** stale `fontTextRunLength`.
  **Fix:** set it to `[newText.length]` every time.
- **Symptom:** `getValue()` returns one weird character / not JSON. **Cause:** it's a Premiere-authored
  graphic or Legacy Title, not an AE MOGRT. **Fix:** detect and report; re-author as an AE MOGRT.
- **Symptom:** Premiere hard-crashes on edit. **Cause:** writing `fontSizeEditValue` on certain builds.
  **Fix:** avoid setting size via the blob unless verified on the user's version; resize in AE instead.
- **Symptom (2025):** MOGRT placed by script won't display on the timeline. **Cause:** AE renderer.
  **Fix:** re-author the .mogrt with AE's **Classic 3D** renderer (not Cinema 4D). `confidence: medium`.
- **Symptom (Windows):** `importMGT` fails/returns null with a valid-looking path. **Cause:** path
  separator handling. **Fix:** normalize/escape separators; use absolute paths.

### Source-Text caching bug — version history (Adobe bug #4221638)
Appeared **13.1** → fixed **13.1.x** → regressed **14.0.1** → fixed **14.2** → regressed again in
**2024/2025 (24.x/25.x)**. This recurs; assume it may be present and always apply the `setValue(...,true)`
+ `fontTextRunLength` + render workarounds. Track per-version when verifying.

## Workarounds
- **Force a render** to flush the cache: render the work area / sequence after `setValue`. `confidence: high`.
- **QE effect application:** to add an effect to the MOGRT's own controls, operate on the **QE** track
  item, not the app-DOM one. `confidence: low` (see `reverse-engineering-qe-dom`).
- **Read-only text from a project (no live edit):** parse an FCPXML/FCP7 export — but note Essential
  Graphics text is often Base64-buried and may be unrecoverable once flattened (see `xml-fcpxml`).

## Migration
- UXP exposes graphics/markers/transcripts but **not** MOGRT text-blob parity as of 25.6. Keep this
  workflow on ExtendScript/CEP until UXP closes the gap; isolate the blob-patching logic so only the
  transport layer changes later. File the gap on the Creative Cloud Developer Forums.

## Cross-References
- `extendscript-core` — ES3/json2.js, Time objects, validation patterns used above
- `sequences-tracks-trackitems` — locating tracks/clips/components; Time/ticks
- `reverse-engineering-qe-dom` — QE track item for effects on MOGRTs; matchName catalog (`AE.ADBE Text`)
- `xml-fcpxml` — extracting graphics text from exports (Base64 caveat)
- `captions` — distinct from graphics text; do not conflate
- `uxp` — current parity gaps for text/graphics

## Sources
- Premiere Pro Scripting Guide (importMGT, ComponentParam): https://ppro-scripting.docsforadobe.dev/
- Adobe community — modifying MOGRT text via CEP (Bruce Bullis): https://community.adobe.com/t5/premiere-pro-discussions/extendscript-modifying-mogrt-text-using-cep-panel/td-p/11186245
- Adobe community — programmatically change text/font size: https://community.adobe.com/t5/premiere-pro-discussions/programmatically-change-a-motion-graphics-text-font-size/m-p/12205513
- Adobe community — changing MOGRT text (fontTextRunLength): https://community.adobe.com/t5/premiere-pro-discussions/premiere-pro-extendscript-changing-the-text-of-a-mogrt/m-p/14788591
- Adobe-CEP PProPanel sample (.jsx patterns): https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
