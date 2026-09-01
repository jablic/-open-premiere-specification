# app.setExtensionPersistent()

Surface: ExtendScript DOM / CEP integration
Evidence: A/B for signature and purpose; lifecycle edge cases: Not documented.

## Syntax

```javascript
app.setExtensionPersistent(extensionID, persistent)
```

## Parameters

| Parameter | Type | Meaning |
|---|---|---|
| `extensionID` | `String` | CEP extension identifier declared in the extension manifest. |
| `persistent` | `Number` | Persistence state; use `0` to disable and `1` to enable. |

The public declaration permits an optional state parameter in some Adobe-maintained typings; this reference uses the explicit two-argument form from the application inventory.

## Returns

Adobe-maintained typings expose `Boolean`. The precise meaning of `false` and whether it indicates a rejected state transition or an invalid ID is **Not documented**.

## Behavior and side effects

- Controls whether a CEP extension remains loaded during the current Premiere Pro session.
- Changes extension lifecycle behavior; it is not a filesystem or manifest edit.
- It does not establish persistence across application restarts unless separately verified.

## Preconditions

- The extension is loaded in the current Premiere Pro session.
- `extensionID` exactly matches the CEP manifest identifier.

## Production contract

Use `0` during development when unload/reload behavior is required. Use `1` only when a lifecycle requirement justifies keeping the extension loaded while hidden. Log the extension ID and requested state, and treat the return value as a failure signal.

## Example

```javascript
var changed = app.setExtensionPersistent("com.example.panel", 1);
if (!changed) {
    throw new Error("Could not change extension persistence");
}
```

## Known issues

- Exact unload timing after setting `0`: **Not documented**.
- Behavior for an extension ID that is not loaded: **Not documented**.
- Persistence across Premiere Pro restart: **Not documented**.

## References

- [Premiere Pro Scripting Guide — Application](https://ppro-scripting.docsforadobe.dev/application/application/)
- [Adobe CEP TypeScript declarations](https://github.com/Adobe-CEP/Samples/blob/master/TypeScript/typings/PremierePro.11.1.2.d.ts)
- [Adobe CEP PProPanel manifest](https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/CSXS/manifest.xml)
