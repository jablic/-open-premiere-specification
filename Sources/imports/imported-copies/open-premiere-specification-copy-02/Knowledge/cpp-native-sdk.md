---
id: cpp-native-sdk
title: C++ Premiere Pro SDK & Native Plugins
category: native
status: current
stability: active
doc_status: partial
introduced: "Long-standing"
deprecated: null
eol: null
min_premiere_version: null
api_namespace: PrSDK
languages: [cpp, rust]
tags: [c++, prsdk, ae-sdk, importer, exporter, transmit, video-filter, gpu, uxpaddon, native-plugin]
related: [uxp, export-rendering-media-encoder, 00-technology-status-matrix]
supersedes: []
superseded_by: []
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://ppro-plugins.docsforadobe.dev/
  - https://ae-plugins.docsforadobe.dev/ppro/ppro/
  - https://docs.rs/premiere/latest/premiere/
---

# C++ Premiere Pro SDK & Native Plugins

## TL;DR
- Native C++ SDK for importers, exporters, transmit, and video filters (effects). **Partially seeded.**
- **Required** for new media formats, custom GPU effects/transitions, exporters, and frame-buffer access — none achievable via scripting/UXP-JS.
- Video filters are built on the **AE SDK** (Premiere lacks AEGP suites, uses software-render entry separate from GPU).

## Status & Lifecycle
- `current`; WinARM-native supported. Also surfaces as **UXP Hybrid `.uxpaddon`** modules paired with UXP JS.
- See `00-technology-status-matrix`.

## Architecture
Plugin types: Importers, Exporters, Transmit (incl. dual-audio), video filters. Capture/Record/Device-Control were removed. Premiere loads most AE plugins but is **missing all AEGP suites**, uses **software rendering only** (separate GPU entry point), lacks 16-bit/SmartFX/3D aux-channel support. Both PPro and AE set `PF_InData->appl_id = 'PrMr'`. **STUB: per-type lifecycle.**

## API Surface
Headers `PrSDK*.h` (`PrSDKString`, `PrSDKStreamLabel.h`, `PrSDKAESupport.h`, `PrSDKColorSEICodes.h`, ...). Importer selectors: `imImportInfoRec`, `imIndFormatRec` (`xfIsMovie`), `imQueryStreamLabel` (stereo L=0/R=1), `imGetPreferredFrameSize`, `imPerformSourceSettingsCommand`. Distinguish PPro/Elements via App Info Suite. **STUB: selector tables.**

## Working Examples
Rust bindings: `after-effects`/`premiere` crates; `premiere::define_gpu_filter!` for GPU. Regenerate from `AESDK_ROOT`/`PRSDK_ROOT`. **STUB: minimal importer + GPU-filter skeletons.**

## Limitations
'You can't write a video filter using only the Premiere SDK — the base engine uses the AE SDK.' No AEGP suites in Premiere. **STUB.**

## Common Errors & Gotchas
**STUB: build-system, entitlement, signing notes.**

## Workarounds
For perf-critical work alongside a UXP plugin, use a **UXP Hybrid `.uxpaddon`** instead of a standalone CEP/native bridge. **STUB.**

## Migration
Native isn't superseded by UXP; they compose (Hybrid plugins). **STUB.**

## Cross-References
- `uxp`
- `export-rendering-media-encoder`
- `00-technology-status-matrix`

## Sources
- https://ppro-plugins.docsforadobe.dev/
- https://ae-plugins.docsforadobe.dev/ppro/ppro/
- https://docs.rs/premiere/latest/premiere/

