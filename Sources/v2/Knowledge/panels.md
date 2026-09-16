---
id: panels
title: Panels (CEP vs UXP)
category: ui-extensibility
status: mixed
stability: active
doc_status: complete
introduced: "CEP 4.0; UXP GR Premiere 25.6"
deprecated: null
eol: null
min_premiere_version: null
api_namespace: none
languages: [javascript, typescript, html, css]
tags: [panel, cep-panel, uxp-panel, spectrum, ui, comparison, migration]
related: [cep, uxp, ai-integration, 00-technology-status-matrix]
supersedes: []
superseded_by: []
sources:
  - https://developer.adobe.com/premiere-pro/uxp/
  - https://github.com/Adobe-CEP/CEP-Resources
  - https://github.com/hyperbrew/bolt-cep
  - https://hyperbrew.co/blog/uxp-plugins-in-premiere-2026/
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
---

# Panels (CEP vs UXP)

> User-facing panel extensions: **CEP** (legacy, Chromium-based) vs **UXP** (current, Spectrum-based).
> New panels for Premiere **25.6+** → UXP. Maintain CEP only for legacy install bases.

## TL;DR
- **CEP:** HTML/CSS/JS in Chromium (CEF) + `CSInterface.evalScript` bridge to ExtendScript. `legacy`.
- **UXP:** Spectrum Web Components in sandboxed JS runtime + `require('premierepro')`. `current` (25.6+).
- **No 1:1 port** — Adobe explicitly does not intend CEP→UXP parity.
- Build scaffolds: **Bolt CEP** (legacy), **Bolt UXP** / Adobe samples (current).

## Status & Lifecycle

| Platform | Status | Min Premiere | Notes |
|---|---|---|---|
| CEP | `legacy` | All (degrading) | CEP 12 = last runtime (25.0); broke in 2026 for some panels |
| UXP Panel | `current` | **25.6+** | GR Dec 2025; UXP v8.1 bundled |
| UXP Hybrid | `current` | **25.6+** | Panel + `.uxpaddon` native module |

See `00-technology-status-matrix`, `cep`, `uxp`.

## Architecture

### CEP panel (legacy)
```
┌─────────────────────────────────────┐
│  CEF Chromium Process (panel UI)    │
│  index.html + CSInterface.js        │
│         │ evalScript(string, cb)    │
└─────────┼───────────────────────────┘
          ▼
┌─────────────────────────────────────┐
│  ExtendScript Engine (host .jsx)    │
│  app.* DOM (sync)                   │
└─────────────────────────────────────┘
```

### UXP panel (current)
```
┌─────────────────────────────────────┐
│  Single UXP Runtime (in-process)    │
│  Spectrum UI + require('premierepro')│
│  async DOM (await) + executeTransaction│
│  optional: .uxpaddon (C++ hybrid)   │
└─────────────────────────────────────┘
```

## Comparison Matrix

| Feature | CEP | UXP |
|---|---|---|
| UI framework | Any HTML/CSS (React/Vue ok) | Spectrum Web Components (limited in Premiere) |
| Host API access | `evalScript` → ExtendScript | `require('premierepro')` native module |
| Async model | Callback-based evalScript | `await` on DOM methods |
| Node.js | Optional via manifest CEF flags | No Node — UXP `fs`/`os` modules |
| Chromium DevTools | Yes (PlayerDebugMode + .debug) | UXP Developer Tool (UDT) |
| Distribution | `.zxp` (ZXPSignCmd) | `.ccx` (UPIA / Marketplace) |
| Premiere min version | Broad (15.0+) | **25.6+** |
| MOGRT text editing | Via ExtendScript bridge | **No parity yet** |
| QE DOM access | Via ExtendScript | Not available |
| Process overhead | Per-panel CEF process | Single shared runtime |
| Future | Maintenance-only | Active development |

## API Surface
Defer to technology-specific docs:
- CEP bridge, manifest, signing → `cep`
- UXP manifest v5, permissions, DOM → `uxp`
- AI/LLM from panel → `ai-integration`

### Panel entry points

| CEP | UXP |
|---|---|
| `/CSXS/manifest.xml` | `/manifest.json` (v5) |
| `<ExtensionList>` + `<DispatchInfo>` | `entrypoints` + `requiredPermissions` |
| Host `PPRO` version range | `host.minVersion` |

## Working Examples

See `cep` for manifest + evalScript bridge; `uxp` for async DOM panel skeleton.

**Decision template:**
```
if (minPremiereVersion >= 25.6 && !needsMOGRTTextBlob && !needsQEDOM) {
  → build UXP panel
} else if (needsMOGRTTextBlob || needsQEDOM || minVersion < 25.6) {
  → build CEP panel (legacy path) + plan UXP migration
} else {
  → UXP with CEP fallback build
}
```

## Limitations
- UXP panels **cannot run on Premiere < 25.6**.
- Spectrum Web Components **not fully supported** in Premiere UXP yet — some UI patterns fail.
- CEP panels **fail to load** on newer Premiere builds without proper signing/debug mode.
- Stock panel integration in UXP can cause **hangs** (known 25.6 issue).
- Single panel cannot mix CEP UI + UXP DOM — pick one runtime per deliverable.

## Common Errors & Gotchas
- **Symptom:** Panel doesn't appear in Window menu. **Cause:** Unsigned extension / wrong manifest host version. **Fix:** Enable debug mode; verify `PPRO` version range; sign ZXP.
- **Symptom:** UXP panel loads but DOM calls fail. **Cause:** Missing `await` or no active project. **Fix:** See `uxp` gotchas.
- **Symptom:** CEP works in 25.0 but not 2026. **Cause:** CEP deprecation. **Fix:** Migrate to UXP.
- **Symptom:** AI suggests `CSInterface` in UXP code. **Cause:** Wrong runtime. **Fix:** UXP has no CSInterface — use `premierepro` module.

## Workarounds
- **Dual-build strategy:** Ship CEP for <25.6, UXP for 25.6+ (Hyper Brew Bolt supports both).
- For MOGRT text until UXP parity: keep CEP+ExtendScript helper panel alongside UXP UI shell.
- Use `openURLInDefaultBrowser` (CEP) or UXP `shell` APIs for external docs/auth flows.

## Migration
CEP → UXP is a **rewrite**, not a port:
1. Replace `evalScript` bridge with `require('premierepro')` async calls.
2. Replace HTML UI with Spectrum components.
3. Replace `.zxp` signing with `.ccx` / UPIA workflow.
4. Audit every ExtendScript call for UXP equivalent — many gaps remain.
5. Drop QE DOM dependencies or isolate behind version-gated module.

See `cep` §Migration and `uxp` §Migration.

## Cross-References
- `cep` — CEP deep dive
- `uxp` — UXP deep dive
- `ai-integration` — LLM panels, MCP
- `00-technology-status-matrix` — lifecycle authority
- `debugging` — DevTools per runtime

## Sources
- https://developer.adobe.com/premiere-pro/uxp/
- https://github.com/Adobe-CEP/CEP-Resources
- https://github.com/hyperbrew/bolt-cep
- https://hyperbrew.co/blog/uxp-plugins-in-premiere-2026/
