---
id: localization-i18n
title: Localization & Internationalization (i18n)
category: advanced
status: current
stability: active
doc_status: complete
introduced: "2024"
min_premiere_version: null
api_namespace: null
languages: [javascript, extendscript, python]
tags: [localization, i18n, internationalization, languages, rtl]
related: [panels, uxp, best-practices, automation]
sources: []
confidence: medium
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Localization & Internationalization (i18n)

## TL;DR

i18n = supporting multiple languages + regional settings. For UI panels: externalize strings, support RTL. For timecode: locale-aware formatting. For APIs: handle localized error messages by checking object state, not message text.

---

## Externalizing Strings (ExtendScript)

```javascript
var strings = {
  en: { "title": "Export Video", "button_ok": "OK" },
  es: { "title": "Exportar Video", "button_ok": "Aceptar" },
  de: { "title": "Video exportieren", "button_ok": "OK" }
};
var currentLang = "en";
alert(strings[currentLang]["title"]);
```

---

## UXP Localization

Externalize strings into a JSON file keyed by locale; read navigator.language at runtime to select the active locale and apply to DOM text content.

---

## Timecode Localization

US format uses semicolon separator before frames (HH:MM:SS;FF); European formats often use comma. Always compute timecode from frame count + fps, then apply locale-specific separator.

```python
def format_timecode(seconds, fps, locale="en-US"):
    frames = int(seconds * fps)
    hours = frames // (fps * 3600)
    minutes = (frames % (fps * 3600)) // (fps * 60)
    secs = (frames % (fps * 60)) // fps
    frame = frames % fps
    sep = "," if locale in ("de-DE", "es-ES") else ";"
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{sep}{frame:02d}"
```

---

## Right-to-Left (RTL) Support

For Hebrew/Arabic UI, set dir="rtl" on container elements and mirror layout via CSS (float/text-align flips).

---

## Locale-Aware Number Formatting

Use Intl.NumberFormat with the target locale to format decimals correctly (e.g. "1.234,56" for de-DE vs "1,234.56" for en-US).

---

## Handling Localized Error Messages

Premiere error messages vary by locale. Always validate objects/state, never match against message text strings.

---

## Platform Locale Detection

ExtendScript: $.locale
UXP: navigator.language
Python: locale.getlocale()

---

See also: panels.md, uxp.md, best-practices.md
