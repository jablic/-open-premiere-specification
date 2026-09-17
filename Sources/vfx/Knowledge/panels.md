---
id: panels
title: CEP & UXP Panels Development
category: ui-extensibility
status: mixed
stability: active
doc_status: partial
introduced: "Premiere Pro CC 2014"
min_premiere_version: null
api_namespace: CSInterface|premierepro
languages: [javascript, extendscript]
tags: [panels, ui, cep, uxp, development]
related: [cep, uxp, extendscript-core, best-practices]
sources: [
  "https://github.com/Adobe-CEP/CEP-Resources",
  "https://developer.adobe.com/premiere-pro/uxp/",
  "Production testing"
]
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# CEP & UXP Panels Development

## TL;DR

**CEP Panels (Legacy):** HTML5 + JavaScript + ExtendScript bridge. Works until Premiere 2026. Requires code signing on macOS 25.2.3+. **UXP Panels (Modern):** Async-first DOM, modern DevTools (UDT), recommended for new work (25.6+).

**Critical differences:**
- CEP: Synchronous, Chromium-based, CEP debugger
- UXP: Asynchronous, React-like DOM, UDT debugger

---

## CEP Panel Structure
Limited features; recommend upgrading to UXP.

---

## Debugging UXP

UDT (UXP Developer Tool):
```bash
npm install -g @adobe/udt
udt --watch ./plugin-folder
```

Modern DevTools-like interface, async debugging, breakpoints.

---

## Sources

- CEP Resources: https://github.com/Adobe-CEP/CEP-Resources
- UXP Guide: https://developer.adobe.com/premiere-pro/uxp/
