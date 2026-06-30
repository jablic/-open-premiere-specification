---
id: ai-integration
title: AI Integration & MCP Servers
category: interop
status: current
stability: experimental
doc_status: stub
introduced: null
deprecated: null
eol: null
min_premiere_version: null
api_namespace: none
languages: [javascript, typescript, python]
tags: [ai, llm, mcp, whisper, tts, elevenlabs, automation, model-context-protocol]
related: [automation, captions, essential-graphics-mogrt-text, cep, uxp]
supersedes: []
superseded_by: []
confidence: medium
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://github.com/antipaster/Adobe-Premiere-Pro-MCP
  - https://github.com/tmoroney/auto-subs
---

# AI Integration & MCP Servers

## TL;DR
- Call external LLM/AI APIs over HTTP from panel JS; or expose Premiere to an agent via an **MCP server**. **STUB.**
- Existing Premiere MCP servers lean on the **deprecated CEP/QE layer** for their most powerful tools; tool counts are self-reported (some inflated).

## Status & Lifecycle
- `experimental`. Underlying technique is the standard import-MOGRT-and-patch + QE pattern wrapped as agent tools. See `00-technology-status-matrix`.

## Architecture
Agent ⇄ MCP server ⇄ (CEP+ExtendScript+QE bridge over file-IPC/`evalScript`) ⇄ Premiere. Or panel JS → HTTP → LLM API (UXP needs `network` permission; CEP needs node/file-access flags). **STUB.**

## API Surface
N/A (composition of other docs' APIs). **STUB.**

## Working Examples
**STUB: minimal UXP fetch-to-LLM panel; minimal MCP tool wrapping importMGT+setValue.**

## Limitations
Most powerful features depend on deprecated CEP/QE; fragile across versions. **STUB.**

## Common Errors & Gotchas
Verify self-reported MCP tool counts against actual source. **STUB.**

## Workarounds
**STUB.**

## Migration
As UXP matures, move agent tools off CEP/QE. **STUB.**

## Cross-References
Known projects: `leancoderkavy/premiere-pro-mcp` (269 tools; CEP+ExtendScript+QE), `antipaster/Adobe-Premiere-Pro-MCP` (170+ tools incl. `add_text_graphic`, `add_tiktok_caption`, MOGRT tools, ElevenLabs TTS), `hetpatel-11/Adobe_Premiere_Pro_MCP`. Whisper via AutoSubs.

- `automation`
- `captions`
- `essential-graphics-mogrt-text`
- `cep`
- `uxp`

## Sources
- https://github.com/antipaster/Adobe-Premiere-Pro-MCP
- https://github.com/tmoroney/auto-subs

