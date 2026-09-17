---
id: uxp
title: UXP (Unified Extensibility Platform)
category: ui-extensibility
status: current
stability: active
doc_status: complete
introduced: "GR in Premiere 25.6 (beta Dec 2024)"
deprecated: null
eol: null
min_premiere_version: 25.6
api_namespace: premierepro
languages: [javascript, typescript]
tags: [uxp, premierepro, manifest-v5, udt, spectrum, async, executeTransaction, hybrid-plugin, uxpaddon]
related: [extendscript-core, cep, cpp-native-sdk, panels, 00-technology-status-matrix, sequences-tracks-trackitems, essential-graphics-mogrt-text, reverse-engineering-qe-dom, debugging, import]
supersedes: [extendscript-core, cep]
superseded_by: []
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://developer.adobe.com/premiere-pro/uxp/
  - https://developer.adobe.com/premiere-pro/uxp/resources/fundamentals/apis/
  - https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
  - https://developer.adobe.com/premiere-pro/uxp/plugins/concepts/manifest/
  - https://developer.adobe.com/premiere-pro/uxp/plugins/hybrid-plugins/
  - https://github.com/AdobeDocs/uxp-premiere-pro-samples
  - https://hyperbrew.co/blog/uxp-plugins-in-premiere-2026/
---

# UXP (Unified Extensibility Platform)

> The **current** extensibility platform for Adobe Premiere (25.6+). One in-process JavaScript runtime
> for UI and host API access — no Chromium, no `CSInterface` bridge. DOM **methods are async**;
> wrap mutations in **`executeTransaction`**.

## TL;DR
- **General release in Premiere 25.6** (Dec 2025). Only **25.6+ / 2026** users can run UXP plugins.
- Entry point: `const ppro = require('premierepro')`. UXP Core: `require('uxp')`, `require('fs')`, `require('os')`.
- **All DOM methods return Promises** — use `await`. Property get/set remain **synchronous**.
- **Mutations** go inside `await project.executeTransaction((compoundAction) => { ... }, 'Undo label')`.
- **Incomplete surface:** no MOGRT Source Text JSON parity, no QE DOM, some panel/UI bugs. Native work → **Hybrid `.uxpaddon`** or C++ PrSDK.
- Adobe explicitly does **not** intend 1:1 CEP/ExtendScript parity — migration is a rewrite, not a port.

## Status & Lifecycle
- **Introduced:** UXP beta in Premiere Dec 2024; **GR in 25.6** (Adobe: "UXP has officially graduated from beta").
- **Bundled UXP v8.1** in Premiere 25.6. Each Premiere release pins a UXP version — check UDT or `require('uxp').versions.uxp` at runtime.
- **Replaces:** CEP panels + ExtendScript bridge (`cep`, `extendscript-core`). ExtendScript remains supported through **2026-09** for legacy users.
- **2026 rebrand:** "Premiere Pro" → "Premiere"; UXP requirement unchanged (25.6+).
- **Replacement for ExtendScript/CEP:** this doc. See `00-technology-status-matrix` for the cross-cutting lifecycle authority.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Single UXP Runtime (in-process, non-blocking UI thread)     │
│                                                              │
│  Panel UI (HTML + Spectrum Web Components)                   │
│       │                                                      │
│       ├── require('uxp')     → host info, entrypoints, shell │
│       ├── require('fs')      → sandbox / request / fullAccess│
│       ├── require('os')      → platform info                 │
│       └── require('premierepro') → Premiere DOM (async)      │
│                                                              │
│  Optional: require('./addons/.../foo.uxpaddon')  (Hybrid)    │
└─────────────────────────────────────────────────────────────┘
         ▲                              ▲
         │                              │
   manifest.json v5/v6          UXP Developer Tool (UDT)
   requiredPermissions           Developer Mode in Premiere
