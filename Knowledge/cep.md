---
id: cep
title: CEP (Common Extensibility Platform)
category: ui-extensibility
status: legacy
stability: frozen
doc_status: complete
introduced: "CEP 4.0"
deprecated: "CEP 12 = last major runtime (Premiere 25.0)"
eol: null
min_premiere_version: null
api_namespace: CSInterface
languages: [javascript, typescript, html, css, extendscript]
tags: [cep, manifest, csxs, csinterface, evalscript, zxp, bolt-cep, nodejs, debugging, player-debug-mode, plugplug, cef]
related: [extendscript-core, uxp, panels, debugging, automation, 00-technology-status-matrix]
supersedes: []
superseded_by: [uxp]
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://github.com/Adobe-CEP/CEP-Resources
  - https://github.com/Adobe-CEP/Getting-Started-guides
  - https://github.com/Adobe-CEP/Samples/tree/master/PProPanel
  - https://github.com/hyperbrew/bolt-cep
  - https://www.npmjs.com/package/bolt-cep
  - https://blog.developer.adobe.com/en/publish/2019/06/debugging-your-adobe-panel
---

# CEP (Common Extensibility Platform)

> HTML/CSS/JS panel extensions that run in a Chromium (CEF) process and call Premiere's ExtendScript
> engine through `CSInterface.evalScript`. **Legacy — maintenance-only.** CEP 12 (Premiere 25.0) is the
> last major runtime. New panels for Premiere **25.6+** → UXP (`uxp`).

## TL;DR
- **Two runtimes:** CEF panel UI (modern JS allowed) + ExtendScript host (`.jsx`, ES3 only), joined by `evalScript`.
- **Packaging:** folder with `/CSXS/manifest.xml` → signed `.zxp` (or unsigned + debug mode for dev).
- **CEP 12 = last major runtime** (25.0). Loading already degrades in 25.x; some panels broke in Premiere 2026.
- **Modern scaffold:** Bolt CEP (Vite + TS + React/Vue/Svelte, HMR, typed ExtendScript via `evalTS()`).
- **Migration target:** UXP — a rewrite, not a port. No `CSInterface`, no Chromium, no 1:1 parity.

## Status & Lifecycle
- **Introduced:** CEP 4.0 brought HTML/CSS/JS panels to Creative Cloud apps.
- **Current status:** `legacy` / `frozen`. Adobe: **CEP 12 is the last major CEP update** — critical security fixes only, no new features. CEP 12 shipped with **Premiere 25.0**.
- **Degradation signals (version-pinned):**
  - Unsigned CEP-12 extensions failing to load by **Premiere 25.2.3** on macOS Sequoia.
  - **AutoSubs** CEP panel stopped loading in **Premiere 2026** (concrete death signal).
- **EOL:** No single Adobe-published "CEP removed in version X" date for Premiere yet. Treat removal mechanics as evolving; verify against the user's build.
- **Replacement:** UXP panels (`uxp`). ExtendScript host logic EOL **2026-09** (`extendscript-core`).
- See `00-technology-status-matrix`.

## Architecture

CEP panels are **out-of-process CEF instances** (one Chromium process per loaded panel) that communicate with the host application's ExtendScript engine via a string bridge.

