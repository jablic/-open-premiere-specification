---
id: faq-troubleshooting-tree
title: FAQ & Troubleshooting Decision Tree
category: support
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2014"
min_premiere_version: "14.0"
api_namespace: null
languages: [extendscript, javascript, uxp]
tags: [faq, troubleshooting, debugging, errors, support, common-issues]
related: [debugging, best-practices, panels, automation]
sources: [
  "User support issues",
  "Production troubleshooting",
  "Community Q&A patterns"
]
confidence: high
last_verified: "2026-07-01"
verified_against_version: "25.6"
---

# FAQ & Troubleshooting Decision Tree

## TL;DR

**ExtendScript issues:** Check app.project exists, wrap in try-catch, verify menu IDs. **UXP async:** Always use await, check for null references, test in dev environment first. **Panel problems:** Verify CSInterface availability, check manifest.xml, enable remote debugging. **Import failures:** Validate file paths (use Folder.fs for cross-platform), check codec support, offline media indicator. **Performance:** Profile with timing, use QE DOM for queries, cache results. **Decision tree:** Error type → symptom → root cause → fix with 5-level decision hierarchy.

---

## Quick Diagnostics Flow

```
Error occurs
│
├─ Is app.project null?
│  ├─ YES → Wait for project load (500ms delay)
│  └─ NO → Continue
│
├─ Is error in ExtendScript eval?
│  ├─ YES → Wrap in try-catch, return error string
│  └─ NO → Continue
│
├─ Is error in UXP async?
│  ├─ YES → Add await, check null references
│  └─ NO → Continue
│
├─ Is panel not loading?
│  ├─ YES → Check CSInterface, manifest.xml, ports 8088/8089
│  └─ NO → Check console for JavaScript errors
│
└─ Still stuck? → See detailed troubleshooting tables below
```

---

## FAQ by Category

### ExtendScript Fundamentals

| Q | A | Issue Type |
|---|---|---|
| **"Cannot read property 'name' of undefined"** | Check if object exists before accessing properties: `if (seq && seq.name)` | Null reference |
| **"app is not defined"** | Ensure script runs in Premiere context, not external editor | Scope error |
| **"SyntaxError: Unexpected token"** | ExtendScript is ES3; no arrow functions `=>`, no `const`. Use `var` and `function()` | Language limitation |
| **"importFiles returns false"** | importFiles doesn't return items, only success/fail. Check bin.children for imported items | API mismatch |
| **"Effect not applied"** | Verify effect name with `app.getEffectsList()`, use exact name from Premiere UI | Naming error |
| **Script runs but nothing happens** | Wrap in `app.beginUndoGroup()` / `app.endUndoGroup()` for changes to persist | Undo stack issue |

### UXP Development

| Q | A | Issue Type |
|---|---|---|
| **"Cannot access 'projectItem' before initialization"** | Always use `await` for async operations: `const item = await clip.projectItem` | Async handling |
| **"TypeError: Cannot read property 'activeProject' of undefined"** | Import `{ application }` correctly: `import { application } from "premierepro"` | Import error |
| **"Module not found: 'premierepro'"** | Only available in Premiere 24.0+. Check manifest.json `requiredHostMinVersion` | Version error |
| **Panel renders but no data shows** | Test with `console.log()` in DevTools (localhost:8089 for UXP). Data fetch may be async | Async data loading |
| **"Security warning: Cannot fetch URL"** | Add to manifest.json `permissions: ["network"]` and whitelist domain if needed | Security sandbox |

### Import & Media Issues

