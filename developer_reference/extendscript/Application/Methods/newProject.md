# app.newProject()

Surface: ExtendScript DOM
Evidence: A/B for signature, return value, and sample usage; overwrite behavior: Not documented.

## Syntax

```javascript
app.newProject(path)
```

## Parameters

| Parameter | Type | Meaning |
|---|---|---|
| `path` | `String` | Destination path for the new Premiere project. |

The documented contract does not state whether the host appends `.prproj`; pass the complete intended filename.

## Returns

`Boolean`. Adobe-maintained sample code treats `true` as project creation success and any other result as failure.

## Behavior and side effects

- Creates a new project at `path`.
- Changes the active project context if creation succeeds; exact activation semantics are **Not documented**.
- Filesystem overwrite, parent-directory creation, and save timing are **Not documented**.

## Preconditions

- Script runs in Premiere Pro ExtendScript context.
- Parent directory exists and is writable.
- Caller has decided how to handle an existing destination.

## Production contract

Do not use an existing path as an implicit overwrite test. Check for collisions before calling, require explicit operator policy, and verify `app.project` plus the resulting file after a `true` return.

## Example

```javascript
var created = app.newProject(projectPath);
if (!created) {
    throw new Error("Premiere Pro did not create the project");
}
```

## Known issues

- Behavior when `path` already exists: **Not documented**.
- Behavior when the parent directory is absent or unwritable: **Not documented**.
- Whether unsaved open projects trigger a prompt: **Not documented**.

## References

- [Premiere Pro Scripting Guide — Application](https://ppro-scripting.docsforadobe.dev/application/application/)
- [Adobe CEP PProPanel sample](https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx)
- [Adobe CEP TypeScript declarations](https://github.com/Adobe-CEP/Samples/blob/master/TypeScript/typings/PremierePro.11.1.2.d.ts)