```

### Two API layers (do not confuse)
| Layer | Module | Purpose |
|---|---|---|
| **UXP Core** | `uxp`, `fs`, `os`, global `document`/`crypto` | Panel UI, filesystem, network (with manifest permission), clipboard |
| **Premiere DOM** | `premierepro` | Projects, sequences, tracks, clips, markers, effects, export, transcripts |

The **Premiere DOM** controls the edit (projects, sequences, clips). The **HTML DOM** (`document.createElement('sp-button')`) controls your panel UI. They are separate systems.

### Runtime model vs CEP
| | CEP (legacy) | UXP (current) |
|---|---|---|
| UI process | Chromium (CEF) per panel | Shared UXP runtime |
| Host API | `CSInterface.evalScript('...')` → ExtendScript | `require('premierepro')` direct |
| Call model | Sync strings over bridge | Async Promises, `await` |
| Node.js | Optional via manifest CEF flags | Not available — use UXP `fs`/`os` |
| Distribution | `.zxp` (ZXPSignCmd) | `.ccx` (UPIA / CC Marketplace) |

### Manifest v5 (standard panels)
Premiere 25.6 supports **`manifestVersion: 5`**. Required top-level keys: `manifestVersion`, `id`, `name`, `version`, `host`, `entrypoints`.

```json
{
  "manifestVersion": 5,
  "id": "com.example.my-panel",
  "name": "My Panel",
  "version": "1.0.0",
  "main": "index.html",
  "host": {
    "app": "premierepro",
    "minVersion": "25.6.0"
  },
  "entrypoints": [
    {
      "type": "panel",
      "id": "mainPanel",
      "label": { "default": "My Panel" },
      "minimumSize": { "width": 230, "height": 200 },
      "maximumSize": { "width": 2000, "height": 2000 },
      "preferredDockedSize": { "width": 300, "height": 400 }
    }
  ],
  "requiredPermissions": {
    "localFileSystem": "request",
    "network": {
      "domains": ["https://api.example.com"]
    }
  },
  "icons": [
    {
      "width": 24,
      "height": 24,
      "path": "icons/icon.png",
      "scale": [1, 2]
    }
  ]
}
```

**Permission notes (v5):** undeclared permissions are denied by default. Common entries:
- `localFileSystem`: `"plugin"` (sandbox only, default) | `"request"` (file picker) | `"fullAccess"`
- `network.domains`: allow-list URLs or `"all"`
- `launchProcess`: required for `openExternal()` / `openPath()`
- `clipboard`: `"readAndWrite"` if needed
- `enableAddon`: `true` for Hybrid plugins (see below)

> **Hybrid plugins:** loading `.uxpaddon` native libraries may require `manifestVersion: 6` plus an `"addon": { "name": "..." }` block per Adobe's Hybrid build guide. Standard JS-only panels use v5. Verify against your UDT version when mixing addon + panel.

### UXP Developer Tool (UDT)
- Install **UXP Developer Tool v2.2.1+** from Creative Cloud Desktop.
- In Premiere: **Settings → Plugins → Developer Mode** → restart Premiere.
- UDT shows connected Premiere + UXP versions; use **Load & Watch** / **Load** to sideload unpacked plugins; **Inspect** opens Chromium DevTools for the panel.
- Distribution: package as `.ccx` via UPIA or the Developer Distribution portal.

### Hybrid `.uxpaddon` (native C++)
When JS is too slow or you need existing C++ code, a **Hybrid plugin** loads compiled `.uxpaddon` binaries at runtime (Node-API–like surface):

```
my-hybrid-plugin/
├── manifest.json          ← enableAddon: true, addon.name
├── index.html / index.js
└── addons/
    ├── mac/arm64/sample.uxpaddon
    ├── mac/x64/sample.uxpaddon
    └── win/x64/sample.uxpaddon
```

```json
{
  "requiredPermissions": { "enableAddon": true },
  "addon": { "name": "sample-uxp-addon.uxpaddon" }
}
```

```js
// UXP — Premiere 25.6+ (Hybrid)
const addon = require('./addons/mac/arm64/sample-uxp-addon.uxpaddon');
const result = addon.heavyCompute(buffer); // C++ exposed function
```

macOS `.uxpaddon` binaries require **Apple Developer ID signing + notarization** for production. CC Marketplace requires all three arch folders (mac arm64, mac x64, win x64). See `cpp-native-sdk` for PrSDK vs Hybrid trade-offs.

## API Surface

### Async vs sync rule
| Kind | Await? | Examples |
|---|---|---|
| **Methods** | **Yes** — always `await` | `getActiveProject()`, `importFiles()`, `getActiveSequence()`, `createInsertProjectItemAction()` |
| **Properties** | **No** — sync get/set | `project.name`, `sequence.name`, `project.guid` |
| **Static factories** | **Yes** | `Project.getActiveProject()`, `TickTime.createWithSeconds(1.5)` |

Forgetting `await` on a method yields a **pending Promise object**, not the resolved value — the #1 migration bug from ExtendScript.

### Entry point and version detection
```js
// UXP — Premiere 25.6+
const ppro = require('premierepro');
const { host, versions } = require('uxp');

