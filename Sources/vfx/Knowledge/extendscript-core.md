---
id: extendscript-core
title: ExtendScript Core
category: scripting
status: legacy
stability: frozen
doc_status: complete
introduced: "Adobe CC (pre-2015); New-World scripting changes ~Premiere 14.1 (2020)"
deprecated: "API work stopped (2024)"
eol: "2026-09"
min_premiere_version: null
api_namespace: app
languages: [extendscript, javascript-es3]
tags: [extendscript, es3, json2, jsx, scripting-core, bridgetalk, scriptui, evalscript, utf-8, ticks]
related: [cep, uxp, automation, debugging, best-practices, sequences-tracks-trackitems, reverse-engineering-qe-dom]
supersedes: []
superseded_by: [uxp]
sources:
  - https://ppro-scripting.docsforadobe.dev/
  - https://extendscript.docsforadobe.dev/
  - https://github.com/douglascrockford/JSON-js
  - https://github.com/aenhancers/Types-for-Adobe
  - https://github.com/qmasingarbe/pymiere
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
---

# ExtendScript Core

> The ECMAScript-3 scripting runtime that drives Premiere's automation DOM. Most capable backend
> available, but **frozen** and supported only **through September 2026**. New work → UXP (`uxp`).

## TL;DR
- **ES3 only.** No `let`/`const`, arrow functions, template literals, `Promise`, default params, or native `JSON`.
- **No native JSON** — bundle **json2.js**. The classic failure is `JSON is undefined`.
- **Single global entry point:** `app` (`app.project`, `app.project.activeSequence`, …). Synchronous.
- **Status: legacy/frozen, EOL 2026-09.** Use only for existing tooling and for users below Premiere 25.6.

## Status & Lifecycle
- **Introduced:** the ExtendScript dialect predates Creative Cloud; Premiere's scriptable DOM grew across CC releases.
- **New-World scripting** (~Premiere 14.1 / 2020) removed implicit type coercion and began requiring
  **`Time` objects** (not raw numbers) for properties like `start`/`end`. Code written for older
  versions that passed numbers will throw or silently misbehave on 14.1+.
- **Frozen:** Adobe stopped additional work on the ExtendScript API in 2024.
- **EOL:** supported **through September 2026** per the Scripting Guide (see `00-technology-status-matrix`).
- **Replacement:** UXP scripting + `premierepro` module. Migration is a rewrite, not a port.

## Architecture
- **Where it runs:** inside Premiere's embedded ExtendScript engine. One process, synchronous, single-threaded.
- **How it's invoked:**
  - From a **CEP panel** → `CSInterface.evalScript("hostFn(args)", callback)` (the recommended bridge; see `cep`).
  - From **another Adobe app** → `BridgeTalk` messages.
  - From **Python** → pymiere serializes calls over HTTP to a CEP helper that runs `evalScript` (see `automation`).
  - **UXP** can also run single-file `.js` scripts now (UXP Scripting), but that is the UXP runtime, not ExtendScript.
- **What it reaches:** the documented `app` DOM (project, sequences, tracks, items, components,
  encoder, metadata) plus the undocumented `qe` DOM after `app.enableQE()` (see `reverse-engineering-qe-dom`).

## API Surface

### Global objects and ExtendScript extensions
| Symbol | Purpose |
|---|---|
| `app` | Root of the Premiere DOM (the only host entry point) |
| `$` | ExtendScript engine object: `$.writeln()`, `$.write()`, `$.sleep(ms)`, `$.global`, `$.fileName`, `$.line`, `$.os` |
| `File`, `Folder` | Filesystem I/O (support `encoding` property; see UTF-8 below) |
| `BridgeTalk` | Inter-application messaging and host status checks |
| `ScriptUI` (`Window`, `Panel`, …) | Native script UI (rarely used now; CEP/UXP preferred for panels) |
| `XML`, `XMLList` | E4X XML support (available in ExtendScript, unlike browser JS) |
| `app.enableQE()` → `qe` | Enables the undocumented QE DOM (see `reverse-engineering-qe-dom`) |

