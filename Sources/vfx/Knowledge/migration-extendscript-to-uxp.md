---
id: migration-extendscript-to-uxp
title: Migration Guide - ExtendScript to UXP
category: migration
status: current
stability: active
doc_status: complete
introduced: "2025"
min_premiere_version: "25.6"
api_namespace: null
languages: [extendscript, javascript]
tags: [migration, extendscript, uxp, upgrade-path]
related: [extendscript-core, uxp, best-practices]
sources: []
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Migration Guide: ExtendScript to UXP

## Overview

ExtendScript (ES3) EOL Sept 2026. Migrate production code to UXP (Premiere 25.6+).

Timeline:
- Now-Sept 2025: Dual support (ExtendScript + UXP)
- Sept 2025-Sept 2026: Maintenance only (ExtendScript)
- Sept 2026+: ExtendScript gone, UXP only

---

## Step 1: Assess Code

| Pattern | ExtendScript | UXP | Effort |
|---|---|---|---|
| Sequential loops | Yes | Yes | Low |
| UI (panel/dialog) | Yes (CEP) | Yes (UXP) | High |
| File I/O | Yes | Limited | Medium |
| Timeline mutations | Yes | Yes + executeTransaction() | Medium |

---

## Step 2: Rewrite with Async/Await

ExtendScript (blocking):
```javascript
var seq = app.project.activeSequence;
var name = seq.name;
alert(name);
```

UXP (async):
```javascript
const { application } = require("premierepro");
(async () => {
  const proj = await application.activeProject;
  const seq = await proj.activeSequence;
  const name = await seq.name;
  console.log(name);
})();
```

---

## Step 3: Use executeTransaction for Mutations

ExtendScript:
```javascript
clip.name = "New Name";
```

UXP:
```javascript
await application.executeTransaction(async () => {
  await clip.setName("New Name");
});
```

---

## Step 4: Error Handling

ExtendScript:
```javascript
try {
  var seq = app.project.activeSequence;
} catch (e) {
  alert("Error: " + e);
}
```

UXP:
```javascript
try {
  const seq = await proj.activeSequence;
} catch (error) {
  console.error("Error:", error.message);
}
```

---

## Fallback: Hybrid Approach

If UXP missing APIs (effects-by-name, ripple, speed):
1. Use UXP for UI + standard operations
2. Fall back to QE for unsupported features
3. Document QE usage (high risk)

---

## Timeline & Estimated Effort

- Phase 1 (Now-Q2 2025): Prototype in UXP, keep ExtendScript backup
- Phase 2 (Q2-Q4 2025): Full UXP migration
- Phase 3 (Q4 2025-Sept 2026): Maintenance mode only
- Phase 4 (Sept 2026+): ExtendScript removed

Effort: Simple script (<500 LOC) 1-2 days; Medium (500-2000 LOC) 1-2 weeks; Complex (2000+ LOC + UI) 2-4 weeks; with C++ hybrid +3-6 weeks.

---

See also: uxp.md, best-practices.md
