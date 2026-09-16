---
id: cep
title: CEP (Chromium Embedded Framework) Panels
category: ui-extensibility
status: legacy
stability: frozen
doc_status: complete
introduced: "Premiere Pro CC 2014"
deprecated: "Premiere Pro 25.0"
eol: "2026-12 (estimated)"
min_premiere_version: null
api_namespace: CSInterface
languages: [javascript, extendscript]
tags: [panels, legacy, html5, cef, deprecated-api]
related: [uxp, extendscript-core, automation, best-practices]
superseded_by: [uxp]
sources: [
  "https://github.com/Adobe-CEP/CEP-Resources",
  "https://adobe-cep.github.io/CEP-Resources/",
  "https://ppro-scripting.docsforadobe.dev/",
  "Production testing: Premiere 25.x, 2026"
]
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# CEP (Chromium Embedded Framework) Panels

## TL;DR

**CEP = Chromium Embedded Framework panels.** HTML5 UI + JavaScript + ExtendScript bridge. **Legacy status:** CEP 12 (Premiere 25.0) is the last major runtime. CEP panels fail on macOS Sequoia (25.2.3+) unless signed. Deprecated in Premiere 2026. **For new work:** build UXP (25.6+). **For existing CEP tooling:** maintain, plan migration to UXP.

