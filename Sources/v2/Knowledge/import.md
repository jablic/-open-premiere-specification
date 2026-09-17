---
id: import
title: Import
category: workflow
status: legacy
stability: frozen
doc_status: complete
introduced: "CC era"
deprecated: "API frozen 2024"
eol: "2026-09"
min_premiere_version: null
api_namespace: app
languages: [extendscript, javascript-es3, javascript]
tags: [import, importFiles, importMGT, importMGTFromLibrary, projectitem, media-path, bin, suppressUI, numbered-stills]
related: [sequences-tracks-trackitems, essential-graphics-mogrt-text, xml-fcpxml, uxp]
supersedes: []
superseded_by: [uxp]
sources:
  - https://ppro-scripting.docsforadobe.dev/general/project/
  - https://ppro-scripting.docsforadobe.dev/item/projectitem/
  - https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
---

# Import

> Bring media, captions, MOGRTs, and project files into the active Premiere project.
> ExtendScript `importFiles` is `legacy` (EOL 2026-09); UXP `project.importFiles` is `current` (25.6+).

## TL;DR
- **`app.project.importFiles(paths, suppressUI, targetBin, importAsNumberedStills)`** — general media import; returns **boolean**, not the items.
- Locate imported items afterward via **`rootItem.findItemsMatchingMediaPath(path, ignoreSubclips)`**.
- **MOGRTs** use **`importMGT(path, time, vTrack, aTrack)`** or **`importMGTFromLibrary(libraryName, templateName, time, vTrack, aTrack)`** — see `essential-graphics-mogrt-text`.
- **Project files:** `app.isDocument(path)` then `app.openDocument(path, suppressUI, addToMRU, addToRecent)` or `app.project.importFiles` for sequences inside another project.

## Status & Lifecycle
- ExtendScript import API is **frozen**; EOL **2026-09**. UXP `await project.importFiles(...)` is async and returns boolean (25.6+).
- See `00-technology-status-matrix`.

## Architecture
```
File path(s)
  └─ app.project.importFiles → ProjectItem(s) under targetBin (or root)
       └─ findItemsMatchingMediaPath → ProjectItem reference
  MOGRT path
  └─ sequence.importMGT / importMGTFromLibrary → TrackItem on timeline
```

Import creates **ProjectItem** nodes in the bin tree (`rootItem` hierarchy). Timeline placement of MOGRTs is a separate step from bin import.

## API Surface

### `app.project.importFiles(arrayOfPaths, suppressUI, targetBin, importAsNumberedStills)`

| Param | Type | Notes |
|---|---|---|
| `arrayOfPaths` | `string[]` | Absolute paths. macOS: use `/` separators. |
| `suppressUI` | `boolean` | `true` = no import dialog |
| `targetBin` | `ProjectItem` or `null` | Destination bin; `null` = root |
| `importAsNumberedStills` | `boolean` | `true` for image sequences |

**Returns:** `boolean` — success/failure only.

### Locating imported items

| Method | Returns |
|---|---|
| `project.rootItem.findItemsMatchingMediaPath(path, ignoreSubclips)` | `ProjectItem` or `null` |
| `project.rootItem.children[num]` | Child `ProjectItem` |
| `projectItem.type` | `1` = clip, `2` = bin, `3` = root, `4` = file |

### MOGRT import (on Sequence)

| Method | Notes |
|---|---|
| `sequence.importMGT(path, time, videoTrackIndex, audioTrackIndex)` | Places MOGRT on timeline |
| `sequence.importMGTFromLibrary(lib, name, time, vTrack, aTrack)` | From Essential Graphics library |

### Project / document

| Method | Notes |
|---|---|
| `app.isDocument(path)` | `true` if valid `.prproj` |
| `app.openDocument(path, suppressUI, addToMRU, addToRecent)` | Opens project file |
| `app.getProjectViewIDs()` / `app.getProjectViewSelection(viewID)` | Selected items in Project panel |

## Working Examples

```js
// ExtendScript (ES3) — import media into a named bin
function importToBin(filePaths, binName) {
  if (!app.project) { return { ok: false, error: 'No active project' }; }
  var root = app.project.rootItem;
  var bin = null;
  for (var i = 0; i < root.children.numItems; i++) {
    if (root.children[i].name === binName && root.children[i].type === 2) {
      bin = root.children[i]; break;
    }
  }
  if (!bin) {
    bin = root.createBin(binName);
  }
  var ok = app.project.importFiles(filePaths, true, bin, false);
  if (!ok) { return { ok: false, error: 'importFiles returned false' }; }
  var found = [];
  for (var j = 0; j < filePaths.length; j++) {
    var item = root.findItemsMatchingMediaPath(filePaths[j], true);
    if (item) { found.push(item.name); }
  }
  return { ok: true, items: found };
}
```

```js
// ExtendScript (ES3) — import MOGRT to timeline at playhead
function importMogrtAtPlayhead(mogrtPath) {
  var seq = app.project.activeSequence;
  if (!seq) { return false; }
  var t = seq.getPlayerPosition();
  return seq.importMGT(mogrtPath, t, 0, 0);
}
```

```js
// UXP — Premiere 25.6+
const ppro = require('premierepro');
const project = await ppro.Project.getActiveProject();
const ok = await project.importFiles(['/path/to/clip.mov'], true);
```

## Limitations
- `importFiles` does **not** return created `ProjectItem` references — must search afterward.
- No batch import progress callback in ExtendScript.
- Some codecs require installed importers (native SDK territory for new formats).
- Importing a sequence from another project may create duplicate media references — relink carefully.

## Common Errors & Gotchas
- **Symptom:** `importFiles` returns `true` but item not found. **Cause:** Path mismatch (relative vs absolute, symlink). **Fix:** Normalize paths; search with `ignoreSubclips=true`.
- **Symptom:** Import dialog appears despite `suppressUI=true`. **Cause:** Premiere needs user confirmation for conflicting media. **Fix:** Pre-check paths; handle `false` return.
- **Symptom:** MOGRT imports but text won't update. **Cause:** Wrong object layer (ProjectItem vs TrackItem). **Fix:** See `essential-graphics-mogrt-text`.
- **Windows paths:** Use escaped backslashes or forward slashes in ExtendScript strings.

## Workarounds
- Walk `rootItem` tree recursively after import if `findItemsMatchingMediaPath` fails (see `sequences-tracks-trackitems`).
- For FCPXML/AAF interchange, use `sequence.importAsFinalCutProXML` / UXP `ProjectConverter` instead of raw media import (`xml-fcpxml`).

## Migration

| ExtendScript | UXP (25.6+) |
|---|---|
| `app.project.importFiles(paths, suppress, bin, stills)` | `await project.importFiles(paths, suppressUI)` |
| Sync boolean | Async boolean — **must `await`** |
| `targetBin` as ProjectItem | Check UXP bin APIs on `Project` |

## Cross-References
- `sequences-tracks-trackitems` — bin tree, ProjectItem types
- `essential-graphics-mogrt-text` — `importMGT`, Source Text JSON
- `xml-fcpxml` — XML-based project interchange
- `uxp` — async import API

## Sources
- https://ppro-scripting.docsforadobe.dev/general/project/
- https://ppro-scripting.docsforadobe.dev/item/projectitem/
- https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