const project = await ppro.Project.getActiveProject();
if (!project) { throw new Error('No active project'); }

// Gate features on host version
const major = parseInt(host.version.split('.')[0], 10); // 25 or 26
```

### Core classes and methods (Premiere DOM)

> Full reference: https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
> TypeScript: `@adobe/premierepro` npm package (+ `@beta` for bleeding edge).
> Min-version tags on each member in the official reference (most baseline **25.0** within the UXP era).

#### `Project` (static + instance)
| Member | Async | Min | Notes |
|---|---|---|---|
| `Project.getActiveProject()` | ✓ | 25.0 | Returns `null` if no project |
| `Project.open(path, options?)` | ✓ | 25.0 | |
| `Project.createProject(path)` | ✓ | 25.0 | |
| `project.getActiveSequence()` | ✓ | 25.0 | |
| `project.setActiveSequence(seq)` | ✓ | 25.0 | |
| `project.getRootItem()` | ✓ | 25.0 | `FolderItem` — project panel root |
| `project.getSequences()` | ✓ | 25.0 | `Sequence[]` |
| `project.importFiles(paths, suppressUI, targetBin?, asNumberedStills?)` | ✓ | 25.0 | Does not return created items — search afterward |
| `project.importAEComps(aepPath, compNames, targetBin)` | ✓ | 25.0 | |
| `project.createSequence(name, presetPath)` | ✓ | 25.0 | `presetPath` arg **deprecated** — use `createSequenceWithPresetPath` |
| `project.createSequenceWithPresetPath(name, presetPath)` | ✓ | 25.0 | Preferred preset-based creation |
| `project.createSequenceFromMedia(name, clipProjectItems, targetBin?)` | ✓ | 25.0 | |
| `project.executeTransaction(callback, undoString?)` | ✓ | 25.0 | **Required wrapper for edit mutations** |
| `project.lockedAccess(callback)` | ✓ | 25.0 | Read-lock during callback; can nest `executeTransaction` |
| `project.save()` / `project.saveAs(path)` | ✓ | 25.0 | |
| `project.name`, `project.path`, `project.guid` | sync | 25.0 | |

#### `Sequence`
| Member | Async | Min | Notes |
|---|---|---|---|
| `sequence.getSequenceEditor()` | ✓ | 25.0 | Returns `SequenceEditor` for edit actions |
| `sequence.getVideoTrack(index)` / `getAudioTrack(index)` | ✓ | 25.0 | |
| `sequence.getPlayerPosition()` / `setPlayerPosition(tickTime)` | ✓ | 25.0 | CTI |
| `sequence.getInPoint()` / `setInPoint(tickTime)` | ✓ | 25.0 | |
| `sequence.getOutPoint()` / `setOutPoint(tickTime)` | ✓ | 25.0 | |
| `sequence.exportAsFinalCutProXML(path)` | ✓ | 25.0 | |
| `sequence.getSettings()` / `setSettings(settings)` | ✓ | 25.0 | |
| `sequence.getFrameSize()` | ✓ | 25.0 | |
| `sequence.getTimebase()` | ✓ | 25.0 | Ticks per frame |
| `sequence.getFrameRate()` | ✓ | 25.6+ | **Added in 25.6** — early UXP builds lacked this getter |
| Markers | ✓ | 25.0 | See `markers` |

#### `SequenceEditor` (action-based editing, 25.0+)
Replaces direct `insertClip` / `overwriteClip` calls. Build **actions**, add to `CompoundAction`, execute inside `executeTransaction`.

| Static factory | Purpose |
|---|---|
| `createInsertProjectItemAction(projectItem, time, vTrackIndex, aTrackIndex)` | Ripple insert |
| `createOverwriteProjectItemAction(projectItem, time, vTrackIndex, aTrackIndex)` | Overwrite |
| `createCloneTrackItemAction(trackItem, time, vOffset, aOffset, vTrackIndex, aTrackIndex)` | Clone clip |
| `createRemoveItemsAction(trackItems, ripple, alignToVideo)` | Delete |
| `createMoveTrackItemAction(...)` | Move clip |

Pattern:
```js
await project.executeTransaction(async (compoundAction) => {
  const editor = await sequence.getSequenceEditor();
  const action = editor.createInsertProjectItemAction(item, tickTime, 0, 0);
  compoundAction.addAction(action);
}, 'Insert clip');
```

#### `TickTime`
| Member | Notes |
|---|---|
| `TickTime.createWithSeconds(n)` | Factory |
| `TickTime.createWithTicks(ticksString)` | Ticks exceed JS safe integer — often passed as string |
| `tickTime.seconds`, `tickTime.ticks` | sync properties |
| `TickTime.alignToFrame(tickTime, frameRate)` | Frame alignment |
| `TickTime.alignToNearestFrame(tickTime, frameRate)` | |

Ticks per second: **254016000000** (same as ExtendScript). See `sequences-tracks-trackitems`.

#### Effects, keyframes, metadata
| Area | UXP surface | ExtendScript parity |
|---|---|---|
| Add video/audio effects | Effect APIs on track items (by effect reference) | Partial — QE still needed for **by-name** lookup in ExtendScript |
| Keyframes | Keyframe APIs (evolving) | Partial |
| Metadata | `getProjectMetadata` / XMP APIs | Partial |
| Component properties | `Component` / `ComponentParam` | **MOGRT Source Text JSON: no parity** |

#### `ProjectConverter` (interop)
| Method | Purpose |
|---|---|
| `importAAF(path, options?)` | AAF import |
| `importFCPXML(path, options?)` | FCPXML import |
| `importOTIO(path, options?)` | OTIO import |
| Export variants | See `xml-fcpxml` |

#### `Preset`
Load sequence/export presets by path — replaces some ExtendScript preset-file workflows.

#### Transcripts / captions (evolving, 25.6+)
Caption and transcript APIs are actively growing. Check `@adobe/premierepro` types and `captions` for the current surface — do not assume ExtendScript parity.

#### UXP Core (panel infrastructure)
| API | Module | Permission |
|---|---|---|
| `host.version`, `entrypoints.getPanel()` | `uxp` | none |
| `fs.getFileForOpening()`, `fs.getFolder()` | `fs` | `localFileSystem: "request"` |
| `shell.openExternal(url)`, `shell.openPath(path)` | `uxp` | `launchProcess` |
| `fetch(url)` | global | `network.domains` |

### Tooling packages
| Package | Purpose |
|---|---|
| `@adobe/premierepro` | Official TypeScript declarations |
| `@adobe/eslint-plugin-premierepro` | Lint rules for Premiere UXP APIs |
| UXP Developer Tool (UDT) | Load, watch, debug, package |
| AdobeDocs/uxp-premiere-pro-samples | Reference panel implementations |

## Working Examples

### 1. Minimal panel entry — validate chain, read active sequence
```js
// UXP — Premiere 25.6+ (panel index.js)
const ppro = require('premierepro');