```
┌─────────────────────────────────────────────────────────────┐
│  Premiere Pro (host application)                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  ExtendScript Engine                                   │  │
│  │  host/index.jsx  →  app.* DOM (sync, ES3)             │  │
│  │  ↑ evalScript(string) returns string                   │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │ CSXS / PlugPlug bridge            │
│  ┌───────────────────────▼───────────────────────────────┐  │
│  │  CEF Chromium Process (panel extension)               │  │
│  │  client/index.html + main.js + CSInterface.js         │  │
│  │  Modern JS / React / Vue / Node (if enabled)          │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Folder structure (typical)

```
my-panel/
├── CSXS/
│   └── manifest.xml          # Extension metadata, host targeting, CEF flags
├── client/                   # Panel UI (served by CEF)
│   ├── index.html
│   ├── main.js               # Panel logic; calls CSInterface
│   └── CSInterface.js        # Adobe bridge library (from CEP-Resources)
├── host/                     # ExtendScript host scripts
│   ├── index.jsx             # Entry; functions called via evalScript
│   └── json2.js              # Required for JSON in ExtendScript
├── .debug                    # Dev only: assigns DevTools port per host
└── META-INF/                 # Optional; signing metadata for ZXP
```

**Install locations (unsigned dev):**
- **macOS:** `~/Library/Application Support/Adobe/CEP/extensions/<extension-id>/`
- **Windows:** `C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\<extension-id>\`

After changing `manifest.xml` or host `.jsx` files, **relaunch Premiere** (hot reload is unreliable for manifest/host changes).

### Lifecycle
1. Premiere starts → CSXS loads extensions whose manifest matches host `PPRO` + version range.
2. User opens panel from **Window → Extensions** menu.
3. CEF loads `MainPath` HTML; panel JS calls `evalScript("hostFn()")`.
4. ExtendScript executes synchronously on the main thread; result string returns to callback.
5. Panel can listen for / dispatch **CSXS events** (PlugPlug) for host ↔ panel messaging beyond evalScript.

## API Surface

### manifest.xml — key elements

| Element / attribute | Purpose |
|---|---|
| `<ExtensionList>` | Declares one or more extension IDs |
| `<Extension Id="com.example.panel">` | Unique reverse-DNS ID (matches `.debug`, signing) |
| `<HostList><Host Name="PPRO" Version="[15.0,99.9]"/></HostList>` | Target Premiere Pro; bracket syntax = min–max inclusive |
| `<RequiredRuntime Name="CSXS" Version="12.0"/>` | CEP runtime version — use **12.0** for Premiere 25.0+ |
| `<DispatchInfo>` | Per-extension UI metadata |
| `<Resources><MainPath>./client/index.html</MainPath>` | Panel entry HTML |
| `<Resources><ScriptPath>./host/index.jsx</ScriptPath>` | ExtendScript loaded at panel startup |
| `<UI><Type>Panel</Type>` | Panel vs ModalDialog vs Custom (see CEP docs) |
| `<UI><Menu>My Panel</Menu>` | Window menu label |
| `<CEFCommandLine>` | CEF/Chromium flags (Node.js, mixed context, etc.) |

**Minimal manifest skeleton:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExtensionManifest Version="7.0"
  ExtensionBundleId="com.example.mypanel"
  ExtensionBundleVersion="1.0.0"
  ExtensionBundleName="My Panel">
  <ExtensionList>
    <Extension Id="com.example.mypanel.panel" Version="1.0.0"/>
  </ExtensionList>
  <ExecutionEnvironment>
    <HostList>
      <!-- PPRO = Premiere Pro. Bracket range future-proofs host versions. -->
      <Host Name="PPRO" Version="[15.0,99.9]"/>
    </HostList>
    <LocaleList><Locale Code="All"/></LocaleList>
    <RequiredRuntimeList>
      <RequiredRuntime Name="CSXS" Version="12.0"/>
    </RequiredRuntimeList>
  </ExecutionEnvironment>
  <DispatchInfoList>
    <Extension Id="com.example.mypanel.panel">
      <DispatchInfo>
        <Resources>
          <MainPath>./client/index.html</MainPath>
          <ScriptPath>./host/index.jsx</ScriptPath>
          <CEFCommandLine>
            <!-- Enable Node.js in panel JS (see Limitations) -->
            <Parameter>--enable-nodejs</Parameter>
            <Parameter>--mixed-context</Parameter>
          </CEFCommandLine>
        </Resources>
        <Lifecycle><AutoVisible>true</AutoVisible></Lifecycle>
        <UI>
          <Type>Panel</Type>
          <Menu>My Panel</Menu>
          <Geometry>
            <Size><Width>400</Width><Height>600</Height></Size>
          </Geometry>
        </UI>
      </DispatchInfo>
    </Extension>
  </DispatchInfoList>
</ExtensionManifest>
```

