---
id: panels
title: CEP & UXP Panels Development
category: ui-extensibility
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2014"
min_premiere_version: "14.0"
api_namespace: CSInterface|premierepro
languages: [javascript, extendscript, html, css]
tags: [panels, ui, cep, uxp, development, flexbox, debugging, manifest]
related: [cep, uxp, extendscript-core, best-practices, debugging, ui-theming-and-responsive-panels]
sources: [
  "https://github.com/Adobe-CEP/CEP-Resources",
  "https://developer.adobe.com/premiere-pro/uxp/",
  "Production testing (Premiere 25.x)",
  "Examples/cep-theme-sync-panel.*",
  "Examples/uxp-responsive-rubber-panel.html"
]
confidence: high
last_verified: "2026-07-01"
verified_against_version: "25.6"
---

# CEP & UXP Panels Development

## TL;DR

**CEP Panels (Legacy):** HTML5 + JavaScript + ExtendScript bridge. Works until Premiere 2026. Requires code signing on macOS 25.2.3+. **UXP Panels (Modern):** Async-first DOM, modern DevTools (UDT), recommended for new work (25.6+).

**Critical differences:**
- CEP: Synchronous, Chromium-based, CEP debugger
- UXP: Asynchronous, React-like DOM, UDT debugger

---

## CEP Panel Architecture (Legacy, EOL 2026)

### Project Structure

```
my-panel/
├── CSXS/
│   └── manifest.xml          # Panel registration & capabilities
├── css/
│   └── styles.css
├── js/
│   ├── csinterface.js        # Adobe CEP library
│   └── index.js              # Panel logic
├── jsx/
│   └── hostscript.jsx        # ExtendScript code (runs in Premiere)
└── index.html                # Panel UI
```

### manifest.xml (Critical)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExtensionManifest xmlns="http://www.adobe.com/products/extendscript/manifest"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  
  <ExtensionBundleVersion>1.0</ExtensionBundleVersion>
  <ExtensionBundleId>com.example.mypanel</ExtensionBundleId>
  
  <Extension Id="com.example.mypanel">
    <Name>My Panel</Name>
    <Version>1.0</Version>
    
    <UI>
      <Type>Panel</Type>
      <Geometry>
        <Size>
          <Width>300</Width>
          <Height>400</Height>
        </Size>
      </Geometry>
    </UI>
    
    <RequiredRuntime>
      <Name>CSXS</Name>
      <Version>12.0</Version>  <!-- CEP 12 for Premiere 25.x -->
    </RequiredRuntime>
  </Extension>
</ExtensionManifest>
```

### Panel → ExtendScript Communication (CEP)

```javascript
// In panel JavaScript (index.js)
var csInterface = new CSInterface();

// Send message to ExtendScript
function callExtendScript(funcName, args) {
  var jsxFile = csInterface.getSystemPath(SystemPath.EXTENSION) + "/jsx/hostscript.jsx";
  csInterface.evalFile(jsxFile);
  
  var result = csInterface.evalScript(funcName + "('" + args.join("','") + "')");
  return result;
}

// Listen for messages from ExtendScript
csInterface.addEventListener(CSInterface.CONSOLE_MESSAGE, function(event) {
  console.log("ExtendScript: " + event.data);
});

// Usage
var seqName = callExtendScript("getActiveSequenceName");
document.getElementById("output").innerText = seqName;
```

```javascript
// In ExtendScript (jsx/hostscript.jsx)
function getActiveSequenceName() {
  var seq = app.project.activeSequence;
  return seq ? seq.name : "No sequence";
}