async function getActiveSequenceSafe() {
  const project = await ppro.Project.getActiveProject();
  if (!project) {
    return { ok: false, error: 'No project open.' };
  }
  const sequence = await project.getActiveSequence();
  if (!sequence) {
    return { ok: false, error: 'No active sequence.' };
  }
  return { ok: true, project, sequence };
}

document.getElementById('btnRefresh').addEventListener('click', async () => {
  const result = await getActiveSequenceSafe();
  const label = document.getElementById('status');
  if (!result.ok) {
    label.textContent = result.error;
    return;
  }
  label.textContent = 'Sequence: ' + result.sequence.name;
});
```

### 2. Import media with user-selected files
```js
// UXP — Premiere 25.6+
const ppro = require('premierepro');
const fs = require('fs');

async function importViaPicker() {
  const project = await ppro.Project.getActiveProject();
  if (!project) { return { ok: false, error: 'No project' }; }

  const files = await fs.getFileForOpening({ allowMultiple: true });
  if (!files || files.length === 0) { return { ok: false, error: 'Cancelled' }; }

  const paths = files.map((f) => f.nativePath);
  const ok = await project.importFiles(paths, true);
  return { ok, error: ok ? '' : 'importFiles returned false' };
}
```

Requires `"localFileSystem": "request"` in manifest.

### 3. Insert clip via SequenceEditor + executeTransaction
```js
// UXP — Premiere 25.6+
const ppro = require('premierepro');

