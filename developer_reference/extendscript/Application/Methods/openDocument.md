# app.openDocument()

Surface: ExtendScript DOM
Evidence: A/B for signature and sample usage; detailed failure behavior: Not documented.

## Syntax

```javascript
app.openDocument(
    path,
    suppressConversionDialog,
    bypassLocateFileDialog,
    bypassWarningDialog,
    doNotAddToMRUList
)
```

## Parameters

| Parameter | Type | Meaning |
|---|---|---|
| `path` | `String` | Path to the Premiere project file. |
| `suppressConversionDialog` | `Boolean` | Suppresses the project-conversion dialog when `true`. |
| `bypassLocateFileDialog` | `Boolean` | Bypasses the locate-files dialog when `true`. |
| `bypassWarningDialog` | `Boolean` | Bypasses warning dialogs when `true`. |
| `doNotAddToMRUList` | `Boolean` | Prevents adding the project to the Most Recently Used list when `true`. |

The public signature documents the flags, but does not define their precedence or every dialog that they suppress.

## Returns

`Boolean`. Adobe-maintained typings describe `true` as successful opening of the project. Exact behavior for a missing path, invalid project, or cancelled dialog is **Not documented**.

## Behavior and side effects

- Opens a project document and changes Premiere's project context.
- May trigger conversion, locate-media, or warning dialogs unless the corresponding flags are enabled.
- May change the MRU list unless `doNotAddToMRUList` is `true`.
- The method is synchronous in ExtendScript/CEP usage.

## Preconditions

- Script runs in Premiere Pro ExtendScript context.
- `path` identifies a file the host can attempt to open.

## Production contract

Validate the path before calling, log all five arguments, and do not suppress dialogs silently in an operator-facing workflow. After a successful return, re-read `app.project` and verify the expected project identity instead of relying on the boolean alone.

## Example

```javascript
var opened = app.openDocument(
    projectPath,
    false, // allow conversion dialog
    false, // allow locate-files dialog
    false, // allow warning dialog
    true   // do not add to MRU
);

if (!opened) {
    throw new Error("Premiere Pro did not open the project");
}
```

## Known issues

- Return value and dialog behavior for nonexistent or malformed files: **Not documented**.
- Whether the method waits for all project/media initialization before returning: **Not documented**.
- Version-specific differences in conversion and warning dialogs require experiments.

## References

- [Premiere Pro Scripting Guide — Application](https://ppro-scripting.docsforadobe.dev/application/application/)
- [Adobe CEP PProPanel sample](https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx)
- [Adobe CEP TypeScript declarations](https://github.com/Adobe-CEP/Samples/blob/master/TypeScript/typings/PremierePro.11.1.2.d.ts)