// Send message back to panel
$.writeln("Sequence loaded");
```

---

## UXP Panel Architecture (Modern, 25.6+)

### Project Structure

```
my-uxp-panel/
├── src/
│   ├── index.js              # Entry point
│   ├── index.html
│   ├── style.css             # UXP Flexbox styles
│   └── components/           # Optional component modules
├── package.json
├── uxp.config.json
└── manifest.json             # UXP plugin manifest
```

### package.json (UXP)

```json
{
  "name": "my-uxp-panel",
  "version": "1.0.0",
  "description": "My UXP panel for Premiere",
  "main": "src/index.js",
  "dependencies": {
    "premierepro": "^1.0.0"
  },
  "devDependencies": {
    "@adobe/udt": "latest"
  }
}
```

### manifest.json (UXP Plugin)

```json
{
  "id": "com.example.mypanel",
  "name": "My UXP Panel",
  "version": "1.0.0",
  "requiredHostMinVersion": {
    "premierepro": "25.6"
  },
  "requiredApiVersion": "1.0.0",
  "uiEntryPoints": [
    {
      "type": "panel",
      "name": "My Panel"
    }
  ],
  "requiredPermissions": []
}
```

### UXP Panel Code (Async-First)

```javascript
// src/index.js
const { application } = require("premierepro");

async function initPanel() {
  const proj = await application.activeProject;
  
  if (!proj) {
    console.log("No project open");
    return;
  }
  
  const seq = await proj.activeSequence;
  const name = await seq?.name ?? "No sequence";
  
  document.getElementById("output").textContent = name;
  
  // Listen for sequence changes
  proj.addEventListener("activeSequenceChange", async () => {
    const newSeq = await proj.activeSequence;
    const newName = await newSeq?.name ?? "No sequence";
    document.getElementById("output").textContent = newName;
  });
}

initPanel().catch(e => console.error("Panel init error:", e));
```

### UXP Flexbox Layout (index.html)

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>My Panel</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <div id="container">
    <h1>Sequence Info</h1>
    <div id="output">Loading...</div>
    <button id="applyBtn">Apply Changes</button>
  </div>
  <script src="index.js"></script>
</body>
</html>
```

```css
/* style.css - UXP Flexbox */
#container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  height: 100%;
}

h1 {
  font-size: 20px;
  margin: 0;
}

#output {
  flex: 1;
  border: 1px solid #ccc;
  padding: 8px;
  word-wrap: break-word;
}

button {
  padding: 8px 16px;
  background: #0078d4;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background: #106ebe;
}
```

---

## Debugging & Development Tools

### CEP Debugging (Legacy)

**Remote Debugger (Chrome DevTools):**
```bash
# Enable CEP remote debugging in extensions
# Requires PlayerDebugMode registry key on Windows
# Use CEP debugger port: localhost:8088
```

Console access in panel:
```javascript
csInterface.addEventListener(CSInterface.CONSOLE_MESSAGE, function(event) {
  console.log("CEP console: " + event.data);
});
```

### UXP Debugging (Modern)

**UDT (UXP Developer Tool):**
```bash
npm install -g @adobe/udt
udt --watch ./plugin-folder
```

Features:
- Real-time async/await debugging
- Breakpoints and step-through
- Console logging with proper async context
- DOM inspection
- Network request logging

**Console Debugging in UXP:**
```javascript
// All output goes to UDT console
console.log("Info:", data);
console.error("Error:", error);
console.warn("Warning:", warning);
```

---

## Best Practices

**CEP (Ending):**
- Code sign on macOS 25.2.3+
- Use async bridge if calling async UXP APIs
- Keep panel lightweight (Chromium instance has memory overhead)

**UXP (Recommended):**
- Use `await` for all async API calls
- Wrap mutations in `executeTransaction()`
- Handle null/undefined checks with optional chaining (`?.`)
- Use Flexbox for responsive layouts
- Test on multiple screen DPI settings

---

## See Also

- Examples/cep-theme-sync-panel.jsx and .html
- Examples/uxp-responsive-rubber-panel.html
- Knowledge/cep.md — Full CEP reference
- Knowledge/uxp.md — Full UXP reference

---

## Sources

- CEP Resources: https://github.com/Adobe-CEP/CEP-Resources
- UXP Guide: https://developer.adobe.com/premiere-pro/uxp/
- UDT: https://github.com/Adobe-UXP/UDT