| Q | A | Issue Type |
|---|---|---|
| **"File not found" on Windows**  | Use `new File(path)` without drive letter for cross-platform: `/mnt/storage/` not `Z:\storage\` | Path format |
| **"Media appears offline"** | Check file exists: `if (item.file.exists)`. If false, relink via `item.refreshMedia()` | Relinking needed |
| **"Proxy not created for RED file"** | RED proxies only in Premiere 24.6+. Try DNxHD proxy instead: `createMediaProxy("1/4 Resolution")` | Version limited |
| **"Import hangs with 10,000+ files"** | Batch in groups of 500: split array, import, wait 100ms between batches | Performance |
| **"Cannot import H.265"** | Requires codec support (Windows/Mac may differ). Transcode to ProRes first | Codec support |

### Panels & CEP

| Q | A | Issue Type |
|---|---|---|
| **"CSInterface is not defined"** | Add check in window.addEventListener('load'): `if (typeof CSInterface !== 'undefined')` | Timing issue |
| **"evalScript returns null"** | Script ran but failed. Always wrap ExtendScript in try-catch and return error string | Error swallowing |
| **"Panel doesn't appear in menu"** | Verify manifest.xml `<Extension>`, restart Premiere, check Plugin Manager | Config error |
| **"Console.log shows nothing"** | Enable remote debugging: registry `PlayerDebugMode=1` (Windows) or system settings (Mac) | Debug mode off |
| **"CORS error when fetching API"** | CEP blocks cross-domain XHR. Use CSInterface.evalScript() instead, or add AllowNetworking to manifest | Network sandbox |

### Performance Issues

| Q | A | Issue Type |
|---|---|---|
| **"Script hangs on 1000+ clips"** | Enable QE: `app.enableQE()` reduces iteration time 100x. Avoid nested loops. | Algorithmic |
| **"Memory usage grows over time"** | Clear arrays after use: `largeArray = []`. Check for circular references. Profile with iterations. | Memory leak |
| **"Real-time playback drops at 4K"** | Switch to 1/4 resolution proxies. Disable audio scrubbing. Check hard drive speed. | Hardware limit |
| **"Panel UI freezes when processing"** | ExtendScript blocks UI. Break work into batches: `$.sleep(10)` between iterations to yield. | UI blocking |
| **"QE DOM returns null"** | Not all contexts support QE. Wrap in try-catch: `if (!app.enableQE()) { use standard DOM }` | QE unavailable |

### Audio Issues

| Q | A | Issue Type |
|---|---|---|
| **"Audio track missing from sequence"** | Some clips have no audio. Check: `clip.projectItem.hasAudio` before access. Add audio-only track if needed. | Missing audio |
| **"Sample rate mismatch (48kHz vs 44.1kHz)"** | Premiere automatically resamples. Check: Project → Project Settings → Audio. | Automatic |
| **"Audio sync drifts over time"** | Timecode mismatch. Verify source and sequence frame rates match exactly. Relink media. | Sync issue |
| **"Cannot set audio levels via script"** | Audio levels require Lumetri or external tool. ExtendScript can't directly modify. | API limitation |

### Marker Issues

| Q | A | Issue Type |
|---|---|---|
| **"Marker created but doesn't appear"** | Call `seq.setPlayerPosition()` to refresh: `seq.setPlayerPosition(marker.start)` | Refresh needed |
| **"Cannot read marker color"** | Marker colors are 0-7 (index). Clamp: `Math.max(0, Math.min(7, index))` | Range error |
| **"Batch delete markers fails"** | Delete from end to start (reverse): `for (i = count - 1; i >= 0; i--)` to avoid index shifts | Iteration order |
| **"Marker duration incorrect"** | Duration in Premiere time units (254016000000 per second). Convert: `durationSeconds * 254016000000` | Unit conversion |

### Color & Effects

| Q | A | Issue Type |
|---|---|---|
| **"Lumetri adjustment not visible"** | Effect applied but not enabled. Check: `effect.enabled = true` | Disabled effect |
| **"Effect parameters don't change"** | Parameter names case-sensitive. Use exact name from effect inspector. | Naming |
| **"Color space mismatch (P3 vs Rec709)"** | Check: File → Project Settings → Color Management. Conforming changes color space. | Project settings |
| **"Adjustment Layer doesn't affect clips below"** | Create Adjustment Layer above clips, ensure track is enabled. Check layer stacking order. | Layer order |

### Distribution & Export

| Q | A | Issue Type |
|---|---|---|
| **"ZXP signing fails with certificate"** | Certificate must be valid (not expired). Check: `openssl x509 -in cert.p12 -text` | Certificate issue |
| **"Export hangs at 99%"** | Timeout on muxing. Simplify sequence (remove unused tracks, effects). Export to ProRes intermediate first. | Hang/timeout |
| **"H.264 file won't play in browser"** | H.264 codec support varies. Use MP4 container instead of MOV. | Container issue |
| **"UXP plugin won't install from marketplace"** | Check manifest.json version format (must be semver: X.Y.Z). Repackage and resubmit. | Validation error |

---

## Troubleshooting Decision Trees

### Tree 1: "Script doesn't run"

```
Does the script appear in any menu?
│
├─ NO → Is it in correct folder? (~/Library/Application Support/Adobe/CEP/extensions)
│  └─ Move script, restart Premiere
│
├─ YES, but clicking does nothing
│  ├─ Check: Is app.project null?
│  │  ├─ YES → Add delay: setTimeout(() => {...}, 500)
│  │  └─ NO → Continue
│  │
│  ├─ Is there a syntax error?
│  │  ├─ YES → Check JavaScript console, fix error
│  │  └─ NO → Add try-catch
│  │
│  └─ Wrap in app.beginUndoGroup() / app.endUndoGroup()
│
└─ Script runs but no visual change
   ├─ Check console: $.writeln("DEBUG")
   └─ Verify effect/clip exists before modifying