### Version / environment detection
```js
// ExtendScript (ES3)
var v = app.version;        // e.g. "25.3.0" — string
var build = app.build;      // build string
var major = parseInt(app.version.split(".")[0], 10);  // 25
// $.os -> "Windows..." | "Macintosh..."   (platform branching)
```

### The ticks constant (time base)
Premiere's fundamental time unit is **ticks**: **254016000000 ticks per second** (confirmed by Adobe;
hard-coded in pymiere as `TICKS_PER_SECONDS = 254016000000`). `Time` objects expose `.ticks` and
`.seconds`. See `sequences-tracks-trackitems` for frame/second/tick conversion patterns.

## Working Examples

### 1. Robust JSON bootstrap (json2.js polyfill guard)
```js
// ExtendScript (ES3) — Premiere (any)
// The global JSON object is only present when the CC Libraries panel happens to be open,
// and is unreliable. Always bundle json2.js and include it before any JSON use.
//@include "json2.js"

if (typeof JSON === "undefined" || !JSON.parse) {
    throw new Error("json2.js not loaded — bundle Crockford's json2.js with the script.");
}
```

### 2. Safe access to the active sequence (validate everything)
```js
// ExtendScript (ES3) — Premiere 14.1+ (New-World scripting)
function getActiveSequenceSafe() {
    if (!app.project) { return { ok: false, err: "No project open." }; }
    var seq = app.project.activeSequence;
    if (!seq) { return { ok: false, err: "No active sequence." }; }
    return { ok: true, seq: seq };
}

var r = getActiveSequenceSafe();
if (!r.ok) { $.writeln(r.err); }
else { $.writeln("Sequence: " + r.seq.name); }
```

### 3. UTF-8 file write (Cyrillic-safe logging / .jsx generation)
```js
// ExtendScript (ES3)
function writeUtf8(path, text) {
    var f = new File(path);
    f.encoding = "UTF-8";          // MUST set before open; default is platform locale
    f.lineFeed = "Unix";
    if (!f.open("w")) { return false; }
    f.write(text);                  // text may contain Cyrillic; engine encodes per f.encoding
    f.close();
    return true;
}
// writeUtf8(Folder.temp.fsName + "/ppro_log.txt", "Кириллица OK — кадр 0123");
```

### 4. Iterating components/properties to find a parameter by display name
```js
// ExtendScript (ES3) — Premiere 14.x+
// Generic walk; prefer component.properties.getParamForDisplayName(name) when available.
function findParam(trackItem, displayName) {
    var comps = trackItem.components;
    for (var i = 0; i < comps.numItems; i++) {
        var comp = comps[i];                 // Component (has .matchName)
        var props = comp.properties;
        for (var j = 0; j < props.numItems; j++) {
            var p = props[j];                // ComponentParam (has .displayName)
            if (p.displayName === displayName) {
                return { component: comp, param: p };
            }
        }
    }
    return null;
}
```

### 5. CEP → ExtendScript call with serialized return + error envelope
```js
// --- HOST SIDE: host/index.jsx (ExtendScript, ES3) ---
//@include "json2.js"
function getSequenceInfo() {
    try {
        var seq = app.project && app.project.activeSequence;
        if (!seq) { return JSON.stringify({ ok: false, err: "No active sequence" }); }
        return JSON.stringify({
            ok: true,
            name: seq.name,
            videoTracks: seq.videoTracks.numTracks,
            audioTracks: seq.audioTracks.numTracks
        });
    } catch (e) {
        return JSON.stringify({ ok: false, err: String(e) });
    }
}
```
```js
// --- CLIENT SIDE: client/main.js (CEP, modern JS allowed) ---
const cs = new CSInterface();
cs.evalScript("getSequenceInfo()", (raw) => {
  // evalScript returns a STRING (or "EvalScript error.") — always parse defensively
  let res;
  try { res = JSON.parse(raw); } catch { res = { ok: false, err: "Bad host return: " + raw }; }
  if (!res.ok) { console.error(res.err); return; }
  console.log(res.name, res.videoTracks, res.audioTracks);
});
```

