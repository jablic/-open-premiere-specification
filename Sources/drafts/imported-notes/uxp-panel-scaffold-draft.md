---
id: uxp-panel-scaffold
title: UXP Panel Scaffold & Manifest v5
category: ui-extensibility
status: current
stability: active
doc_status: complete
introduced: "GR in Premiere 25.6"
deprecated: null
eol: null
min_premire_version: "25.6"
api_namespace: uxp
languages: [javascript, typescript, html, css]
tags: [uxp, manifest-v5, spectrum-web-components, permission-model, panel-skeleton, ccx]
related: [uxp, cep, debugging, panels, 00-technology-status-matrix]
supersedes: []
superseded_by: []
sources:
  - https://developer.adobe.com/premiere-pro/uxp/resources/manifest-v5-reference/
  - https://developer.adobe.com/premiere-pro/uxp/resources/fundamentals/apis/
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.6 / 26.0"
---

# UXP Panel Scaffold & Manifest v5

> Minimal, production-ready scaffolding for UXP panels in Premiere Pro 25.6+. Covers `manifest.json` v5, permission model, Spectrum Web Components baseline, and runtime lifecycle.

## TL;DR
- **Manifest v5** replaces CEP's `.csxs`. Permissions are declarative (`requiredPermissions`).
- **No Chromium bridge**: UI and logic run in a single sandboxed JS engine. `require('premierepro')` gives async DOM access.
- **Spectrum Web Components** are the only supported UI primitives. No raw HTML/CSS hackery.
- Distribution: `.ccx` via UPIA or Adobe CC Marketplace. Signing handled by Adobe's toolchain.

## Status & Lifecycle
- `current`. Requires **Premiere 25.6+**. CEP is no longer relevant for new panels.
- Manifest format is stable in v5; watch Adobe's developer blog for permission model tweaks.

## Architecture
