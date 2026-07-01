---
id: ui-theming-and-responsive-panels
title: UI Theming & Responsive ("Rubber") Panel Layout
category: ui-extensibility
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro 14.0"
deprecated: null
eol: null
min_premiere_version: null
api_namespace: none
languages: [javascript, typescript, html, css]
tags: [theming, dark-mode, appearance, spectrum, css-variables, responsive-layout, flexbox, resizeobserver, panel-resize, csinterface, appskininfo, uxp-host-theme]
related: [cep, uxp, panels, best-practices, 00-technology-status-matrix]
supersedes: []
superseded_by: []
sources:
  - https://developer.adobe.com/premiere-pro/uxp/
  - https://developer.adobe.com/photoshop/uxp/2022/guides/theme-awareness/
  - https://developer.adobe.com/premiere-pro/uxp/plugins/concepts/panels-and-commands/
  - https://developer.adobe.com/premiere-pro/uxp/plugins/concepts/manifest/
  - https://developer.adobe.com/premiere-pro/uxp/uxp-api/reference-css/general/variables
  - https://community.adobe.com/t5/premiere-pro-discussions/csinterface-theme-color-changed-event/m-p/8200664
  - https://community.adobe.com/t5/premiere-pro-discussions/how-can-i-change-the-ui-theme-in-premiere-pro-2025/td-p/14921607
  - https://helpx.adobe.com/premiere/desktop/get-started/preferences-and-settings/appearance-preferences.html
confidence: medium
last_verified: "2026-07-01"
verified_against_version: "25.x / 26.0"
---

# UI Theming & Responsive ("Rubber") Panel Layout

> What an extension can and cannot do to Premiere's look-and-feel and layout behavior —
> and how to build theme-synced, content-adaptive layout **inside your own panel**, which is
> the only surface where this is actually achievable.

## TL;DR
- **You cannot restyle Premiere's native chrome** (Timeline, Program Monitor, Effects, Project
  panel, menus, window borders). There is no documented/public API to change the app-wide color
  scheme beyond the built-in **Appearance brightness slider** (`Edit/Premiere Pro > Preferences >
  Appearance`), which is a user preference, not a scriptable surface. Confirmed by Adobe Community
  threads reporting this is now more restrictive than in past versions, not less.
- **You cannot make native panels "rubber" (auto-fit-to-content).** Native panel sizing is either
  user-drag or a saved **Workspace** layout (`Window > Workspaces`); there is no exposed API to
  make the Timeline/Effects/Project panel programmatically reflow based on content.
- **What you CAN build, fully and legitimately:** your own CEP or UXP panel is a web view you
  own completely. Inside it you can (1) sync to the host's live theme via CSS variables (UXP) or
  `appSkinInfo` (CEP), and (2) build a genuinely responsive/"rubber" internal layout with Flexbox +
  size observation, reflowing your own controls as the panel is resized or its content changes.
- Any tool claiming to reskin the native app itself is doing **unsupported binary/resource
  patching** of Adobe's app package — not an extension API, breaks on every update, and is outside
  the scope of legitimate extension development. This doc does not cover that path.

## Status & Lifecycle
- Native-shell theming/layout: **`undocumented`/not exposed** — no lifecycle to track because
  there is no API surface, in CEP or UXP, on any verified version.
- Own-panel theme sync + responsive layout: **`current`**, built on the same CEP (`legacy`) /
  UXP (`current`) split documented in `cep` and `uxp`. Prefer UXP for new work — see
  `00-technology-status-matrix`.

## Architecture
Three distinct layers, only two of which an extension can touch:

1. **Native application shell** (Timeline, Program Monitor, Effects, Project panel, menus,
   window chrome) — closed, proprietary C++ UI toolkit. No ExtendScript, QE DOM, CEP, or UXP
   entry point reaches its styling or layout engine. Out of reach by design.
2. **CEP panel** — a per-panel Chromium (CEF) process rendering your HTML/CSS/JS. The host
   pushes skin info (colors, font) into `CSInterface.getHostEnvironment().appSkinInfo` and fires
   a theme-change event when the user moves the Appearance slider. Full CSS/Flexbox control over
   your own panel's DOM.
3. **UXP panel** — a single sandboxed JS runtime (no Chromium) rendering your HTML/CSS/JS via
   UXP's own minimal web engine. The host exposes live theme values as **CSS custom properties**
   (`--uxp-host-*`) directly usable in your stylesheet — no manual redraw loop needed for basic
   color/font sync.

Layers 2 and 3 are where all real work in this doc happens.

## API Surface

### CEP theme sync (`CSInterface`, legacy)
```js
// CEP — CSInterface.js
const csInterface = new CSInterface();

function onAppThemeColorChanged() {
  const skinInfo = csInterface.getHostEnvironment().appSkinInfo;
  const panelBg   = skinInfo.panelBackgroundColor.color; // {red,green,blue,alpha} 0-255
  const fontSize  = skinInfo.baseFontSize;
  const fontFam   = skinInfo.baseFontFamily;
  applyHostTheme(panelBg, fontSize, fontFam); // your own function: writes CSS vars / classes
}

csInterface.addEventListener(CSInterface.THEME_COLOR_CHANGED_EVENT, onAppThemeColorChanged);
onAppThemeColorChanged(); // run once on load, don't wait for the first change event
```

