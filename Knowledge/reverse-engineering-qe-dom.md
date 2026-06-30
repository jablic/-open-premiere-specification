---
id: reverse-engineering-qe-dom
title: Reverse Engineering & the QE DOM
category: scripting
status: undocumented
stability: frozen
doc_status: partial
introduced: "Internal QA tool"
deprecated: "No work planned"
eol: null
min_premiere_version: null
api_namespace: qe
languages: [extendscript, javascript-es3]
tags: [qe-dom, undocumented, reverse-engineering, matchname, effects, ripple, speed, app.enableQE, reflect]
related: [extendscript-core, sequences-tracks-trackitems, essential-graphics-mogrt-text, automation, 00-technology-status-matrix]
supersedes: []
superseded_by: []
confidence: medium
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://vakago-tools.com/premiere-pro-qe-api/
  - https://vakago-tools.com/extendscript-tutorial-adding-effect-to-a-clip-in-premiere-pro/
  - https://community.adobe.com/questions-529/match-name-for-source-text-property-30308
  - https://github.com/tmoroney/auto-subs
---

# Reverse Engineering & the QE DOM

## TL;DR
- `app.enableQE()` unlocks the global `qe` DOM — Quality-Engineering internals built for testing. **DEEP-DIVE TARGET — partially seeded.**
- **Undocumented, unsupported, frozen; breaks between releases.** Last resort only — flag risk to the user.
- Still the only route to: apply effects/transitions **by name**, ripple/roll/slide/slip, set clip **speed**/reverse, `exportFramePNG`, `newSequence(name, presetPath)`.

## Status & Lifecycle
- `undocumented`. Adobe (Bruce Bullis): 'no additional work planned on the unsupported, undocumented PPro ExtendScript QE DOM.' Project-model refresh is unreliable (stale refs across project switches).
- See `00-technology-status-matrix`.

## Architecture
`app.enableQE()` → global `qe` (`qe.project`, `qe.source`, ...). Parallel to the documented `app` tree but with operations the official API lacks. **STUB: tree + relationship to app DOM.**

## API Surface
`qe.project.getVideoEffectByName(name, true)` → `qeTrackItem.addVideoEffect(effect)`; `getVideoEffectList()`/`getVideoTransitionList()`; ripple/roll/slide/slip; set speed/reverse; frame blending; remove all effects; `qe.project.newSequence(name, sqPresetPath)`; `activeSequence.exportFramePNG(time, path)`. Discovery: `qe.reflect.methods`, `qe.project.reflect.methods`. **STUB: full catalog.**

## Working Examples
```js
// ExtendScript (ES3) — apply an effect by name (UNDOCUMENTED, version-fragile)
app.enableQE();
var fx = qe.project.getVideoEffectByName('Gaussian Blur', true);
// operate on the QE track item, not the app-DOM one:
// qeTrackItem.addVideoEffect(fx);
```
**STUB: ripple-delete, set-speed, exportFramePNG examples + version notes.**

## Limitations
No support, no docs, no stability guarantee. To apply an effect to a MOGRT's own controls you must use the **QE** track item, not the app-DOM one. **STUB.**

## Common Errors & Gotchas
Stale `qe.project` references after switching projects. Behavior shifts across New-World-scripting versions. **STUB.**

## Workarounds
Prefer documented APIs; isolate QE calls behind a single module so they can be swapped/disabled per version. **STUB.**

## Migration
No 1:1 UXP replacement for many QE ops yet — track Adobe's UXP additions. **STUB.**

## Cross-References
**matchName catalog** lives here: `AE.ADBE Text` (Source Text component, DisplayName `Text`), `AE.ADBE Gaussian Blur 2`, `ADBE Dropdown Control`. Discover via `trackItem.components[].matchName` + `.properties[].displayName`, or AE `rd_GimmePropPath`. Community catalogs: vakago-tools.com, `vidjuheffex.github.io/ppro.api`.

- `extendscript-core`
- `sequences-tracks-trackitems`
- `essential-graphics-mogrt-text`
- `automation`
- `00-technology-status-matrix`

## Sources
- https://vakago-tools.com/premiere-pro-qe-api/
- https://vakago-tools.com/extendscript-tutorial-adding-effect-to-a-clip-in-premiere-pro/
- https://community.adobe.com/questions-529/match-name-for-source-text-property-30308
- https://github.com/tmoroney/auto-subs