```

### Tree 2: "Panel won't load"

```
Is Premiere running?
│
├─ NO → Start Premiere, load CEP/UXP panel
│
└─ YES
   ├─ Does panel appear in Window → Extensions?
   │  ├─ NO → Check manifest.xml is valid XML
   │  │  └─ Use online XML validator
   │  │
   │  └─ YES, but shows error
   │     ├─ Is CSInterface available?
   │     │  ├─ In DevTools (localhost:8088)?
   │     │  │  ├─ YES → Check console for errors
   │     │  │  └─ NO → Enable PlayerDebugMode in registry
   │     │  │
   │     │  └─ In panel code?
   │     │     └─ Wait for window.load before accessing
   │     │
   │     └─ Does manifest allow network?
   │        └─ Add `<AllowNetworking>all</AllowNetworking>`
```

### Tree 3: "Media won't import"

```
Does file exist?
│
├─ NO → Check path: Use Folder.fs for cross-platform compatibility
│
└─ YES
   ├─ Is it a supported format?
   │  ├─ NO (e.g., H.265 on unsupported OS) → Transcode to ProRes
   │  └─ YES → Continue
   │
   ├─ Is project open?
   │  ├─ NO → Create/open project first
   │  └─ YES → Continue
   │
   ├─ importFiles() returns true/false?
   │  ├─ FALSE → Check disk space, try smaller file
   │  └─ TRUE → Check bin.children for imported items (not returned directly)
   │
   └─ Does media appear offline?
      ├─ YES → Relink: projectItem.refreshMedia()
      └─ NO → Success!
```

### Tree 4: "Slow script performance"

```
How many clips are you processing?
│
├─ < 100 → Acceptable, no optimization needed
│
├─ 100–1000 → Use QE: app.enableQE()
│  └─ Expect 10–100x speedup
│
└─ 1000+ → Multiple optimizations
   ├─ Enable QE: app.enableQE()
   ├─ Cache results: Don't query same data twice
   ├─ Avoid nested loops: O(n²) kills performance
   ├─ Batch I/O: Import 500 at a time, not 1 at a time
   └─ Profile with timing to find bottleneck
```

### Tree 5: "Async code not working (UXP)"

```
Does code use await?
│
├─ NO → Add await before async call: const seq = await app.activeSequence
│
├─ YES, but still undefined
│  ├─ Did you check for null?
│  │  ├─ NO → Add: if (!seq) { return; }
│  │  └─ YES → Continue
│  │
│  └─ Is it in async function?
│     ├─ NO → Wrap in: async function() { await ... }
│     └─ YES → Check DevTools console for actual error
│
└─ Code runs but data wrong
   └─ Add console.log() before/after each await to trace
