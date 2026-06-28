---
id: 00-technology-status-matrix
title: Technology Status & Version Matrix
category: meta
status: mixed
stability: active
doc_status: complete
introduced: null
deprecated: null
eol: null
min_premiere_version: null
api_namespace: none
languages: [extendscript, javascript-es3, typescript, cpp]
tags: [lifecycle, status, versions, eol, migration, matrix, cep, uxp, extendscript, qe-dom, prsdk]
related: [extendscript-core, cep, uxp, cpp-native-sdk, reverse-engineering-qe-dom, automation]
supersedes: []
superseded_by: []
sources:
  - https://ppro-scripting.docsforadobe.dev/
  - https://developer.adobe.com/premiere-pro/uxp/
  - https://blog.developer.adobe.com/
  - https://github.com/Adobe-CEP/CEP-Resources
  - https://hyperbrew.co/blog/uxp-plugins-in-premiere-2026/
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.6 / 26.0"
---

# Technology Status & Version Matrix

> **Read this first.** This is the cross-cutting lifecycle reference every other doc defers to.
> When writing Premiere-extension code, resolve the target version here before choosing an API.

## TL;DR
- **ExtendScript is the most capable but actively dying backend.** Adobe froze the API and supports it **through September 2026**.
- **UXP is the current path** (general release in **Premiere 25.6**, Dec 2025) but has an **incomplete API surface** and is **not** 1:1 with ExtendScript + QE DOM.
- **CEP is maintenance-only** — **CEP 12 (Premiere 25.0) is the last major runtime**; loading already degraded in 25.x.
- **QE DOM** is undocumented/unsupported but still the only route to several operations.
- **Native C++ (PrSDK/AE SDK)** and **UXP Hybrid (`.uxpaddon`)** remain mandatory for effects/importers/exporters/heavy compute.

---

## Lifecycle Matrix

| Technology | `status` | `stability` | Introduced | Deprecated / EOL | Authoritative doc |
|---|---|---|---|---|---|
| **ExtendScript (ES3) API** | `legacy` | frozen | Pre-CC; grown through ~12.1.x | API work stopped (2024); **support ends 2026-09** | `extendscript-core` |
| **CEP** | `legacy` | frozen | CEP 4.0 (HTML panels) | **CEP 12 = last major runtime**; no new features | `cep` |
| **QE DOM** (`app.enableQE()`) | `undocumented` | frozen | Internal QA tool | No work planned; breaks between releases | `reverse-engineering-qe-dom` |
| **UXP (panels + scripting)** | `current` | active | GR in **25.6** (beta Dec 2024) | — (incomplete surface) | `uxp` |
| **UXP Hybrid Plugin** (C++ `.uxpaddon`) | `current` | active | 25.6 era | — | `cpp-native-sdk` |
| **C++ Premiere Pro SDK** | `current` | active | Long-standing | — (WinARM-native supported) | `cpp-native-sdk` |
| **Legacy Titles** | `deprecated` | frozen | — | Deprecated & not scriptable | `essential-graphics-mogrt-text` |
| **ESTK (ExtendScript Toolkit)** | `deprecated` | frozen | — | Deprecated 2020 (32-bit; dead on modern macOS) | `debugging` |

### Status definitions
See `PROJECT_SPECIFICATION.md` §5.2. Short form: `current` = use for new work; `legacy` = compat
only, warn; `deprecated` = do not use, name replacement; `undocumented` = last resort, flag risk.

---

## ExtendScript EOL — exact wording

The Premiere Pro Scripting Guide states that as of **November 2025** Premiere moved to UXP-based
extensibility, that ExtendScript integrations **remain supported through September 2026**, and that
Adobe has **stopped additional work on the ExtendScript API**. Treat **2026-09** as the hard
migration deadline for any ExtendScript-dependent pipeline.

## CEP — "last runtime" status

Adobe's developer tech blog states **CEP 12 will be the last major update to CEP**: critical security
issues will still be addressed, but **no new features are planned**. CEP 12 shipped with **Premiere
25.0**. Real-world degradation is already observable:
- Unsigned CEP-12 extensions failing to load by **Premiere 25.2.3** on macOS Sequoia.
- The **AutoSubs** CEP panel broke outright in **Premiere 2026** (no longer loads) — a concrete death signal.

> There is no single Adobe-published "CEP removed in version X" date for Premiere yet. Treat exact
> removal mechanics as **evolving**; verify against the user's build. Plan as if CEP is gone.

