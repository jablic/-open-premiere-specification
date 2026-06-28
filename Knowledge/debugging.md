---
id: debugging
title: Debugging & Tooling
category: meta
status: mixed
stability: active
doc_status: complete
introduced: null
deprecated: null
eol: null
min_premiere_version: null
api_namespace: none
languages: [extendscript, javascript, typescript]
tags: [debugging, extendscript-debugger, vscode, devtools, udt, writeln, breakpoints, types-for-adobe, estk]
related: [extendscript-core, cep, uxp, automation]
supersedes: []
superseded_by: []
sources:
  - https://blog.developer.adobe.com/en/publish/2019/06/debugging-your-adobe-panel
  - https://github.com/Adobe-CEP/Getting-Started-guides/blob/master/Client-side%20Debugging/readme.md
  - https://github.com/aenhancers/Types-for-Adobe
  - https://marketplace.visualstudio.com/items?itemName=Adobe.extendscript-debug
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
---

# Debugging & Tooling

> Debug paths per runtime: **ExtendScript** (VS Code debugger), **CEP** (Chromium DevTools), **UXP** (UDT).
> ESTK (ExtendScript Toolkit) is **deprecated** — use VS Code ExtendScript Debugger.

## TL;DR
- **ExtendScript:** VS Code + `Adobe.extendscript-debug` extension; `$.writeln()` for quick logs; set `"targetSpecifier": "premierepro"` in launch config.
- **CEP panel UI:** Enable `PlayerDebugMode` + `.debug` port file → Chrome DevTools at `localhost:<port>`.
- **CEP host (.jsx):** Debug via ExtendScript Debugger or `$.writeln` (shows in ESTK console if attached, or ExtendScript Toolkit log).
- **UXP:** Enable Developer Mode (Settings → Plugins) → **UXP Developer Tool v2.2.1+** → load plugin → Inspect.
- **IntelliSense:** `Types-for-Adobe` (community TypeScript defs) — not official but invaluable.

## Status & Lifecycle

| Tool | Status |
|---|---|
| ESTK (ExtendScript Toolkit) | `deprecated` — 32-bit, dead on modern macOS |
| VS Code ExtendScript Debugger | `current` for ExtendScript |
| CEP Chromium DevTools | `legacy` (works while CEP loads) |
| UXP Developer Tool (UDT) | `current` for UXP |
| Types-for-Adobe | `current` community resource |

## Architecture

```
Runtime          Inspector                    Log output
─────────        ─────────                    ──────────
ExtendScript  →  VS Code debugger / $.writeln  ESTK console / VS Code Debug Console
CEP UI        →  Chrome DevTools (CEF)         Browser console
CEP host .jsx →  VS Code debugger              $.writeln
UXP panel     →  UDT Chromium DevTools         UDT console
```

## API Surface

### ExtendScript logging
```js
// ExtendScript (ES3)
$.writeln('debug: ' + variable);
$.write('partial ');
alert('blocking dialog'); // avoid in production
```

### VS Code launch config (ExtendScript)
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "extendscript-debug",
      "request": "launch",
      "name": "Premiere ExtendScript",
      "hostAppSpecifier": "premierepro",
      "hostName": "premierepro",
      "scriptFile": "${workspaceFolder}/host/index.jsx"
    }
  ]
}
```

### CEP debug setup

**macOS** — enable debug mode (replace `<n>` with CSXS version, e.g. 12):
```bash
defaults write com.adobe.CSXS.12 PlayerDebugMode 1
```

**Windows** — registry:
```
HKCU\Software\Adobe\CSXS.12
  PlayerDebugMode = "1" (string)
```

**.debug file** (next to manifest):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExtensionList>
  <Extension Id="com.example.panel">
    <HostList>
      <Host Name="PPRO" Port="8088"/>
    </HostList>
  </Extension>
</ExtensionList>
```

Open `http://localhost:8088` or `chrome://inspect` → inspect CEF target.

### UXP debug setup
1. Premiere → Settings → Plugins → **Developer Mode** ON
2. Restart Premiere
3. Launch **UXP Developer Tool** v2.2.1+
4. Add Developer Workspace → point to plugin folder
5. Load → Inspect (Chromium DevTools)

## Working Examples

```js
// ExtendScript (ES3) — safe debug wrapper (no alert in production)
function dbg(msg) {
  if (typeof $.writeln === 'function') {
    $.writeln('[myPanel] ' + String(msg));
  }
}
```

```js
// CEP panel — log from UI side
console.log('CEP UI:', csInterface.getHostEnvironment());
csInterface.evalScript('$.writeln("from panel")', function(res) {
  console.log('host returned:', res);
});
```

## Limitations
- ExtendScript Debugger can be **flaky inside complex CEP panels** — prefer isolated `.jsx` test scripts.
- `$.writeln` from evalScript may not appear in CEP DevTools — check VS Code debug console.
- Modern Chrome versions may break CEP DevTools on `KeyboardEvent.keyIdentifier` — use `chrome://inspect` or older Chrome.
- UXP DevTools does not expose ExtendScript — UXP is a separate runtime.
- No official source maps for host `.jsx` in CEP bridge.

## Common Errors & Gotchas
- **Symptom:** Breakpoints never hit. **Cause:** Wrong `hostAppSpecifier` or script not loaded in Premiere. **Fix:** Premiere must be running; verify launch config targets `premierepro`.
- **Symptom:** CEP DevTools blank. **Cause:** `PlayerDebugMode` not set or wrong CSXS version number. **Fix:** Match CSXS version in manifest `RequiredRuntime`.
- **Symptom:** UXP plugin not in UDT list. **Cause:** Developer Mode off or invalid `manifest.json`. **Fix:** Restart after enabling; validate manifest v5 schema.
- **Symptom:** `JSON is undefined` in ExtendScript. **Cause:** No json2.js. **Fix:** Bundle json2.js (`extendscript-core`).

## Workarounds
- **Types-for-Adobe** (`github.com/aenhancers/Types-for-Adobe`) — TypeScript definitions for Premiere DOM IntelliSense.
- Wrap `evalScript` with error-envelope pattern (return JSON `{ok, error}`) — see `extendscript-core` / `cep`.
- For headless debugging, write results to temp file via ExtendScript `File` object.
- pymiere: log Python side; ExtendScript side via `$.writeln` (`automation`).

## Migration
- ESTK → VS Code ExtendScript Debugger (mandatory on Apple Silicon).
- CEP DevTools → UDT as panels migrate to UXP.
- Keep ExtendScript debugger for legacy `.jsx` until 2026-09 EOL.

## Cross-References
- `extendscript-core` — ES3 runtime, json2.js
- `cep` — evalScript bridge, .debug, PlayerDebugMode
- `uxp` — UDT, Developer Mode
- `automation` — pymiere remote debugging

## Sources
- https://blog.developer.adobe.com/en/publish/2019/06/debugging-your-adobe-panel
- https://github.com/Adobe-CEP/Getting-Started-guides/blob/master/Client-side%20Debugging/readme.md
- https://github.com/aenhancers/Types-for-Adobe
- https://marketplace.visualstudio.com/items?itemName=Adobe.extendscript-debug
