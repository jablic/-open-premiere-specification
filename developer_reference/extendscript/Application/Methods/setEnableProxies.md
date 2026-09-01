# app.setEnableProxies()

Surface: ExtendScript DOM
Evidence: A/B for existence and basic semantics; scope and persistence details: Not documented.

## Syntax

```javascript
app.setEnableProxies(enabled)
```

## Parameters

| Parameter | Type | Meaning |
|---|---|---|
| `enabled` | `Number` | Use `1` to enable proxy usage and `0` to disable it. |

## Returns

The application inventory records an integer result. Adobe-maintained typings expose a boolean-compatible result, while the PProPanel sample uses the paired getter to observe state. Treat the exact success-code semantics beyond truthiness as **Not documented**.

## Behavior and side effects

- Changes proxy usage state at application/session level according to the public scripting sample.
- It does not attach or detach proxy media from a `ProjectItem`.
- It does not prove a per-sequence or per-project persistence model.

## Preconditions

- Script runs in Premiere Pro ExtendScript context.
- `enabled` is normalized to `0` or `1`.

## Production contract

Read the current state with `app.getEnableProxies()`, record it, set the requested value, then read it back. If a tool temporarily changes proxy usage, restore the original state in a guarded cleanup path.

## Example

```javascript
var previous = app.getEnableProxies();
var result = app.setEnableProxies(1);
var actual = app.getEnableProxies();

if (!actual) {
    throw new Error("Proxy usage was not enabled");
}
```

## Known issues

- Scope across multiple open projects: **Not documented**.
- Persistence after closing a project or restarting Premiere Pro: **Not documented**.
- Exact return values for no-op and invalid numeric inputs: **Not documented**.

## References

- [Premiere Pro Scripting Guide — Application](https://ppro-scripting.docsforadobe.dev/application/application/)
- [Adobe CEP PProPanel proxy sample](https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx)
- [Adobe CEP TypeScript declarations](https://github.com/Adobe-CEP/Samples/blob/master/TypeScript/typings/PremierePro.11.1.2.d.ts)