async function insertClipAtPlayhead(projectItem) {
  const project = await ppro.Project.getActiveProject();
  if (!project) { throw new Error('No project'); }

  const sequence = await project.getActiveSequence();
  if (!sequence) { throw new Error('No active sequence'); }

  const ct = await sequence.getPlayerPosition();
  const editor = await sequence.getSequenceEditor();

  const ok = await project.executeTransaction((compoundAction) => {
    const action = editor.createInsertProjectItemAction(
      projectItem,
      ct,
      0,  // video track index (0-based)
      0   // audio track index (0-based)
    );
    compoundAction.addAction(action);
  }, 'Insert clip at playhead');

  return ok;
}
```

### 4. Create sequence from preset path
```js
// UXP — Premiere 25.6+
const ppro = require('premierepro');
const os = require('os');
const path = require('path'); // not available in UXP — build path manually

async function createSequenceFromPreset(name, presetPath) {
  const project = await ppro.Project.getActiveProject();
  if (!project) { throw new Error('No project'); }

  // Prefer createSequenceWithPresetPath over deprecated presetPath arg on createSequence
  const seq = await project.createSequenceWithPresetPath(name, presetPath);
  if (!seq) { throw new Error('createSequenceWithPresetPath failed'); }

  await project.setActiveSequence(seq);
  return seq;
}

// macOS example preset location (verify on target machine):
// ~/Library/Application Support/Adobe/Premiere Pro/25.0/Settings/SequencePresets/...
```

### 5. Add a sequence marker
```js
// UXP — Premiere 25.6+
const ppro = require('premierepro');

async function addMarkerAtSeconds(seconds, name, comment) {
  const project = await ppro.Project.getActiveProject();
  const sequence = project ? await project.getActiveSequence() : null;
  if (!sequence) { throw new Error('No active sequence'); }

  const tickTime = ppro.TickTime.createWithSeconds(seconds);
  const markers = await sequence.getMarkers();
  if (!markers) { throw new Error('No marker collection'); }

  await project.executeTransaction(() => {
    markers.createMarker(tickTime, name, comment, 0, ''); // signature per @adobe/premierepro types
  }, 'Add marker');
}
```

Verify exact `createMarker` signature against `@adobe/premierepro` for your target build — the API is still evolving.

### 6. Export FCPXML from active sequence
```js
// UXP — Premiere 25.6+
const ppro = require('premierepro');
const fs = require('fs');

async function exportActiveSequenceFCPXML(outPath) {
  const project = await ppro.Project.getActiveProject();
  const sequence = project ? await project.getActiveSequence() : null;
  if (!sequence) { throw new Error('No active sequence'); }

  const ok = await sequence.exportAsFinalCutProXML(outPath);
  return ok;
}
```

### 7. Version-gated feature check (host + UXP)
```js
// UXP — Premiere 25.6+
const { host, versions } = require('uxp');

function parseMajor(versionString) {
  return parseInt(String(versionString).split('.')[0], 10);
}

function supportsUxpFrameRateGetter() {
  return parseMajor(host.version) >= 25; // getFrameRate() landed 25.6 — verify in your build
}