**Host codes:** `PPRO` = Premiere Pro, `AEFT` = After Effects, `PHXS` = Photoshop, etc. Always verify against [CEP-Resources HostList](https://github.com/Adobe-CEP/CEP-Resources).

### CSInterface — bridge API

Load `CSInterface.js` (from [CEP-Resources](https://github.com/Adobe-CEP/CEP-Resources)) in the panel HTML.

| Method / property | Signature | Notes |
|---|---|---|
| `evalScript` | `(script: string, callback?: (result: string) => void) => void` | Executes ExtendScript in host context. **Callback receives a STRING.** On uncaught host error → `"EvalScript error."` |
| `getHostEnvironment` | `() => HostEnvironment` | App ID, version, locale, skin info |
| `getSystemPath` | `(pathType: string) => string` | `SystemPath.EXTENSION`, `SystemPath.USER_DATA`, etc. |
| `getExtensionID` | `() => string` | Current extension ID |
| `addEventListener` | `(type: string, listener: fn, obj?: any) => void` | CSXS/PlugPlug events |
| `removeEventListener` | `(type: string, listener: fn, obj?: any) => void` | |
| `dispatchEvent` | `(event: CSEvent) => void` | Send event to host or other extensions |
| `requestOpenExtension` | `(extensionId: string, params?: string) => void` | Open another CEP extension |
| `openURLInDefaultBrowser` | `(url: string) => void` | External links (auth flows, docs) |
| `getNetworkPreferences` | `() => NetworkPreferences` | Proxy settings |
| `evalScript` sync variant | N/A | **No synchronous evalScript** — always callback-based |
| `getCurrentApiVersion` | `() => ApiVersion` | CEP API version |

**Theme / UI sync:** `getHostEnvironment().appSkinInfo` exposes host panel colors. Use `window.__adobe_cep__.invokeSync("getHostEnvironment", "")` only when documented — prefer `CSInterface` wrappers. On macOS, Spectrum-themed click bugs have been reported; Bolt CEP exposes `enableSpectrum()` workaround.

### evalScript contract
- Host functions must **return strings** (typically `JSON.stringify(...)`).
- Wrap host logic in `try/catch` and return structured error envelopes — bare exceptions become useless `"EvalScript error."` strings.
- Host is **ES3** — no modern syntax in `.jsx` (see `extendscript-core`).
- Panel side may use ES6+, TypeScript, React, etc.

### Node.js integration
Enable via manifest `<CEFCommandLine>`:
```xml
<Parameter>--enable-nodejs</Parameter>
<Parameter>--mixed-context</Parameter>
```
Then in panel JS: `const fs = require('fs');` — useful for HTTP clients, file I/O, local ML inference. **Risk:** Node in CEP is legacy; UXP has no Node equivalent (use UXP `fs`/`os` modules instead when migrating).

### CSXS events (PlugPlug)
Beyond one-shot `evalScript`, panels can subscribe to typed events:
```js
// CEP panel (modern JS)
const cs = new CSInterface();
cs.addEventListener('com.adobe.csxs.events.ApplicationActivate', () => {
  console.log('Premiere activated');
});
// Dispatch custom events between panel ↔ host via CSEvent + dispatchEvent
```
Event catalog: [CEP-Resources CSXS Event Reference](https://github.com/Adobe-CEP/CEP-Resources/tree/master/CEP_12.x).

## Working Examples

### 1. Minimal manifest + evalScript bridge (error envelope)
Host (`host/index.jsx`):
```js
// ExtendScript (ES3) — Premiere 14.x+
//@include "json2.js"

function getActiveSequenceName() {
    try {
        var seq = app.project && app.project.activeSequence;
        if (!seq) {
            return JSON.stringify({ ok: false, err: "No active sequence" });
        }
        return JSON.stringify({ ok: true, name: seq.name });
    } catch (e) {
        return JSON.stringify({ ok: false, err: String(e) });
    }
}
```

Client (`client/main.js`):
```js
// CEP panel (modern JS)
const cs = new CSInterface();

function callHost(fnCall, onSuccess, onError) {
  cs.evalScript(fnCall, (raw) => {
    let res;
    try { res = JSON.parse(raw); }
    catch { onError("Bad host return: " + raw); return; }
    if (!res.ok) { onError(res.err); return; }
    onSuccess(res);
  });
}

callHost("getActiveSequenceName()",
  (res) => console.log("Sequence:", res.name),
  (err) => console.error(err)
);
```

Full pattern also in `extendscript-core` Example 5.

### 2. .debug file (DevTools port assignment)
Place `.debug` next to `CSXS/manifest.xml` (dev builds only — do not ship to production):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExtensionList>
  <Extension Id="com.example.mypanel.panel">
    <HostList>
      <Host Name="PPRO" Port="8088"/>
    </HostList>
  </Extension>
</ExtensionList>
```
Requires `PlayerDebugMode=1` (see §Common Errors). Open `http://localhost:8088` or use `chrome://inspect` → inspect CEF target.

### 3. PlayerDebugMode + unsigned loading
**macOS** (match CSXS version to manifest, e.g. 12):
```bash
defaults write com.adobe.CSXS.12 PlayerDebugMode 1
```
**Windows** — create/set registry string:
```
HKCU\Software\Adobe\CSXS.12
  PlayerDebugMode = "1"
```
Restart Premiere after changing. See `debugging` for full setup.

### 4. ZXP signing (distribution)
Adobe **ZXPSignCmd** (from CEP-Resources or ExManCmd bundle):
```bash
# 1. Create self-signed cert (dev / internal distribution)
ZXPSignCmd -selfSignedCert US CA "My Org" "com.example" mycert.p12 mypassword

# 2. Sign extension folder → .zxp
ZXPSignCmd -sign /path/to/my-panel /path/to/my-panel.zxp mycert.p12 mypassword
```
Install signed `.zxp` via **ExManCmd**, Anastasiy's Extension Manager, or double-click (platform-dependent).

**TSA timestamp note:** A global TSA outage in **April 2025** broke signing for some toolchains. Fixed in community tooling (e.g. `vite-cep-plugin@1.2.9` bundles the fix). If signing fails with timestamp errors, update Bolt CEP / vite-cep-plugin.

### 5. Bolt CEP scaffold (recommended for new CEP maintenance work)
```bash
npm create bolt-cep my-panel -- --template react-ts
cd my-panel
npm run build    # outputs ZXP-ready bundle
npm run zxp      # sign (configure cert in bolt.config)
```
Bolt CEP provides: Vite bundling, TypeScript, React/Vue/Svelte templates, HMR during dev, `evalTS()` typed ExtendScript calls, integrated ZXP signing, and `enableSpectrum()` macOS workaround. See [hyperbrew/bolt-cep](https://github.com/hyperbrew/bolt-cep).

Reference sample: Adobe's [PProPanel](https://github.com/Adobe-CEP/Samples/tree/master/PProPanel) (official, older scaffold).

## Limitations
- **Maintenance-only platform.** No new CEP features from Adobe; plan UXP migration.
- **Per-panel CEF process** — memory/CPU overhead vs UXP's single runtime.
- **Two-language, two-runtime split** — panel JS + host ES3; no shared module graph without build tooling.
- **`evalScript` is stringly-typed and synchronous** — no native Promises across the bridge; batch/chunk long work from the panel side.
- **Host changes require relaunch** — editing `manifest.xml` or `.jsx` rarely hot-reloads reliably.
- **Unsigned extensions increasingly blocked** — especially CEP 12 on recent macOS/Premiere builds.
- **No direct UXP/premierepro DOM** — everything goes through ExtendScript `app.*` (frozen, EOL 2026-09).
- **MOGRT text-blob, QE DOM, encoder edge cases** — only reachable via ExtendScript host; same EOL clock applies.
- **Distribution friction** — ZXP signing certs, ExManCmd, vs UXP `.ccx` / Marketplace workflow.
- **Premiere 2026+** — treat CEP as unreliable; verify panel loads on target builds.

## Common Errors & Gotchas
- **Symptom:** Panel missing from Window → Extensions. **Cause:** Wrong host name/version, unsigned extension, or `PlayerDebugMode` off. **Fix:** Verify `<Host Name="PPRO" Version="[15.0,99.9]"/>`, enable debug mode or sign ZXP, check install path.
- **Symptom:** `"EvalScript error."` with no detail. **Cause:** Uncaught exception in host `.jsx`. **Fix:** Wrap every host function in try/catch; return JSON error envelope (Example 1).
- **Symptom:** `JSON is undefined` in host. **Cause:** ExtendScript has no native JSON. **Fix:** `//@include "json2.js"` in host scripts (`extendscript-core`).
- **Symptom:** CEP DevTools blank / won't connect. **Cause:** Wrong CSXS version in `defaults write` / registry; or modern Chrome removed `KeyboardEvent.keyIdentifier`. **Fix:** Match CSXS number to manifest `RequiredRuntime`; use `chrome://inspect` or an older Chrome build.
- **Symptom:** Node `require` fails. **Cause:** Missing `--enable-nodejs` / `--mixed-context` in manifest. **Fix:** Add `<CEFCommandLine>` parameters; relaunch host.
- **Symptom:** Panel worked in 25.0, dead in 2026. **Cause:** CEP deprecation / runtime removal in progress. **Fix:** Migrate to UXP (`uxp`).
- **Symptom:** ZXP signing fails (timestamp). **Cause:** TSA infrastructure issue (Apr 2025 historically). **Fix:** Update signing toolchain / vite-cep-plugin.
- **Symptom:** macOS Spectrum UI clicks don't register. **Cause:** Known CEP/Spectrum interaction bug. **Fix:** Bolt CEP `enableSpectrum()` or custom CSS pointer-events workaround. `confidence: medium`.

## Workarounds
- **Bolt CEP** — eliminates manual manifest/scaffold/signing pain; typed `evalTS()` reduces evalScript bugs. `confidence: high`.
- **Dual-build strategy** — ship signed ZXP for legacy (<25.6), UXP `.ccx` for 25.6+ (`panels`). `confidence: high`.
- **Error-envelope + JSON** — mandatory pattern for any non-trivial host bridge (`extendscript-core` Example 5). `confidence: high`.
- **External automation** — pymiere / MCP servers keep a headless CEP helper for Python agents (`automation`, `ai-integration`). Accept unmaintained/pinned-version risk. `confidence: medium`.
- **MOGRT text until UXP parity** — keep a thin CEP+ExtendScript helper alongside a UXP UI shell. `confidence: medium`.
- **HTTP from panel** — Node.js in CEP (`--enable-nodejs`) or fetch polyfill; UXP uses `requiredPermissions.network`. `confidence: high`.

## Migration

CEP → UXP is a **rewrite**, not a port. Adobe explicitly does not intend 1:1 parity.

| CEP / ExtendScript | UXP replacement | Parity |
|---|---|---|
| `CSInterface.evalScript("hostFn()")` | `require('premierepro')` + `await` | Partial — many DOM gaps |
| `host/index.jsx` (ES3) | Panel `index.js` (modern JS) | Language upgrade |
| HTML/React panel UI | Spectrum Web Components | UI rewrite; Spectrum limited in Premiere |
| `manifest.xml` | `manifest.json` v5 | Different schema |
| `.zxp` + ZXPSignCmd | `.ccx` + UPIA / Marketplace | Different distribution |
| Node.js (`--enable-nodejs`) | UXP `fs` / `os` / `shell` | No Node |
| Chromium DevTools | UXP Developer Tool (UDT) | Different debug workflow |
| QE DOM via ExtendScript | Not available | **Gap** |
| MOGRT Source Text JSON | Not available yet | **Gap** — keep CEP fallback |

**Suggested migration steps:**
1. Inventory every `evalScript` host function → map to UXP `premierepro` API (file gaps on Adobe forums).
2. Rebuild UI with Spectrum Web Components (or minimal HTML if Spectrum gaps block you).
3. Replace error-envelope bridge with native async/await + `executeTransaction` for mutations.
4. Swap packaging: `.zxp` → `.ccx`; enable Premiere **Settings → Plugins → Developer Mode** for dev.
5. Drop CEP-only dependencies (Node modules) → UXP equivalents.
6. Run dual-build until install base is 25.6+ (`00-technology-status-matrix`).
7. For perf-critical native code, add **UXP Hybrid `.uxpaddon`** (`cpp-native-sdk`) instead of CEP Node bridges.

See `uxp` §Migration and `panels` comparison matrix.

## Cross-References
- `extendscript-core` — ES3 host runtime, json2.js, evalScript error envelopes (Example 5)
- `uxp` — migration target, async DOM, manifest v5
- `panels` — CEP vs UXP decision matrix
- `debugging` — PlayerDebugMode, `.debug`, VS Code ExtendScript Debugger for host `.jsx`
- `automation` — pymiere CEP bridge, BridgeTalk
- `ai-integration` — MCP servers riding CEP+evalScript (version risk)
- `00-technology-status-matrix` — CEP 12 last-runtime authority, 2026 breakage signals
- `Examples/extendscript/` — guarded host patterns referenced by panels

## Sources
- Adobe CEP Resources (manifest, CSInterface, ZXPSignCmd, CSXS 12): https://github.com/Adobe-CEP/CEP-Resources
- Adobe CEP Getting Started guides: https://github.com/Adobe-CEP/Getting-Started-guides
- PProPanel official sample: https://github.com/Adobe-CEP/Samples/tree/master/PProPanel
- Bolt CEP scaffold: https://github.com/hyperbrew/bolt-cep
- Debugging Adobe panels (Adobe blog): https://blog.developer.adobe.com/en/publish/2019/06/debugging-your-adobe-panel
- Hyper Brew UXP/CEP migration analysis: https://hyperbrew.co/blog/uxp-plugins-in-premiere-2026/