### UXP theme sync (CSS custom properties, current)
No JS event required for the common case — these are live CSS variables the UXP host recomputes
whenever the user changes the app appearance; your stylesheet reacts automatically via the cascade.

| CSS variable | Purpose |
|---|---|
| `--uxp-host-background-color` | Host panel background — match your root background to this |
| `--uxp-host-text-color` | Primary text color |
| `--uxp-host-text-color-secondary` | Secondary/muted text |
| `--uxp-host-border-color` | Divider/border color |
| `--uxp-host-link-text-color` / `--uxp-host-link-hover-text-color` | Link states |
| `--uxp-host-label-text-color` | Form label color |
| `--uxp-host-widget-hover-background-color` / `-text-color` / `-border-color` | Hover states on interactive widgets |
| `--uxp-host-font-size` / `-font-size-smaller` / `-font-size-larger` | Host type scale |

```css
/* UXP panel stylesheet — inherits host theme automatically */
body {
  background-color: var(--uxp-host-background-color);
  color: var(--uxp-host-text-color);
  border-color: var(--uxp-host-border-color);
  font-size: var(--uxp-host-font-size);
}
.my-widget:hover {
  background-color: var(--uxp-host-widget-hover-background-color);
}
```

### Layout primitives available inside a panel
- **CSS Flexbox: confirmed supported** in UXP (and unrestricted in CEP's Chromium). Use it as the
  base of any responsive layout.
- **CSS Grid: not confirmed supported** on the UXP runtime as of the sources reviewed for this doc
  — treat as unavailable and build equivalent behavior with nested Flexbox + `flex-wrap` until
  verified otherwise against your target UXP version.
- **`ResizeObserver`: not confirmed** as a supported Web API inside the UXP runtime (it is not a
  full Chromium — only a defined API subset). CEP panels (full CEF) support it natively.
  **STUB — verify empirically per Premiere/UXP version**; the safe cross-runtime baseline is the
  standard `window.addEventListener('resize', ...)` shown below, which works in both CEP and UXP.

### Panel size hints (manifest v5, UXP)
```json
{
  "panels": [
    {
      "id": "your.panel.id",
      "minimumSize":     { "width": 230, "height": 200 },
      "maximumSize":     { "width": 2000, "height": 2000 },
      "preferredDockedSize":   { "width": 300, "height": 400 },
      "preferredFloatingSize": { "width": 300, "height": 400 }
    }
  ]
}
```
`minimumSize`/`maximumSize` bound what the **user** can drag the panel to; they are not a
content-driven auto-resize mechanism. Setting `minimumSize == maximumSize` locks the panel to a
fixed size (documented trick for panels that must not be resized).

## Working Examples

### 1. Own-panel accent-color theming, independent of the host
Because you fully own your panel's DOM, you can layer a **second, extension-specific color
scheme** (e.g. a user-selectable accent color) on top of host theme sync — this is the legitimate
version of "change the color scheme," scoped to your panel:

```js
// UXP or CEP — persists a user-chosen accent color for THIS extension's panel only
const ACCENT_KEY = 'ext.accentColor';

function applyAccent(hex) {
  document.documentElement.style.setProperty('--ext-accent-color', hex);
  localStorage.setItem(ACCENT_KEY, hex); // UXP: prefer require('uxp').storage.localFileSystem for larger data
}

// on load
applyAccent(localStorage.getItem(ACCENT_KEY) || '#4A90D9');
```
```css
.primary-button {
  background-color: var(--ext-accent-color);
  color: var(--uxp-host-background-color); /* still respects host light/dark for contrast */
}
```

### 2. "Rubber" panel — content-driven responsive reflow (Flexbox)
This is the buildable version of "resizable interface": your panel's own controls reflow to fill
or shrink with available space and with how much content is present. Works identically in CEP and
UXP since it's standard CSS + a resize listener.

```css
/* Rubber layout shell */
.panel-root {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;      /* let items drop to next line instead of overflowing */
  gap: 8px;
  height: 100%;
  overflow: auto;
}
.panel-item {
  flex: 1 1 160px;      /* grow, shrink, base width — self-sizes within available space */
  min-width: 0;         /* allow shrinking below content's intrinsic width */
}
```

```js
// Content-driven behavior JS cannot express in pure CSS: switch to a stacked layout
// below a width threshold, and hide low-priority controls when starved for space.
const root = document.querySelector('.panel-root');

function reflow() {
  const width = root.clientWidth;
  root.classList.toggle('stacked', width < 260);      // vertical stack on narrow panels
  root.classList.toggle('compact', width < 340);       // hide secondary labels
}

// Baseline (CEP + UXP): standard resize event on window/panel container.
window.addEventListener('resize', reflow);

// Prefer ResizeObserver where the runtime supports it (confirmed in CEP/CEF; verify in UXP
// before relying on it — fall back silently to the window listener above if unavailable).
if (typeof ResizeObserver !== 'undefined') {
  new ResizeObserver(reflow).observe(root);
}

reflow(); // initial pass
```

```css
.stacked { flex-direction: column; }
.compact .secondary-label { display: none; }
```

### 3. Auto-fit rows to variable content length (no CSS Grid dependency)
For content that varies in count/length (e.g. a list of markers, effect params), measure and wrap
with Flexbox instead of relying on Grid `auto-fit`/`minmax`, which is not confirmed available:

```css
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.tag {
  flex: 0 1 auto;   /* size to content, don't grow past it, allow shrink+wrap */
  white-space: nowrap;
}
```

## Limitations
- **Hard wall:** no API (ExtendScript, QE DOM, CEP, UXP, PrSDK) exposes the native application's
  color scheme or lets you set it programmatically. The only lever is the user-facing Appearance
  brightness slider, which is not scriptable.
- **Hard wall:** no API exposes native panel layout/auto-sizing. Workspace switching
  (`Window > Workspaces`) changes which saved panel arrangement is shown, but is a discrete preset
  swap, not continuous content-driven reflow, and there is no verified ExtendScript/UXP call in
  this KB to invoke it programmatically — treat as **menu-only** until a concrete API is sourced.
- UXP's theme CSS variables cover color/font only — no variable set exposes host spacing/density
  or layout metrics.
- `ResizeObserver` support inside the UXP runtime specifically (as opposed to CEP's full CEF) is
  **unverified** — do not depend on it as the only resize signal; always keep the `window.resize`
  fallback.
- CSS Grid support in UXP is **unverified** — do not build layouts that require it without testing
  against the target UXP version first.

## Common Errors & Gotchas
- **Symptom:** panel background doesn't match host after a theme switch (CEP). **Cause:** relying
  only on the initial `getHostEnvironment()` read. **Fix:** always also register
  `CSInterface.THEME_COLOR_CHANGED_EVENT` and re-apply on every event, not just at load.
- **Symptom:** UXP panel looks static/unthemed. **Cause:** hardcoded colors instead of
  `var(--uxp-host-*)`. **Fix:** route every panel color/font through the host CSS variables; only
  layer custom accent colors on top (Example 1), never replace the base palette outright.
- **Symptom:** flex children refuse to shrink below their content width, breaking the "rubber"
  effect. **Cause:** Flexbox default `min-width: auto` on flex items. **Fix:** explicit
  `min-width: 0` (or `min-height: 0` for column layouts) on each flex item, as shown in Example 2.
- **Symptom:** panel content overflows instead of wrapping when the user shrinks the panel.
  **Cause:** missing `flex-wrap: wrap` on the container. **Fix:** set it on `.panel-root` (Example 2).

## Workarounds
- For "app-wide" look consistency without touching the native shell: theme-sync your panel tightly
  (Example 1 + host CSS variables) so it visually blends with whichever Appearance brightness the
  user has chosen, rather than trying to override it. **Confidence: high** — this is the intended,
  supported pattern per Adobe's own theme-awareness guidance.
- For "rubber" behavior beyond a single panel's own contents (e.g. wanting the *Timeline* itself to
  resize with content): not achievable via extension APIs. The closest supported approximation is
  authoring multiple named **Workspaces** and prompting the user to switch between them for
  different tasks. **Confidence: medium** — a real but coarse substitute, not true reflow.

## Migration
Not applicable in the CEP→UXP sense — theme-sync and responsive-layout technique carries over
directly: swap `CSInterface`/`appSkinInfo` reads for `--uxp-host-*` CSS variables, keep the
Flexbox + resize-listener reflow logic unchanged (Example 2/3 code is runtime-agnostic).

## Cross-References
- `cep` — `THEME_COLOR_CHANGED_EVENT` sits inside the broader CEP API surface.
- `uxp` — host CSS variables and Flexbox-only layout are UXP-runtime specifics.
- `panels` — CEP vs UXP panel architecture this doc's examples plug into.
- `best-practices` — general extension UI guidance.
- `00-technology-status-matrix` — pick CEP vs UXP before applying this doc's examples.

## Sources
- https://developer.adobe.com/premiere-pro/uxp/
- https://developer.adobe.com/photoshop/uxp/2022/guides/theme-awareness/
- https://developer.adobe.com/premiere-pro/uxp/plugins/concepts/panels-and-commands/
- https://developer.adobe.com/premiere-pro/uxp/plugins/concepts/manifest/
- https://developer.adobe.com/premiere-pro/uxp/uxp-api/reference-css/general/variables
- https://community.adobe.com/t5/premiere-pro-discussions/csinterface-theme-color-changed-event/m-p/8200664
- https://community.adobe.com/t5/premiere-pro-discussions/how-can-i-change-the-ui-theme-in-premiere-pro-2025/td-p/14921607
- https://helpx.adobe.com/premiere/desktop/get-started/preferences-and-settings/appearance-preferences.html
