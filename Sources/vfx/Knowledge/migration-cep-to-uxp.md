---
id: migration-cep-to-uxp
title: Migration Guide - CEP to UXP Panels
category: migration
status: current
stability: active
doc_status: complete
introduced: "2025"
min_premiere_version: "25.6"
api_namespace: null
languages: [javascript, extendscript]
tags: [migration, cep, uxp, panels, ui]
related: [cep, uxp, panels, best-practices]
sources: []
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Migration Guide: CEP to UXP Panels

## Overview

CEP (Chromium panels) deprecated in Premiere 2026. Unsigned CEP fails on macOS 25.2.3+. Migrate to UXP (native, async, modern).

---

## Step 1: Compare Architectures

| Aspect | CEP | UXP |
|---|---|---|
| Runtime | Chromium v59-v80 | Native (React-like) |
| Language | HTML5/CSS + JS + ExtendScript bridge | UXP DOM + async JS |
| Signing | ZXP (macOS 25.2.3+ mandatory) | UXP (simpler) |
| Debugging | CEP Debugger (old) | UDT (modern) |
| Async | No (blocking) | Yes (async/await) |

---

## Step 2: Rewrite JS Bridge

CEP:
```javascript
var csInterface = new CSInterface();
csInterface.evalScript("app.project.name", function(result) {
  console.log(result);
});
```

UXP:
```javascript
const { application } = require("premierepro");
(async () => {
  const proj = await application.activeProject;
  const name = await proj.name;
  console.log(name);
})();
```

---

## Step 3: Migrate Manifest

CEP manifest.xml requires Host/MainPath/DigitalSignatures.
UXP manifest.json uses uiModes array with type "panel".

---

## Timeline

- 24.x: CEP 11 (works, signing optional)
- 25.0-25.2.2: CEP 12 (unsigned works)
- 25.2.3+: CEP 12 (unsigned BROKEN on macOS)
- 26.0+: CEP deprecated

Recommendation: Migrate by Q4 2025 (before 26.0).

Effort: Small panel (<500 LOC) 3-5 days; Medium (500-2000 LOC) 2-3 weeks; Large (2000+ LOC) 4-8 weeks.

---

See also: uxp.md, cep.md, panels.md
