---
id: cpp-native-sdk
title: C++ Native SDK (PrSDK & AE SDK)
category: extensibility
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro 2015"
min_premiere_version: "14.0"
api_namespace: PrSDK
languages: [cpp]
tags: [sdk, native, plugins, c++, video-filters, effects]
related: [extendscript-core, uxp, export-rendering-media-encoder]
sources: [
  "https://developer.adobe.com/console/servicesandapis",
  "Adobe Premiere Pro SDK documentation",
  "Production testing: Premiere 25.x"
]
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# C++ Native SDK (PrSDK & AE SDK)

## TL;DR

**PrSDK = Premiere Pro C++ SDK.** Build native video filters, effects, exporters. **Limitation:** No direct effects API — Premiere effects use AE SDK (After Effects SDK). **Current path:** UXP with `.uxpaddon` C++ hybrids (Premiere 25.6+). **Legacy path:** Direct PrSDK (Premiere 14–24.x, frozen).

**Critical traps:**
- Premiere video filters built on AE SDK, not PrSDK alone
- No AEGP suites in Premiere (AE-only)
- Software render only (no GPU access direct from Premiere)
- Plugin architecture complex; UXP hybrids now preferred

---

## PrSDK Architecture

### What is PrSDK?

Premiere Pro C++ SDK. Covers: exporters, playback plugins, importer/demultiplexers, video filters. Based on plugin architecture (ProPlugin framework).

### Core Plugin Types

| Type | Use Case | Status |
|---|---|---|
| **Exporter** | Custom export formats (ProRes, custom codec) | Current ✅ |
| **Importer** | Import custom media formats | Current ✅ |
| **Playback Engine** | Custom playback codec | Frozen ⚠️ |
| **Video Filter** | Effects (must use AE SDK) | AE SDK only |

**Key limitation:** Video effects require After Effects SDK (AEGP suites), NOT PrSDK directly.

---

## Video Filters: AE SDK Requirement

Premiere effects built on AE SDK (`AfterEffectsSDK.framework` on macOS, `AfterEffectsSDK.dll` on Windows).

```cpp
#include "AE_Effect.h"
#include "AE_EffectCB.h"

typedef struct {
  A_long brightness;
} BrightnessParams;

static PF_Err
Render(PF_InData *in_data, 
        PF_OutData *out_data, 
        PF_ParamDef *params[],
        PF_LayerDef *output)
{
  return PF_Err_NONE;
}
```

**Workflow:**
1. Write AE effect plugin (C++)
2. Register with Premiere via PrSDK exporter interface
3. Premiere loads as native filter (software render, isolated process)

---

## UXP Hybrid Plugins (Modern Path)

Premiere 25.6+: UXP + C++ hybrid plugins (`.uxpaddon`).

**Advantages:**
- UXP handles UI (modern DOM, async)
- C++ only for compute-heavy rendering
- Cleaner separation of concerns
- Better error isolation

---

## Software Rendering Only

**GPU acceleration NOT directly available from Premiere SDK.** All PrSDK effects render in software (CPU).

**Workaround:** Use NVIDIA CUDA or OpenCL (CPU-side API calls). Offload heavy compute to GPU, return results to Premiere.

---

## Export Plugins

Custom exporters built with PrSDK for ProRes, DNxHD, Avid formats.

---

## Importer / Demultiplexer Plugins

Custom media importers used by RED, ARRI, MXF, ProRes RAW importers.

---

## Legacy Path: Direct PrSDK (Frozen)

Premiere 14–24.x: Native PrSDK plugins. **No longer recommended.** Use UXP hybrids (25.6+) for new work.

---

## Build Environment

### macOS
- Xcode 12+
- AfterEffectsSDK.framework
- C++11 minimum

### Windows
- Visual Studio 2017+
- AfterEffectsSDK.dll
- C++11 minimum

---

## Sources

- Adobe Premiere Pro SDK: https://developer.adobe.com/console/servicesandapis
- After Effects SDK: https://github.com/Adobe-CEP/CEP-Resources
- ProRes documentation: https://support.apple.com/en-us/102216