```

---

## Common Error Messages & Fixes

| Error | Meaning | Fix |
|---|---|---|
| `ReferenceError: app is not defined` | Script not in Premiere context | Run from Premiere, not terminal |
| `TypeError: Cannot read property 'activeSequence' of null` | No project open | Wait for project to load, add null check |
| `SyntaxError: Missing } on line 42` | Code syntax error | Check braces match, use XML validator |
| `undefined method 'createMarker'` | Object doesn't have method | Check object type, verify API version |
| `File does not exist: /path/to/file.mov` | File path wrong or file deleted | Verify path with `file.exists` |
| `Error: Effect "Brightness" not found` | Effect name not exact | Use correct name from UI, case-sensitive |
| `ImportError: Module 'premierepro' not found` | UXP API not available | Update to Premiere 24.0+ |
| `Uncaught SyntaxError: Missing operand` | Malformed expression | Check quotes, operators, parentheses |
| `XHR error: CORS policy blocked` | Network request blocked | Use CSInterface.evalScript() instead |
| `Error: QE DOM not accessible` | QE unavailable in this context | Fallback to standard DOM query |

---

## Debugging Checklist

- ☐ Is the issue reproducible? (Consistently fails or intermittent?)
- ☐ Does it happen in fresh Premiere instance? (Or persistent in project?)
- ☐ Have you checked the console? (Debug Output panel in Premiere, DevTools for panels)
- ☐ Have you added logging? (`$.writeln()`, `console.log()`)
- ☐ Have you isolated the issue? (Remove code until it works, add back piece by piece)
- ☐ Does it happen on both Mac and Windows? (Platform-specific?)
- ☐ Have you tested with different Premiere versions? (Version-specific?)
- ☐ Have you searched the community? (Adobe forums, GitHub issues, Stack Overflow)

---

## When to Escalate

**Submit to Adobe Support if:**
- Issue is in Premiere UI itself (not your script)
- Error comes from built-in function (e.g., `app.project.exportFile()` crashes)
- Happens after Premiere update
- Affects multiple projects consistently
- You have a support subscription

**Submit to community if:**
- Custom script issue (your code)
- Workaround exists
- Question about API usage
- Feature request

**Where to get help:**
- Adobe Premiere scripting docs: https://ppro-scripting.docsforadobe.dev/
- GitHub: https://github.com/Adobe-CEP/CEP-Resources
- Forums: https://community.adobe.com/t5/premiere-pro/ct-p/ct-premiere-pro
- Stack Overflow: Tag `adobe-premiere` or `extendscript`

---

## Quick Reference: Common Patterns

```javascript
// Always wrap Premiere calls
try {
  var seq = app.project.activeSequence;
  if (!seq) throw new Error("No active sequence");
} catch (e) {
  $.writeln("Error: " + e.toString());
}

// Cross-platform file paths
var file = new File("/mnt/storage/video.mov");  // Works on Mac and Windows
if (!file.exists) {
  alert("File not found");
  return;
}

// Batch operations with error tracking
var results = { success: 0, failed: 0, errors: [] };
for (var i = 0; i < clips.length; i++) {
  try {
    // Do something
    results.success++;
  } catch (e) {
    results.failed++;
    results.errors.push(clips[i].name + ": " + e.toString());
  }
}

// UXP async pattern
async function getSequence() {
  try {
    const project = await application.activeProject;
    const seq = await project.activeSequence;
    if (!seq) return null;
    return await seq.name;
  } catch (e) {
    console.error("Error:", e);
  }
}

// Performance check
var start = new Date().getTime();
// ... operation ...
var elapsed = new Date().getTime() - start;
$.writeln("Time: " + elapsed + "ms");
```

---

## See Also

- Knowledge/debugging.md — Detailed debugging techniques
- Knowledge/best-practices.md — Error handling patterns
- Knowledge/panels.md — CEP/UXP troubleshooting
- Knowledge/automation.md — Script debugging

---

## Sources

- Adobe Support: https://support.adobe.com/en-us
- Community Forums: https://community.adobe.com/
- Stack Overflow: https://stackoverflow.com/questions/tagged/adobe-premiere
- GitHub Issues: https://github.com/Adobe-CEP/CEP-Resources/issues
