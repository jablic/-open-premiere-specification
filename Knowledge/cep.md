---
id: cep
title: CEP (Common Extensibility Platform)
category: ui-extensibility
status: legacy
stability: frozen
doc_status: partial
introduced: "CEP 4.0"
deprecated: "CEP 12 = last major runtime (Premiere 25.0)"
eol: null
min_premiere_version: null
api_namespace: CSInterface
languages: [javascript, typescript, html, css, extendscript]
tags: [cep, manifest, csxs, csinterface, evalscript, zxp, bolt-cep, nodejs, debugging, player-debug-mode]
related: [extendscript-core, uxp, panels, debugging, automation, 00-technology-status-matrix]
supersedes: []
superseded_by: [uxp]
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://github.com/Adobe-CEP/CEP-Resources
  - https://github.com/Adobe-CEP/Getting-Started-guides
  - https://github.com/hyperbrew/bolt-cep
  - https://www.npmjs.com/package/bolt-cep
---

# CEP (Common Extensibility Platform)

## TL;DR
- HTML/JS/CSS panels bridged to ExtendScript via `CSInterface.evalScript`. **DEEP-DIVE TARGET — partially seeded.**
- **`legacy/frozen`: CEP 12 (Premiere 25.0) is the last major runtime; loading already degraded in 25.x; AutoSubs CEP panel broke in 2026.**
- Modern build path: **Bolt CEP** (Vite + TS + React/Vue/Svelte, HMR, typed ExtendScript).

## Status & Lifecycle
- **CEP 12 = last major runtime** (Adobe: no new features; security fixes only). CEP 12 shipped with **Premiere 25.0**.
- Unsigned CEP-12 extensions failing to load by **25.2.3** on macOS Sequoia. Plan as if CEP is going away — build UXP for new work.
- See `00-technology-status-matrix`.

## Architecture
Panel = `/CSXS/manifest.xml` + `/client` (HTML/JS/CSS + `CSInterface.js`) + `/host` (`.jsx`). Two runtimes: a Chromium (CEF) UI process and the ExtendScript engine, joined by `evalScript`. **STUB: full lifecycle + folder diagram.**

## API Surface
**Manifest:** `<Host Name="PPRO" Version="[15.0,99.9]"/>`, `<RequiredRuntime Name="CSXS" Version="x.0"/>`, `<CEFCommandLine>` (e.g. `--enable-nodejs`, `--mixed-context`).
**Bridge:** `new CSInterface().evalScript('fn(args)', callback)` — callback receives a STRING.
**CSInterface:** `getHostEnvironment()`, `getSystemPath()`, `addEventListener`, `dispatchEvent`, `openURLInDefaultBrowser`.
**STUB: event/PlugPlug, persistence, theme color sync.**

## Working Examples
See `extendscript-core` Example 5 for the host/client error-enveloped bridge. **STUB: add manifest.xml, .debug file, node-integration example.**

## Limitations
Maintenance-only; no new features. Per-panel Chromium process is heavy. Edits to `manifest.xml`/`.jsx` require host relaunch. **STUB.**

## Common Errors & Gotchas
**Debugging:** set `PlayerDebugMode=1` (macOS `defaults write com.adobe.CSXS.<n> PlayerDebugMode 1`; Windows `HKCU\Software\Adobe\CSXS.<n>` string `PlayerDebugMode=1`), add a `.debug` file assigning a port per host, open `http://localhost:<port>/`. Modern Chrome console may break on a removed `KeyboardEvent.keyIdentifier` — use `chrome://inspect` or older Chrome. **Signing:** `ZXPSignCmd -selfSignedCert` then sign `.zxp`; TSA breakage hit April 2025 (fixed; vite-cep-plugin@1.2.9 bundles fix). **STUB: expand.**

## Workarounds
Use Bolt CEP to avoid manual scaffolding/signing. macOS Spectrum click bug → `enableSpectrum()`. **STUB.**

## Migration
CEP → UXP is a **rewrite** (Adobe: 1:1 parity not intended). `evalScript` bridge disappears; UI moves to Spectrum; logic moves into the single UXP runtime. Bolt UXP is the sibling scaffold. **STUB: step-by-step.**

## Cross-References
- `extendscript-core`
- `uxp`
- `panels`
- `debugging`
- `automation`
- `00-technology-status-matrix`

## Sources
- https://github.com/Adobe-CEP/CEP-Resources
- https://github.com/Adobe-CEP/Getting-Started-guides
- https://github.com/hyperbrew/bolt-cep
- https://www.npmjs.com/package/bolt-cep

