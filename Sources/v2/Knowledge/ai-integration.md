---
id: ai-integration
title: AI Integration & MCP Servers
category: interop
status: current
stability: experimental
doc_status: complete
introduced: "2024–2026 MCP ecosystem"
deprecated: null
eol: null
min_premiere_version: null
api_namespace: none
languages: [javascript, typescript, python]
tags: [ai, llm, mcp, whisper, tts, elevenlabs, automation, model-context-protocol, agent-tools]
related: [automation, captions, essential-graphics-mogrt-text, cep, uxp]
supersedes: []
superseded_by: []
sources:
  - https://github.com/antipaster/Adobe-Premiere-Pro-MCP
  - https://github.com/tmoroney/auto-subs
  - https://modelcontextprotocol.io/
  - https://developer.adobe.com/premiere-pro/uxp/
confidence: medium
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
---

# AI Integration & MCP Servers

> Connect LLM agents to Premiere via **MCP servers**, panel HTTP calls, and transcription tools.
> Most powerful agent tools today ride on **legacy CEP + ExtendScript + QE DOM** — flag version risk.

## TL;DR
- **Pattern A:** Panel (CEP/UXP) → HTTP → external LLM API (OpenAI, Anthropic, local Ollama).
- **Pattern B:** External agent → **MCP server** → CEP bridge → `evalScript` / QE DOM → Premiere.
- **Pattern C:** Transcription tools (AutoSubs/Whisper) → caption track → optional LLM post-processing.
- Underlying Premiere operations still use documented patterns: **MOGRT import + Source Text JSON**, **QE DOM for effects**, **importFiles + createCaptionTrack**.
- **Verify MCP tool counts against source** — self-reported numbers are often inflated.

## Status & Lifecycle
- AI integration layer is `experimental` — built on top of `legacy`/`undocumented` Premiere APIs.
- UXP `network` permission required for HTTP from UXP panels (25.6+).
- CEP requires `allow-node` or fetch polyfill for HTTP from panel JS.
- As UXP matures, migrate agent tools off CEP/QE (`00-technology-status-matrix`).

## Architecture

### Pattern A — LLM inside panel
```
┌──────────────┐    HTTPS     ┌─────────────┐
│ UXP/CEP Panel│ ──────────► │ LLM API      │
│ (Spectrum UI)│ ◄────────── │ (OpenAI etc) │
└──────┬───────┘              └─────────────┘
       │ premierepro / evalScript
       ▼
┌──────────────┐
│ Premiere DOM │
└──────────────┘
```

### Pattern B — MCP agent bridge
```
┌──────────────┐   MCP stdio/   ┌──────────────┐  evalScript  ┌──────────┐
│ Cursor/Claude│ ◄────────────► │ MCP Server   │ ───────────► │ Premiere │
│ Agent        │   HTTP/SSE     │ (Node/Python)│  (CEP helper)│ (open)   │
└──────────────┘                └──────────────┘              └──────────┘
```

## Known MCP / Agent Projects