**Critical traps:**
- Unsigned CEP-12 panels fail silently on macOS 25.2.3+ — requires code signing or migration to UXP
- AutoSubs (stock CEP panel) broke in Premiere 2026 (Issue #571)
- CEP 11 (Premiere 24.x) still works; CEP 12 is final version
- No cross-version CEP compatibility — must target explicitly

---

## CEP Runtime Lifecycle

### What is CEP?

Chromium Embedded Framework v59–v80 (varies by Premiere release). Renders HTML5/CSS/JS in isolated Chromium context. Bridges to ExtendScript via `CSInterface.evalScript()`.

### Version Matrix

| Premiere | CEP | Status | Notes |
|---|---|---|---|
| 2024 (24.x) | CEP 11 | Frozen | Works; EOL imminent |
| 2025 (25.0–25.1) | CEP 12 | Active | Last major version |
| 2025 (25.2.3+) macOS | CEP 12 | Broken unsigned | Requires ZXP signature |
| 2026 (26.x) | CEP 12 | Deprecated | New work → UXP |

**EOL timeline:** ExtendScript full EOL Sept 2026 will likely include CEP deprecation.

---

## Manifest (manifest.xml)

CEP panels discovered via `manifest.xml` in extension bundle. Essential fields:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExtensionManifest Version="10.0" xmlns="http://ns.adobe.com/CSXS/10.0">
  <ExtensionBundleId>com.example.premiere-panel</ExtensionBundleId>
  <ExtensionBundleVersion>1.0.0</ExtensionBundleVersion>
  <ExtensionBundleName>My Premiere Panel</ExtensionBundleName>

  <!-- Premiere 25.0 only = CEP 12 -->
  <Host Name="PrME" Version="[25.0,26.0]" />

  <RequiredRuntime Name="CSXS" Version="10.0" />

  <ExecutionEnvironment>
    <NativeApplication File="libs/PProPanel.dll" />
  </ExecutionEnvironment>

  <UI>
    <Type>Panel</Type>
    <Geometry>
      <Size>
        <Width>400</Width>
        <Height>300</Height>
      </Size>
    </Geometry>
    <MainPath>./html/index.html</MainPath>
  </UI>

  <Extension Id="com.example.premiere-panel.panel">
    <DispatchInfo>
      <Verb Name="show">
        <Message>Show the panel</Message>
      </Verb>
    </DispatchInfo>
  </Extension>

  <!-- REQUIRED on macOS 25.2.3+ -->
  <DigitalSignatures>
    <DigitalSignature File="META-INF/signatures.xml" />
  </DigitalSignatures>
</ExtensionManifest>
```

**Critical fields:**
- `Host Name="PrME" Version="[25.0,26.0]"` → CEP 12 only
- `MainPath` → HTML entry point
- `DigitalSignatures` → REQUIRED for macOS 25.2.3+

---

## CSInterface API Bridge

JavaScript ↔ ExtendScript via `CSInterface`:

```javascript
var csInterface = new CSInterface();

// Invoke ExtendScript (async callback)
csInterface.evalScript(
  'app.project.name',
  function(result) {
    console.log("Project name:", result);
  }
);

// Listen for host events
csInterface.addEventListener("com.adobe.premiere.events.ProjectChanged", function(evt) {
  console.log("Project changed:", evt.data);
});

// Get host environment
var appVersion = csInterface.hostEnvironment.appVersion;     // e.g. "25.0"
var osVersion = csInterface.hostEnvironment.osVersion;       // e.g. "14.0" (Sequoia)

// ERROR HANDLING (ESSENTIAL)
csInterface.evalScript(
  '(function() {' +
  '  try {' +
  '    return app.project.getFooterText(0);' +
  '  } catch(e) {' +
  '    return "ERROR: " + e.toString();' +
  '  }' +
  '})()',
  function(result) {
    if (result.indexOf("ERROR") === 0) {
      console.error("ExtendScript error:", result);
    } else {
      console.log("Result:", result);
    }
  }
);
```

**Key points:**
- `evalScript()` is async (result in callback)
- No automatic error handling — wrap ExtendScript in try/catch
- Result serialized as string, not JSON
- Callback may never fire if ExtendScript hangs

---

## Code Signing (macOS Requirement)

**macOS 25.2.3+: Unsigned CEP panels silently fail to load.**

### Signing with ZXP

```bash
# 1. Create certificate (self-signed, valid 25 years)
ZXPSignCmd -selfSignedCert US CA MyCompany MyPassword cert.p12

# 2. Sign extension folder
ZXPSignCmd -sign ./extension-folder ./output.zxp cert.p12 MyPassword

# 3. Install
# macOS: ~/Library/Application Support/Adobe/CEP/extensions/
# Windows: C:\Program Files\Common Files\Adobe\CEP\extensions\
# Unzip .zxp, restart Premiere
```

**For development:** Test on Windows first (unsigned works), or use CEP 11 (Premiere 24.x).

---

## Common Errors & Gotchas

| Error | Cause | Fix |
|---|---|---|
| Panel doesn't appear | Not signed (macOS 25.2.3+) | Sign ZXP certificate |
| `CSInterface is not defined` | Script outside CEP context | Verify manifest HTML entry |
| `evalScript` callback never fires | ExtendScript hangs/crashes | Add timeout; wrap in try/catch |
| `TypeError: Cannot read property X` | Result is string, not parsed JSON | Parse result or split delimiters |
| AutoSubs broken in Premiere 2026 | CEP panel incompatibility | Wait for patch or migrate to UXP |

---

## Migration Path: CEP → UXP

For new panel work (25.6+):

| Aspect | CEP | UXP | Effort |
|---|---|---|---|
| UI layer | HTML5 + Chromium | UXP DOM (React-like) | Rewrite UI |
| Premiere API | ExtendScript bridge | `require("premierepro")` + async | Rewrite calls |
| Debugging | CEP debugger (old) | UDT (modern) | Learn UDT |
| Signing | ZXP | UXP signature | Different process |

**Recommendation:** Plan UXP migration for all existing CEP projects by mid-2026.

---

## Production Example

See `Examples/extendscript/cep-bridge-safe.jsx` for safe CEP-to-ExtendScript wrapper with error handling.

---

## Sources

- Adobe CEP Resources: https://github.com/Adobe-CEP/CEP-Resources
- PProPanel samples: https://github.com/Adobe-CEP/Samples/tree/master/PProPanel
- Premiere 2026 AutoSubs issue: GitHub #571
- Adobe Developer: https://developer.adobe.com/premiere-pro/
