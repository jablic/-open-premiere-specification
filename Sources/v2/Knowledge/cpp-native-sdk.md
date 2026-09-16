---
id: cpp-native-sdk
title: C++ Premiere Pro SDK & Native Plugins
category: native
status: current
stability: active
doc_status: complete
introduced: "Long-standing"
deprecated: null
eol: null
min_premiere_version: null
api_namespace: PrSDK
languages: [cpp, rust]
tags: [c++, prsdk, ae-sdk, importer, exporter, transmit, video-filter, gpu, uxpaddon, native-plugin, winarm, pipl]
related: [uxp, export-rendering-media-encoder, 00-technology-status-matrix]
supersedes: []
superseded_by: []
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://ppro-plugins.docsforadobe.dev/
  - https://ae-plugins.docsforadobe.dev/ppro/ppro/
  - https://developer.adobe.com/premiere-pro/uxp/
  - https://docs.rs/premiere/latest/premiere/
  - https://docs.rs/after-effects/latest/after_effects/
  - https://github.com/AdobeDocs/uxp-premiere-pro-samples
---

# C++ Premiere Pro SDK & Native Plugins

> Native C++ plugins for importers, exporters, transmit (video output), and video filters/effects.
> **Required** for new media formats, custom GPU effects, frame-buffer access, and export pipelines —
> none of which are achievable via ExtendScript, UXP-JS, or scripting DOM alone. Video filters are
> built on the **After Effects (AE) SDK**; Premiere-specific types use **PrSDK** headers.

## TL;DR
- **Plugin types:** Importer, Exporter, Transmit, Video Filter (effect). Capture/Record/Device-Control removed.
- **Video filters = AE SDK** — you cannot write a filter using PrSDK alone. Premiere loads most AE plugins but **omits all AEGP suites** and uses a **separate GPU entry point**.
- **Premiere sets** `PF_InData->appl_id = 'PrMr'`. Distinguish Pro vs Elements via **App Info Suite**.
- **Distribution:** platform binaries (`.plugin` macOS, `.dll` Windows) + **PiPL** resource; or **UXP Hybrid `.uxpaddon`** paired with a UXP panel (25.6+).
- **WinARM-native** builds supported for Windows on ARM.
- **Rust option:** `after-effects` / `premiere` crates with `define_gpu_filter!` macro — regenerates from `AESDK_ROOT` / `PRSDK_ROOT`.

