# Adobe Premiere Pro Developer Reference

This directory is the source editorial structure for the developer-facing reference manual.

The scope is intentionally narrow:

- Premiere Pro extensibility surfaces.
- External plugins and extensions.
- Automation interfaces.
- Host communication mechanisms.
- API contracts and observed behaviour.

This project does **not** document user-facing editing workflows unless they affect plugin, extension, scripting, SDK, or automation behaviour.

## Primary surfaces

1. ExtendScript DOM.
2. UXP Premiere API.
3. CEP panel runtime.
4. QE DOM, clearly marked as undocumented / reverse-engineered unless evidence says otherwise.
5. Premiere Pro C++ SDK.
6. XML, caption, MOGRT, and other interchange/internal formats when relevant to external tooling.

## Source of truth policy

Human-readable reference chapters live in `developer_reference/`.
Machine-readable inventory lives in `inventory/` and `knowledge/`.
Generated files must not become authoritative sources.
