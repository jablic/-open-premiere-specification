---
id: uxp
title: UXP (Unified Extensibility Platform) Plugins
category: ui-extensibility
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro 24.0"
min_premiere_version: "25.6"
api_namespace: premierepro
languages: [javascript-es6-plus, udt-script]
tags: [plugins, uxp, async, current-api, recommended]
related: [cep, best-practices, automation, ai-integration]
supersedes: [cep]
sources: [
  "https://developer.adobe.com/premiere-pro/uxp/",
  "https://developer.adobe.com/premiere-pro/uxp/ppro-reference/",
  "https://developer.adobe.com/premiere-pro/uxp/resources/fundamentals/apis/",
  "Production testing: Premiere 25.6"
]
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# UXP (Unified Extensibility Platform) Plugins

## TL;DR

**UXP = Unified Extensibility Platform.** Modern plugin/scripting system for Premiere. **General release: Premiere 25.6 (Dec 2025).** Async-first DOM, no Chromium (React-like DOM), native JSON manifest. **Recommended for all new work.** **Limitations:** No MOGRT text-blob parity, no effects-by-name (need QE), but covers ~80% of production tasks.

**Critical traps:**
- All Premiere DOM calls are async — must `await` or `.then()`
- `executeTransaction()` required for mutations (timeline edits)
- Missing APIs: effects-by-name, ripple edits, speed changes (use QE or wait for 26.x)
- UDT debugger (not browser DevTools) — different UI, learning curve

---

## UXP Platform Overview

### What is UXP?

Modern plugin runtime (successor to CEP + ExtendScript). HTML5-like DOM (not real Chromium), async-first API, JSON manifest, UDT debugger, native C++ integration support.

### Timeline

- **24.0 (Oct 2024):** Beta/preview
- **25.6 (Dec 2025):** General release (stable)
- **26.0 (2026):** Full production (likely API expansions)

---

## Entry Point: require("premierepro")

All Premiere API access through one module:

```javascript
const { application } = require("premierepro");

// Async/await (ES2017+)
(async () => {
  const proj = await application.activeProject;
  const seqCount = await proj.sequences.length;
  console.log("Sequences:", seqCount);
})();

// .then() (ES2015)
application.activeProject.then(proj => {
  proj.sequences.length.then(count => {
    console.log("Sequences:", count);
  });
});
```

Exported objects: `application`, Premiere DOM classes (Project, Sequence, Track, etc.), utilities (Time).

---

## Async/Await Patterns (ESSENTIAL)

All DOM access is async. Three required patterns:

### Pattern 1: Property Access

```javascript
const { application } = require("premierepro");
(async () => {
  const proj = await application.activeProject;
  const name = proj.name;  // Still a Promise!
  const nameStr = await name;  // Now we have the string
  console.log(nameStr);
})();
```

### Pattern 2: Method Calls

```javascript
const { application } = require("premierepro");
(async () => {
  const proj = await application.activeProject;
  const seqs = await proj.sequences;  // Promise of array
  
  for (let i = 0; i < seqs.length; i++) {
    const seq = seqs[i];
    const name = await seq.name;  // Property is async
    console.log("Sequence:", name);
  }
})();
```

### Pattern 3: Mutations (executeTransaction Required)

```javascript
const { application } = require("premierepro");
(async () => {
  const proj = await application.activeProject;
  
  // ALL mutations must wrap in executeTransaction
  await application.executeTransaction(async () => {
    const newSeq = await proj.createSequence({
      name: "My Sequence",
      videoFrameRate: 24
    });
    const name = await newSeq.name;
    console.log("Created:", name);
  });
  
  // Multiple edits in one transaction
  await application.executeTransaction(async () => {
    const seq = await proj.activeSequence;
    const track = await seq.videoTracks[0];
    await track.insertClip(/* ... */);
    await track.insertClip(/* ... */);
    // Both commits in single undo step
  });
})();
```

---

## Limitations: What UXP Cannot Do (Yet)

| Task | UXP 25.6 | Workaround | Expected 26.x |
|---|---|---|---|
| Create title from scratch | ❌ | Import AE `.mogrt`, patch Source Text | Unlikely soon |
| Effects by name | ❌ | Use QE or iterate all components | Likely ✅ |
| Ripple edits | ❌ | Use QE | Likely ✅ |
| Speed/duration | ❌ | Use QE | Likely ✅ |
| Export frame PNG | ❌ | Use QE | Likely ✅ |
| Read/write markers | ✅ | Works, but limited | ✅ |
| Captions | ✅ (partial) | Text ops limited | ✅ (improved) |

**Agent rule:** When UXP limitation hit, check QE. Document hybrid (UXP + QE) solution.

---

## Production Example: List Sequences Plugin

See `Examples/uxp/list-sequences.jsx` for full working plugin.

---

## UXP Hybrid Plugins (C++ Integration)

For performance-critical work (real-time playback, GPU effects):

```javascript
// Declare C++ dependency in manifest
"requiredPlugins": [
  {
    "name": "MyNativeEffect",
    "type": "filter",
    "nativePath": "./native/MyNativeEffect.uxpaddon"
  }
]

// In UXP code, invoke native plugin
const { application } = require("premierepro");
(async () => {
  const proj = await application.activeProject;
  const seq = await proj.activeSequence;
  
  await application.executeTransaction(async () => {
    const clip = await seq.videoTracks[0].clips[0];
    const effect = await clip.createComponent("MyNativeEffect");
    await effect.setParameter("intensity", 0.75);
  });
})();
```

`.uxpaddon` file: Binary plugin built with C++ SDK. Covers filters, effects, exporters.

---

## UDT Debugger

Debugging UXP plugins:

```bash
# 1. Install UDT (UXP Developer Tool)
npm install -g @adobe/udt

# 2. Start debugging session
udt --watch ./plugin-folder

# 3. Attach to Premiere
# UDT opens browser-like DevTools, connects to running plugin
# Breakpoints, console.log(), variable inspection work

# Output: localhost:7777 (default)
```

**Differences from browser DevTools:**
- No DOM tree (UXP DOM ≠ web DOM)
- Limited React DevTools
- Async/await debugging works but tricky
- Source maps required for TypeScript

---

## Migration Path: CEP → UXP

Step-by-step for existing CEP panels:

1. **Rewrite UI:** CEP HTML5 → UXP DOM (React-like, CSS)
2. **Rewrite API:** `CSInterface.evalScript()` → `require("premierepro")` + `await`
3. **Add error handling:** async/await requires try/catch
4. **Test in UDT:** Replace CEP debugger workflow
5. **Sign & package:** UXP manifest + signing (different than CEP)

**Time estimate:** 1–2 weeks for medium panel (4000 LOC CEP → UXP).

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `premierepro module not found` | UXP version < 25.6 | Update Premiere to 25.6+ |
| Promise not awaited | Forgot `await` on async call | Add `await` before method call |
| `executeTransaction is not a function` | Not imported or wrong scope | Use `application.executeTransaction()` |
| Property/method returns undefined | Async property not awaited | Add `await` to property access |
| UDT won't connect | Premiere version mismatch | Ensure UDT ≤ Premiere version |

---

## Sources

- Adobe UXP docs: https://developer.adobe.com/premiere-pro/uxp/
- UXP Premiere API reference: https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
- Adobe UXP SDK: https://developer.adobe.com/premiere-pro/uxp/resources/fundamentals/apis/
- UDT GitHub: https://github.com/Adobe-UXP/UDT