## Status & Lifecycle
- **Status:** `current` / `active`. Native C++ remains Adobe's path for media I/O, effects, and heavy compute.
- **Not superseded by UXP-JS.** UXP scripting handles project DOM; native work composes via **UXP Hybrid** (`.uxpaddon`) or standalone `.plugin`/`.dll`.
- **WinARM:** Premiere Pro SDK supports **Windows on ARM native** plugin builds (alongside x64).
- **SDK access:** Download from [Adobe Developer — Premiere Pro SDK](https://developer.adobe.com/premiere-pro/) and [After Effects SDK](https://developer.adobe.com/after-effects/) (filters require AE headers).
- See `00-technology-status-matrix`.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Adobe Premiere Pro                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Importer    │  │  Exporter    │  │  Transmit              │ │
│  │  (PrSDK)     │  │  (PrSDK)     │  │  (PrSDK)               │ │
│  │  New formats │  │  Custom enc  │  │  SDI/NDI/frame out     │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Video Filter / Effect (AE SDK + Pr GPU hooks)               ││
│  │  PF_* effect API  +  premiere::GPU entry (Pr-only path)    ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  UXP Hybrid (25.6+) — .uxpaddon native module              ││
│  │  Loaded by UXP panel; C++ for perf / GPU / custom codecs     ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
         ▲                              ▲
         │ PrSDK headers                │ AE SDK (PF_*) + PrSDK GPU
         │ (importers/exporters/        │ (video filters — mandatory)
         │  transmit suites)            │
```

### Plugin types

| Type | SDK base | Purpose | Status |
|---|---|---|---|
| **Importer** | PrSDK | Read new container/codec formats into Premiere | `current` |
| **Exporter** | PrSDK | Write custom export formats / pipelines | `current` |
| **Transmit** | PrSDK | Output frames to external devices (SDI, NDI, custom) | `current` |
| **Video filter (effect)** | **AE SDK** (+ Pr GPU entry) | Real-time and render-time video effects | `current` |
| **UXP Hybrid `.uxpaddon`** | C++ native module API | Native code called from UXP JS panel | `current` (25.6+) |
| Capture | PrSDK | Removed | `deprecated` / removed |
| Record | PrSDK | Removed | `deprecated` / removed |
| Device Control | PrSDK | Removed | `deprecated` / removed |

### AE SDK in Premiere — host behavior

Premiere Pro and Premiere Elements implement the After Effects effect API (PF suite) for video filters. Key host differences vs After Effects (from Adobe AE SDK guide, "Premiere Pro & Other Hosts"):

| Feature | After Effects | Premiere Pro |
|---|---|---|
| AEGP suites (proj/footage/layer access) | Available | **Not available** |
| 16-bit / SmartFX rendering | Supported | **Not supported** |
| 3D auxiliary channels, cameras, lights | Supported | **Not supported** |
| Software render path | Standard PF render | **Software rendering only** on this path |
| GPU render path | AE GPU pipeline | **Separate Pr GPU entry point** (`define_gpu_filter!` in Rust; Pr GPU suites in C++) |
| `PF_InData->appl_id` | AE id | **`'PrMr'`** in both Pro and Elements |

Premiere's `version.major` / `version.minor` in `PF_InData` track Premiere releases — **not** AE feature parity at the same version number. Use **App Info Suite** (PrSDK) to distinguish Premiere Pro vs Premiere Elements.

### Typical C++ project layout

```
MyPlugin/
├── MyPlugin.cpp           # Entry points / selector dispatch
├── MyPlugin.h
├── PiPL/                  # PiPL resource (plugin metadata for AE-style plugins)
│   └── MyPlugin.r
├── Mac/
│   └── Info.plist
├── Win/
│   └── MyPlugin.rc
└── SDK/                   # Symlink or copy PrSDK + AESDK headers
    ├── PrSDK/
    └── AE_SDK/
```

Platform output:
- **macOS:** `MyPlugin.plugin` bundle → `/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore/` (or user path)
- **Windows:** `MyPlugin.dll` → `C:\Program Files\Adobe\Common\Plug-ins\7.0\MediaCore\`

Exact MediaCore version folder (7.0, etc.) varies by Premiere major — verify against SDK sample projects for your target version.

## API Surface

### PrSDK headers (representative)

Premiere-specific functionality lives in `PrSDK*.h` headers shipped with the Premiere Pro SDK:

| Header | Domain |
|---|---|
| `PrSDKImport.h` | Importer plugin entry points and records |
| `PrSDKExport.h` | Exporter plugin entry points |
| `PrSDKTransmit.h` | Transmit plugin (frame output) |
| `PrSDKTypes.h` | Core Premiere types |
| `PrSDKString.h` | Premiere string type |
| `PrSDKStreamLabel.h` | Stream labeling (e.g. stereo L/R) |
| `PrSDKAESupport.h` | AE-effect support hooks in Premiere |
| `PrSDKColorSEICodes.h` | Color / SEI metadata |
| `PrSDKAppInfoSuite.h` | Distinguish Pro vs Elements, host queries |
| `PrSDKPPix*.h` | Pixel buffer access (PPix suite family) |
| `PrSDKGPU*.h` | GPU device / image processing suites |
| `PrSDKSequence*.h` | Sequence info / render suites |
| `PrSDKTimeSuite.h` | Time/timeline utilities |
| `PrSDKMemoryManagerSuite.h` | Host memory management |

Importer plugins respond to **selectors** (message types). Common importer records/selectors:

| Selector / record | Purpose |
|---|---|
| `imImportInfoRec` | Plugin registration info |
| `imIndFormatRec` / `xfIsMovie` | Probe whether file is supported |
| `imQueryStreamLabel` | Label audio streams (stereo: L=0, R=1) |
| `imGetPreferredFrameSize` | Preferred frame dimensions |
| `imPerformSourceSettingsCommand` | Source Settings UI / config |
| `imImportAudio` / `imImportVideo` | Frame/audio read paths |
| `imGetTimeInfo` | Duration / timebase |

Exporter and Transmit plugins follow parallel **export/transmit selector** patterns — see `PrSDKExport.h`, `PrSDKTransmit.h`, and [ppro-plugins.docsforadobe.dev](https://ppro-plugins.docsforadobe.dev/).

### AE SDK headers (video filters — mandatory)

Video filters use the standard AE **PF_** effect model:

| Header / concept | Purpose |
|---|---|
| `AE_Effect.h` | Core effect entry (`EffectMain` selector dispatch) |
| `AE_EffectCB.h` | Callback suites passed in `PF_InData` |
| `AE_EffectCBSuites.h` | Suite acquisition |
| `AE_EffectSuites.h` | Utility suites (many unavailable in Premiere — see Limitations) |
| `AEConfig.h` | Platform / feature flags |
| PiPL resource | Plugin name, category, flags — required for host registration |

**Premiere GPU filters** register an additional GPU render entry (not the standard AE GPU path). In Rust: `premiere::define_gpu_filter!`. In C++: use PrSDK GPU suites (`PrSDKGPUDeviceSuite.h`, `PrSDKGPUImageProcessingSuite.h`) per SDK samples.

### UXP Hybrid `.uxpaddon`

Premiere **25.6+** UXP panels can load a native C++ module alongside JS:

```
my-uxp-plugin/
├── manifest.json          # UXP manifest v5; declares native module
├── index.js               # UXP panel logic
└── native/
    └── mymodule.uxpaddon  # Platform-specific native binary
```

Use Hybrid when:
- UXP-JS lacks API for your task but you want a **single `.ccx` deliverable**.
- You need GPU/codec performance without a separate MediaCore `.plugin` install.
- You are migrating off CEP Node.js bridges for compute-heavy work.

See Adobe [uxp-premiere-pro-samples](https://github.com/AdobeDocs/uxp-premiere-pro-samples) and `uxp` doc. Hybrid does **not** replace MediaCore importers/exporters — those still install as `.plugin`/`.dll` unless wrapped.

### App identification

```cpp
// C++ — in effect/importer code
// Premiere Pro and Elements both set:
// PF_InData->appl_id == 'PrMr'

// To distinguish Pro vs Elements, acquire App Info Suite from PrSDK:
// PrSDKAppInfoSuite → query host application variant
```

## Working Examples

### 1. Importer selector skeleton (C++)
```cpp
// C++ — Premiere Pro SDK — Importer plugin (simplified)
#include "PrSDKImport.h"

PREMPLUGENTRY DllExport xImportEntry(
    csSDK_int32 selector,
    imImporterInstanceRec* instanceRec,
    void* param)
{
    switch (selector) {
        case imSelectorStartup:
            // Register capabilities, allocate instance data
            return imImportInfoRec(/* ... */);
        case imSelectorInit:
            return imInit(instanceRec);
        case imSelectorIndFormat:
            // Probe file — set xfIsMovie if recognized
            return imIndFormat(instanceRec, (imIndFormatRec*)param);
        case imSelectorImportVideo:
            return imImportVideo(instanceRec, (imImportVideoRec*)param);
        case imSelectorImportAudio:
            return imImportAudio(instanceRec, (imImportAudioRec*)param);
        case imSelectorShutdown:
            return imShutdown(instanceRec);
        default:
            return imUnsupported;
    }
}
```

Consult SDK sample importers for full record population and memory ownership rules.

### 2. AE-style video filter entry (C++)
```cpp
// C++ — AE SDK effect — also loaded by Premiere (software render path)
#include "AE_Effect.h"
#include "AE_EffectCB.h"

DllExport PF_Err EffectMain(
    PF_Cmd cmd,
    PF_InData* in_data,
    PF_OutData* out_data,
    PF_ParamDef* params[],
    PF_LayerDef* output,
    void* extra)
{
    switch (cmd) {
        case PF_Cmd_ABOUT:
        case PF_Cmd_GLOBAL_SETUP:
            // Register params, declare flags (avoid SmartFX/16-bit flags in Premiere)
            break;
        case PF_Cmd_PARAMS_SETUP:
            break;
        case PF_Cmd_RENDER:
            // Software pixel loop — Premiere uses this path for CPU render
            break;
        case PF_Cmd_USER_CHANGED_PARAM:
            break;
        default:
            break;
    }
    return PF_Err_NONE;
}
```

For GPU acceleration in Premiere, add the **Premiere-specific GPU entry** (PrSDK GPU samples / Rust macro below) — do not assume AE's GPU path works unchanged.

### 3. Rust GPU filter (premiere crate)
```rust
// Rust — Premiere GPU filter via premiere crate
// Cargo.toml: after-effects + premiere (with_premiere cfg in build.rs)

use premiere::{define_gpu_filter, GpuFilter, GpuFilterInstance, PixelFormat};

struct MyGpuFilter;

impl GpuFilter for MyGpuFilter {
    fn render(&self, instance: &mut GpuFilterInstance) -> Result<(), premiere::Error> {
        // Zero-copy GPU path — see Gyroflow / ntsc-rs for production examples
        Ok(())
    }
}

define_gpu_filter!(MyGpuFilter);
```

Build:
```bash
export AESDK_ROOT=/path/to/AfterEffectsSDK
export PRSDK_ROOT=/path/to/PremiereProSDK
# build.rs: println!("cargo:rustc-cfg=with_premiere");
cargo build --release
```

Regenerate bindings when SDK versions change. Pre-generated bindings ship with the crate for out-of-box builds.

### 4. Rust project setup (build.rs)
```rust
// build.rs — enable Premiere SDK features
fn main() {
    println!("cargo:rustc-cfg=with_premiere");
    // pipl crate generates PiPL resource from build script
}
```

Use **`just build`** / **`just release`** (from `AdobePlugin.just`) for debug (panic catching + logging) vs optimized builds. Debug logs: **Console** (macOS), **DbgView** (Windows).

## Limitations

### Hard walls
- **You cannot write a video filter using PrSDK alone.** The base effect engine is the **AE SDK** (`PF_*`). PrSDK adds Premiere-specific GPU/I/O suites on top.
- **No AEGP suites in Premiere.** Effects cannot use AEGP project/footage/layer manipulation that works in After Effects.
- **No 16-bit or SmartFX** in Premiere's AE-host implementation.
- **No 3D auxiliary channels** (cameras, lights, aux channels) in Premiere.
- **Software render path only** for standard PF render in Premiere — GPU requires the **separate Pr GPU entry point**.
- **Scripting/UXP cannot replace** importers, exporters, transmit, or deep pixel/GPU effects — native code is mandatory.
- **PiPL / code signing / notarization** (macOS) and **DLL load paths** (Windows) are common ship blockers — not handled by scripting tooling.

### Practical constraints
- Public SDK may lag latest Premiere features — verify against target build.
- Importer/exporter UI is native (not HTML) — unlike CEP/UXP panels.
- **MediaCore vs UXP Hybrid** — choose delivery model early; importers still typically ship as MediaCore plugins.
- Rust bindings coverage is extensive but **not every suite is wrapped** — check [docs.rs/premiere](https://docs.rs/premiere/latest/premiere/) suite tables for gaps (🔳 = not wrapped).

## Common Errors & Gotchas
- **Symptom:** Plugin missing in Premiere Effects list. **Cause:** PiPL not linked, wrong MediaCore folder, or missing platform bundle structure. **Fix:** Compare against SDK sample; check `Plugin Loading.log` (AE) or Premiere plugin scan logs.
- **Symptom:** Plugin loads in AE but not Premiere. **Cause:** AEGP dependency, SmartFX/16-bit flags, or AE-only suite usage. **Fix:** Remove AEGP calls; use PF render compatible with Premiere host flags.
- **Symptom:** GPU path never invoked. **Cause:** Only implemented `PF_Cmd_RENDER` (CPU) without Pr GPU registration. **Fix:** Implement Premiere GPU entry (`define_gpu_filter!` or C++ GPU sample).
- **Symptom:** `appl_id` check fails. **Cause:** Assuming AE host. **Fix:** Accept `'PrMr'`; branch behavior with App Info Suite.
- **Symptom:** Stereo audio channels swapped/mono. **Cause:** Missing `imQueryStreamLabel` (L=0, R=1). **Fix:** Implement stream label selector.
- **Symptom:** macOS plugin won't load. **Cause:** Unsigned / not notarized bundle, bad `Info.plist` / `PkgInfo`. **Fix:** Sign with Developer ID; validate bundle structure. Run Premiere under debugger.
- **Symptom:** Windows ARM build fails. **Cause:** x64-only dependencies. **Fix:** Rebuild all deps for ARM64; use WinARM-native SDK toolchain.
- **Symptom:** Rust build can't find SDK. **Cause:** Missing `AESDK_ROOT` / `PRSDK_ROOT`. **Fix:** Export env vars; add `with_premiere` cfg.

## Workarounds
- **UXP Hybrid `.uxpaddon`** — ship native compute with a UXP panel without asking users to manually copy MediaCore plugins. Best for 25.6+ single-package installs. `confidence: high`.
- **Rust `after-effects` / `premiere` crates** — safer bindings, PiPL generation, cross-platform build scripts; used in production (Gyroflow, ntsc-rs). `confidence: high`.
- **CPU-only filter** — implement `PF_Cmd_RENDER` only; skip GPU complexity at cost of performance. `confidence: high`.
- **External encoder/transcoder** — when exporter API is overkill, queue ffmpeg/AME via ExtendScript/UXP and keep native plugin out of critical path. `confidence: medium`.
- **Dual plugin binaries** — ship separate AE and Premiere-tuned builds only if feature sets diverge (rare; prefer one binary with host checks). `confidence: low`.

## Migration

Native C++ is **not** superseded by UXP-JS. The relationship is **compositional**:

| Scenario | Path |
|---|---|
| New GPU effect / codec / importer | C++ MediaCore plugin (same as before) |
| Panel + native perf module (25.6+) | UXP panel + `.uxpaddon` Hybrid |
| Legacy CEP Node compute bridge | Replace with Hybrid addon or MediaCore plugin |
| ExtendScript-only automation | Move DOM to UXP-JS; keep native for pixels/codecs |

**CEP/ExtendScript → Native:** use native when hitting DOM limits (custom export format, unsupported import, GPU pixel shaders, transmit to hardware). Do not embed C++ inside CEP — ship a MediaCore plugin or Hybrid addon and call it from panel JS via a thin bridge (UXP native bindings or file/socket protocol).

**Standalone MediaCore → Hybrid:** optional packaging change for 25.6+; importers/exporters often remain standalone MediaCore installs because Hybrid targets panel-bundled native helpers, not system-wide format handlers.

## Cross-References
- `uxp` — UXP Hybrid `.uxpaddon`, manifest v5, 25.6+ panel integration
- `export-rendering-media-encoder` — scripted export vs native exporter plugins
- `panels` — when UI is UXP vs when native has no panel at all
- `00-technology-status-matrix` — native + Hybrid status, decision guide
- [docs.rs/premiere](https://docs.rs/premiere/latest/premiere/) — Rust bindings, suite coverage tables
- [docs.rs/after-effects](https://docs.rs/after-effects/latest/after_effects/) — AE SDK Rust bindings (filters)

## Sources
- Premiere Pro C++ SDK Guide: https://ppro-plugins.docsforadobe.dev/
- After Effects SDK — Premiere Pro & Other Hosts: https://ae-plugins.docsforadobe.dev/ppro/ppro/
- Adobe Premiere Pro UXP / Hybrid samples: https://developer.adobe.com/premiere-pro/uxp/ , https://github.com/AdobeDocs/uxp-premiere-pro-samples
- Rust `premiere` crate: https://docs.rs/premiere/latest/premiere/
- Rust `after-effects` crate: https://docs.rs/after-effects/latest/after_effects/
- Production Rust plugins: Gyroflow (GPU), ntsc-rs (CPU/GPU effect) — referenced in premiere crate docs