console.log('Premiere', host.version, 'UXP', versions.uxp);
```

## Limitations

### Documented hard walls
- **Premiere 25.6+ only.** No fallback for 25.5 and earlier — ship a parallel CEP/ExtendScript build for mixed install bases.
- **No QE DOM.** Operations only available via `app.enableQE()` (effects-by-name, ripple trim tools, clip speed/reverse, `exportFramePNG`) have **no UXP equivalent** yet. See `reverse-engineering-qe-dom`.
- **No MOGRT Source Text JSON parity.** The ExtendScript workflow (`getMGTComponent()` → `getValue()`/`setValue()` on Source Text JSON with `fontTextRunLength`) is **not exposed in UXP as of 25.6**. Text-injection tooling must stay on ExtendScript/CEP until Adobe closes the gap. See `essential-graphics-mogrt-text`.
- **No Node.js.** Use UXP `fs`/`os`; no `npm install` at runtime. Bundle dependencies at build time (Vite/Rollup/webpack).
- **Spectrum Web Components partially supported in Premiere.** Not every `sp-*` element behaves as documented for Photoshop/InDesign. Test UI in Premiere specifically.
- **Adobe does not intend 1:1 CEP→UXP parity.** Missing APIs must be requested on the Creative Cloud Developer Forums — Adobe prioritizes by request volume.
- **Hybrid / PrSDK still required** for new codecs, GPU effects, custom importers/exporters, and heavy compute.

### Known gaps and bugs (25.6 era)
| Gap | Impact | Workaround |
|---|---|---|
| MOGRT text blob editing | Cannot automate lower-thirds/text MOGRTs | ExtendScript/CEP fallback (`essential-graphics-mogrt-text`) |
| `sequence.getFrameRate()` missing in early UXP builds | Frame math fails | Use `getSettings()` / `getTimebase()` or gate on version |
| Stock panel hang | Some UXP panels freeze when browsing Adobe Stock | Avoid Stock API until fixed; test on target build |
| Sequence preset creation reliability | `createSequenceWithPresetPath` may fail on some presets | QE `newSequence(name, presetPath)` via ExtendScript fallback (`confidence: medium`) |
| Clip speed / reverse | Not in UXP DOM | QE DOM or manual FCPXML (`reverse-engineering-qe-dom`) |
| Effects by display name | UXP uses effect references, not QE name lookup | Pre-build effect map from project; or QE fallback |

## Common Errors & Gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `[object Promise]` in UI / logic errors | Forgot `await` on DOM method | Add `await`; use `async` handler |
| Edit appears then vanishes / no undo entry | Mutation outside `executeTransaction` | Wrap all timeline/project mutations |
| `executeTransaction` callback is async but edits don't apply | Passing `async` callback — action must be sync inside callback | Build actions synchronously inside callback; only the outer `executeTransaction` call is awaited |
| Plugin not listed in UDT | Developer Mode off or bad manifest | Enable Settings → Plugins → Developer Mode; restart; validate JSON |
| `localFileSystem` access denied | Missing manifest permission | Add `"localFileSystem": "request"` (or appropriate level) |
| Network fetch blocked | Domain not allow-listed | Add domain to `requiredPermissions.network.domains` |
| `CSInterface is not defined` | CEP pattern pasted into UXP | Remove bridge — use `require('premierepro')` |
| Panel loads, DOM throws immediately | User on Premiere < 25.6 | Gate install; show clear version error |
| Hybrid "Plugin Manifest Validation Failed" | Wrong `addons/` folder layout or unsigned macOS binary | Follow strict mac/arm64, mac/x64, win/x64 tree; sign + notarize |
| Stale sequence/project reference | Holding object across project switch | Re-fetch `getActiveProject()` / `getActiveSequence()` each operation |
| Using `JSON` worries | N/A in UXP | Native JSON available — no json2.js needed |

### executeTransaction — critical pattern
```js
// WRONG — mutation without transaction (may not undo correctly)
await editor.createInsertProjectItemAction(item, t, 0, 0); // don't call actions directly

// WRONG — async callback body
await project.executeTransaction(async (ca) => { /* ... */ }, 'Edit'); // avoid async callback

