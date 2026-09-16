---
id: security-signing
title: Security, Signing & Code Protection
category: operations
status: current
stability: active
doc_status: complete
introduced: "2024"
min_premiere_version: null
api_namespace: null
languages: null
tags: [security, signing, zxp, code-protection, macOS]
related: [cep, panels, best-practices]
sources: []
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Security, Signing & Code Protection

## TL;DR

CEP ZXP signing mandatory on macOS 25.2.3+. UXP has built-in signing (simpler). ExtendScript/UXP scripts run locally without signing. C++ plugins require OS-level code signing (macOS notarization).

---

## CEP ZXP Signing (Required macOS 25.2.3+)

Create self-signed certificate:
```bash
ZXPSignCmd -selfSignedCert US CA MyCompany MyPassword cert.p12
```

Sign extension:
```bash
ZXPSignCmd -sign ./my-extension ./my-extension.zxp cert.p12 MyPassword
```

Install: unzip .zxp into Adobe/CEP/extensions folder, restart Premiere.

---

## UXP Signing (Built-In)

UXP plugins signed by Adobe automatically. No manual ZXP signing required. Manifest.json declares id, name, requiredApiVersion.

---

## ExtendScript/UXP Script Security

No signing required for local scripts. Risks: file access, limited network (UXP can fetch), code injection from unsanitized input. Always validate file paths (reject ".." sequences).

---

## C++ Plugin Signing (macOS Notarization)

Native C++ plugins require macOS notarization (Monterey+) via codesign + xcrun notarytool submit workflow.

---

## Common Security Issues

| Issue | Risk | Fix |
|---|---|---|
| Unsigned CEP on macOS 25.2.3+ | Critical | Sign ZXP |
| Hardcoded API keys | High | Use environment variables |
| File path injection | High | Validate paths (no "..") |
| Network HTTPS | Medium | Use HTTPS only |
| Plugin DLL tampering | Low | Code signing + notarization |

---

See also: cep.md, uxp.md, best-practices.md