## Limitations
- **ES3 language ceiling.** Anything relying on ES5+/ES6 syntax fails to compile. Polyfill or rewrite.
- **No native JSON / typed arrays / fetch / modern stdlib.** Use `File`/`Folder`, `BridgeTalk`, json2.js.
- **Synchronous only.** Long operations block Premiere's UI thread; no async/await, no workers.
- **`EvalScript error.`** is all CEP gets back when a host exception escapes — wrap host fns in try/catch
  and return a JSON error envelope (Example 5), or you lose the actual error.
- **Frozen API.** No new capabilities will be added; gaps that exist now are permanent for ExtendScript.

## Common Errors & Gotchas
- **Symptom:** `JSON is undefined`. **Cause:** relying on the ambient global JSON. **Fix:** bundle json2.js (Example 1).
- **Symptom:** setting `clip.start`/`end` throws or no-ops. **Cause:** passing a number on 14.1+.
  **Fix:** pass a `Time` object (`var t = new Time(); t.seconds = 1.5;`). See `sequences-tracks-trackitems`.
- **Symptom:** Cyrillic shows as `??`/mojibake in logs or generated .jsx. **Cause:** file written in locale encoding.
  **Fix:** set `f.encoding = "UTF-8"` before `open` (Example 3); save the script file itself as UTF-8.
- **Symptom:** string concatenation produces `[object Object]`. **Cause:** New-World scripting removed
  implicit coercion. **Fix:** call `String(x)` / `.toString()` explicitly.
- **Symptom:** intermittent garbage from `evalScript`. **Cause:** returning non-strings or unescaped data.
  **Fix:** always `JSON.stringify` the host return; parse defensively client-side.

## Workarounds
- **Modern syntax desired:** author in **TypeScript** with **Types-for-Adobe** and transpile to ES3
  (Bolt CEP does this end-to-end with `evalTS()` type safety). `confidence: high`.
- **Need async-like behavior:** chunk work and yield with `$.sleep` between batches, or drive iteration
  from the CEP/UXP side calling many small host functions. `confidence: medium`.
- **Need capabilities ExtendScript lacks (effects-by-name, ripple, speed):** drop to the QE DOM
  (`app.enableQE()`), accepting undocumented/unsupported risk. See `reverse-engineering-qe-dom`. `confidence: low`.

## Migration
Target: **UXP scripting** (`uxp`). Key shifts:
- `app` (sync) → `require("premierepro")` DOM (mostly **async**, `await` methods; properties sync).
- json2.js → native JSON (UXP is a modern JS engine).
- `CSInterface.evalScript` bridge → direct in-runtime calls (no bridge).
- Mutations → wrap in `executeTransaction(cb, undoString)`.
- Verify each ExtendScript call you depend on has a UXP equivalent **now** — several do not yet (MOGRT
  text-blob parity, some QE-only ops). File gaps on the Creative Cloud Developer Forums.

## Cross-References
- `00-technology-status-matrix` — the EOL/version authority
- `cep` — how panels invoke this runtime (`evalScript` bridge, debugging, packaging)
- `uxp` — the migration target and its current gaps
- `sequences-tracks-trackitems` — the DOM this runtime drives; Time/ticks conversion
- `reverse-engineering-qe-dom` — `app.enableQE()` escape hatch
- `debugging` — VS Code ExtendScript Debugger, `$.writeln`, breakpoints
- `automation` — pymiere, BridgeTalk, command-line `.jsx`

## Sources
- Premiere Pro Scripting Guide: https://ppro-scripting.docsforadobe.dev/
- ExtendScript language reference: https://extendscript.docsforadobe.dev/
- json2.js (Crockford): https://github.com/douglascrockford/JSON-js
- Types-for-Adobe: https://github.com/aenhancers/Types-for-Adobe
- pymiere (ticks constant, DOM mirror): https://github.com/qmasingarbe/pymiere