| Project | Stack | Notes |
|---|---|---|
| [antipaster/Adobe-Premiere-Pro-MCP](https://github.com/antipaster/Adobe-Premiere-Pro-MCP) | CEP + ExtendScript + QE | 170+ claimed tools; MOGRT, captions, ElevenLabs TTS |
| leancoderkavy/premiere-pro-mcp | CEP + ExtendScript + QE | ~269 claimed tools — verify against source |
| hetpatel-11/Adobe_Premiere_Pro_MCP | CEP bridge | Smaller surface |
| [tmoroney/auto-subs](https://github.com/tmoroney/auto-subs) | CEP + Whisper | Transcription → captions; **broke in Premiere 2026** |

**Confidence: medium** — tool lists change; always read actual `tools/` or server registration code.

## API Surface
No dedicated "AI API" in Premiere. Composition of:

| Task | Underlying API | Doc |
|---|---|---|
| Text on timeline | `importMGT` + Source Text JSON | `essential-graphics-mogrt-text` |
| Effects by name | QE DOM `getVideoEffectByName` | `reverse-engineering-qe-dom` |
| Import media | `importFiles` | `import` |
| Captions | `importFiles` + `createCaptionTrack` | `captions` |
| Export | `app.encoder` / UXP export | `export-rendering-media-encoder` |
| Project read | `app.project` tree walk | `sequences-tracks-trackitems` |

## Working Examples

```js
// UXP — Premiere 25.6+ — fetch LLM (requires network permission in manifest)
const response = await fetch('https://api.openai.com/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + apiKey
  },
  body: JSON.stringify({
    model: 'gpt-4o',
    messages: [{ role: 'user', content: userPrompt }]
  })
});
const data = await response.json();
const text = data.choices[0].message.content;
// Then apply to timeline via premierepro module...
```

```js
// ExtendScript (ES3) — MCP tool pattern: import MOGRT + set text (agent backend)
function agentSetMogrtText(mogrtPath, newText, vTrack, aTrack) {
  var seq = app.project.activeSequence;
  if (!seq) { return JSON.stringify({ ok: false, error: 'No sequence' }); }
  var t = seq.getPlayerPosition();
  seq.importMGT(mogrtPath, t, vTrack, aTrack);
  // ... find trackItem, patch Source Text JSON — see essential-graphics-mogrt-text
  return JSON.stringify({ ok: true });
}
```

```python
# Python MCP server skeleton — tool wraps Premiere via file/HTTP bridge
# Premiere must be open with CEP helper running
@mcp.tool()
def premiere_import_media(paths: list[str]) -> str:
    """Import media files into active Premiere project."""
    return bridge.eval_script(f'importToBin({json.dumps(paths)})')
```

## Limitations
- **No headless Premiere** — agent tools require GUI app running (`automation`).
- MCP servers depending on **QE DOM** break across Premiere versions (`undocumented`).
- **MOGRT text** has no UXP parity — agent tools for text still need ExtendScript path.
- **Rate limits / API keys** — never embed secrets in panel code; use env vars / secure storage.
- AutoSubs CEP failure in 2026 blocks one transcription path until UXP port.

## Common Errors & Gotchas
- **Symptom:** Agent invents `sequence.addCaption(text)`. **Cause:** Hallucinated API. **Fix:** Use real pipeline (`captions`, `best-practices` RULE-AI-0001).
- **Symptom:** MCP tool count doesn't match behavior. **Cause:** Inflated README. **Fix:** Count `@mcp.tool()` decorators in source.
- **Symptom:** evalScript returns empty. **Cause:** ExtendScript error swallowed. **Fix:** Error-envelope pattern (`cep`).
- **Symptom:** UXP fetch fails. **Cause:** Missing `network` permission. **Fix:** Add to `manifest.json` `requiredPermissions`.

## Workarounds
- Isolate Premiere bridge behind stable JSON RPC interface — swap CEP→UXP without changing agent tools.
- Use this knowledge base (`premiere-dev` skill) as agent system prompt context.
- For transcription without AutoSubs: external Whisper → SRT file → `import` + `captions` pipeline.

## Migration
- Move MCP bridge from CEP to UXP as APIs reach parity (MOGRT text, QE operations).
- Prefer UXP `network` permission over CEP Node.js for HTTP.
- Track Adobe UXP API additions each release — update agent tool registry.

## Cross-References
- `automation` — pymiere, external drivers
- `captions` — Whisper, AutoSubs
- `essential-graphics-mogrt-text` — text injection for agents
- `cep` — evalScript bridge for MCP
- `uxp` — forward path for panel-based AI
- `best-practices` — agent safety rules

## Sources
- https://github.com/antipaster/Adobe-Premiere-Pro-MCP
- https://github.com/tmoroney/auto-subs
- https://modelcontextprotocol.io/
- https://developer.adobe.com/premiere-pro/uxp/