// RIGHT
await project.executeTransaction((compoundAction) => {
  const action = editor.createInsertProjectItemAction(item, t, 0, 0);
  compoundAction.addAction(action);
}, 'Insert clip');
```

## Workarounds

- **Mixed install base (pre-25.6 + 2026):** ship **two builds** — CEP `.zxp` for legacy, UXP `.ccx` for 25.6+. Detect host version before recommending install.
- **MOGRT text / QE-only ops:** keep a **CEP + ExtendScript helper panel** (or headless `.jsx` invoked externally) for the gap features; isolate behind a version/feature flag module.
- **UI framework:** Bolt UXP (Hyper Brew) scaffolds Vite + TS + Spectrum; Adobe sample repo for raw patterns.
- **Type safety:** `@adobe/premierepro` + `@adobe/eslint-plugin-premierepro` catch missing `await` and deprecated APIs at lint time.
- **Missing API:** file a detailed request on the [Creative Cloud Developer Forums](https://community.adobe.com/t5/premiere-pro/bd-p/premiere-pro) tagged Premiere + UXP; include use case and ExtendScript equivalent.
- **Heavy compute:** UXP Hybrid `.uxpaddon` or standalone PrSDK plugin (`cpp-native-sdk`).

## Migration

This **is** the migration target for `extendscript-core` and `cep`. Treat every feature as **verify-then-port** — do not assume parity.

### Runtime shifts
| ExtendScript / CEP | UXP |
|---|---|
| `app.project.activeSequence` | `await (await ppro.Project.getActiveProject()).getActiveSequence()` |
| Sync calls | `await` on every DOM **method** |
| `CSInterface.evalScript(...)` | Direct `require('premierepro')` — no bridge, no string serialization |
| `json2.js` polyfill | Native `JSON` |
| `new Time(); t.seconds = n` | `ppro.TickTime.createWithSeconds(n)` |
| `seq.insertClip(item, time, v, a)` | `SequenceEditor.createInsertProjectItemAction` inside `executeTransaction` |
| `seq.overwriteClip(...)` | `createOverwriteProjectItemAction` + transaction |
| `trackItem.remove(ripple, align)` | `createRemoveItemsAction` + transaction |
| `app.project.importFiles(...)` | `await project.importFiles(...)` |
| `seq.exportAsFinalCutProXML(path)` | `await sequence.exportAsFinalCutProXML(path)` |
| `seq.importMGT(...)` + Source Text JSON | **No UXP parity** — keep ExtendScript |
| `app.enableQE()` / `qe.*` | **Not available** — keep ExtendScript or wait for UXP API |
| CEP `manifest.xml` / `.debug` | UXP `manifest.json` v5 + UDT |
| `.zxp` distribution | `.ccx` via UPIA / Marketplace |

### Panel migration checklist
1. Replace CEP manifest with UXP `manifest.json` v5 (`host.app: "premierepro"`, `minVersion: "25.6.0"`).
2. Move host `.jsx` logic into panel JS/TS — delete `evalScript` bridge.
3. Add `await` to every Premiere DOM method call.
4. Wrap all edit operations in `project.executeTransaction`.
5. Replace Node/CEF-specific code with UXP `fs`/`os`/fetch.
6. Rebuild UI with Spectrum Web Components; retest every control in Premiere (not Photoshop).
7. Audit feature list against **Limitations** — keep CEP build for gaps (MOGRT text, QE ops).
8. Package as `.ccx`; test with UDT on clean 25.6+ and 26.x builds.

### UXP Scripting (headless `.js`)
UXP also supports running single-file scripts outside a panel (UXP Scripting). Same `require('premierepro')` rules apply. Useful for batch automation without panel UI — still requires 25.6+.

## Cross-References
- `00-technology-status-matrix` — lifecycle authority, version map, decision guide
- `extendscript-core` — ES3 patterns being replaced; json2.js; Time/ticks
- `cep` — legacy panel bridge being replaced
- `panels` — CEP vs UXP comparison matrix
- `sequences-tracks-trackitems` — DOM hierarchy; SequenceEditor action mapping
- `essential-graphics-mogrt-text` — MOGRT text gap (ExtendScript-only for now)
- `reverse-engineering-qe-dom` — QE escape hatch (ExtendScript-only; no UXP port)
- `import` — async `importFiles` patterns
- `markers` — marker API (both runtimes)
- `captions` — evolving UXP transcript/caption surface
- `cpp-native-sdk` — PrSDK + Hybrid `.uxpaddon`
- `debugging` — UDT workflow, Developer Mode

## Sources
- https://developer.adobe.com/premiere-pro/uxp/
- https://developer.adobe.com/premiere-pro/uxp/resources/fundamentals/apis/
- https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
- https://developer.adobe.com/premiere-pro/uxp/plugins/concepts/manifest/
- https://developer.adobe.com/premiere-pro/uxp/plugins/hybrid-plugins/
- https://developer.adobe.com/premiere-pro/uxp/plugins/hybrid-plugins/build/
- https://github.com/AdobeDocs/uxp-premiere-pro-samples
- https://hyperbrew.co/blog/uxp-plugins-in-premiere-2026/
