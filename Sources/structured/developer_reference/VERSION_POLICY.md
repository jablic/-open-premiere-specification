# Version Policy

The Developer Reference must be version-aware.

## Version dimensions

Track these separately:

- Premiere Pro version.
- ExtendScript DOM version if known.
- UXP API documentation date or version.
- CEP runtime version.
- C++ SDK release.
- Operating system.

## Version table requirement

Every complete object or method page must include a version matrix.

```markdown
| Premiere Version | Status | Notes |
|------------------|--------|-------|
| 2024 | Unknown | Not verified |
| 2025 | Unknown | Not verified |
| 2026 | Verified | Evidence: ... |
```

## Unknown is allowed

If a version is not verified, write `Unknown`. Do not infer compatibility from neighbouring versions.