## UXP — arrival and gaps

- **General release in Premiere 25.6** (Adobe: "UXP has officially graduated from beta and is now
  available in Adobe Premiere 25.6"). Only **25.6+ / 2026** users can run UXP plugins.
- Bundled **UXP v8.1** in 25.6. No Chromium, no CSInterface bridge — everything runs in one runtime.
- **DOM methods are async (Promises, must `await`)**; property get/set are synchronous for migration ease.
- **Known gaps:** no MOGRT text-blob parity, early builds lacked a sequence-frame-rate getter,
  Stock-panel hangs in some UXP panels, Spectrum Web Components not fully supported in Premiere yet.
- Adobe is explicit that **1:1 CEP→UXP parity is not intended** — migration is a rewrite, not a port.

---

## Version-Number → Marketing-Name Map

| Marketing year | Internal major | Notes |
|---|---|---|
| 2020 | 14.x | New-World scripting changes land ~14.1 (Time objects required) |
| 2021 | 15.x | Host code `PPRO` version "15.0" |
| 2022 | 22.x | (numbering jumps to calendar-aligned majors) |
| 2023 | 23.x | pymiere last broadly tested around 23.1 |
| 2024 | 24.x | HEVC programmatic export still worked (24.6.8) |
| 2025 | 25.x | **CEP 12 = 25.0**; **HEVC block = 25.5**; **UXP GR = 25.6** |
| 2026 | 26.x | **Rebranded "Adobe Premiere"** (dropped "Pro") on 2026-01-20; CEP non-loading |

> Manifests commonly target `Version="[15.0,99.9]"` to future-proof the host-version range.

---

## Decision Guide (which technology for the job)

```
Target users on Premiere 25.6+ / 2026 only?
  └─ YES → UXP (panels/scripting). Native bits → UXP Hybrid (.uxpaddon) or C++ PrSDK.
  └─ NO / mixed install base spanning 25.5 and earlier?
        ├─ Need a panel UI now → CEP + ExtendScript (accept maintenance status); build UXP in parallel.
        ├─ Python pipeline → pymiere (ExtendScript bridge; unmaintained — pin Premiere version).
        ├─ New media format / GPU effect / exporter / importer → C++ PrSDK (AE SDK base for filters).
        └─ Need effects-by-name / ripple / speed / from-UI-only ops → QE DOM (undocumented, last resort).
Text/graphics on timeline (any era)?
  └─ Author a parameterized .mogrt in After Effects → import → patch Source Text JSON.
     There is NO from-scratch title/EGL creation API. See essential-graphics-mogrt-text.
HEVC/H.265 via app.encoder?
  └─ Blocked since 25.5 by design. Use H.264 programmatically, or render HEVC manually in AME.
```

---

## Migration Triggers (when to change the plan)

| Trigger | Action |
|---|---|
| **2026-09** | ExtendScript support ends — migrate all ExtendScript pipelines before this. |
| UXP reaches MOGRT/QE parity | Move text-injection and effect-application off CEP/QE. |
| Adobe announces formal CEP removal date for Premiere | Hard cutover to UXP. |
| Install base crosses to 25.6+ | Drop CEP/ExtendScript builds; UXP-only. |

---

## Cross-References
- `extendscript-core` — the frozen-but-capable backend
- `uxp` — the current target, with its gaps
- `cep` — legacy panel layer, last-runtime status
- `reverse-engineering-qe-dom` — the undocumented escape hatch
- `cpp-native-sdk` — native + hybrid, still mandatory for some tasks
- `essential-graphics-mogrt-text` — why text-on-timeline is special-cased everywhere

## Sources
- Premiere Pro Scripting Guide (ExtendScript EOL wording): https://ppro-scripting.docsforadobe.dev/
- Adobe UXP for Premiere docs + "UXP Arrives in Premiere" blog: https://developer.adobe.com/premiere-pro/uxp/ , https://blog.developer.adobe.com/
- CEP 12 "last runtime" (Adobe tech blog) + CEP Resources: https://github.com/Adobe-CEP/CEP-Resources
- Hyper Brew — UXP/CEP migration analysis: https://hyperbrew.co/blog/uxp-plugins-in-premiere-2026/
- Community threads (Bruce Bullis): MOGRT Source Text, QE DOM status, HEVC block, ticks-per-second
