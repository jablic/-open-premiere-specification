# Phase 0 — Resolve fixture contract

Fixture-backed `vfx_core` and read-only adapter are implemented. Live Resolve Studio verification is pending.

Phase 1 core additions now include pure export configuration, column definitions,
collision-safe output naming, and a JSON shot manifest. These modules do not touch
the filesystem or Resolve.

Required fixtures: 24 fps at 01h and 03h, 23.976 non-drop, mixed tracks/markers. The adapter exposes only active project/timeline and read-only marker/item enumeration. Incomplete enumeration returns `status=incomplete`, `complete=false`; future writes must fail closed.

**Not documented — requires live fixture verification:** Workflow Integration bridge availability/version, API payload shape, enumeration completeness, exact FPS representation, displayed-TC/frame conversion, track numbering, and marker duration semantics.
