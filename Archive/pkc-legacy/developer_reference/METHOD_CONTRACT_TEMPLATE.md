# Method Contract Template

Use this template for every API method page.

```markdown
# MethodName()

## Summary

One-paragraph description.

## Surface

- Surface: ExtendScript / UXP / CEP / QE / C++ SDK
- Status: Official / Adobe Sample / Reproduced / Community Verified / Hypothesis
- Minimum verified Premiere version:
- Last verified:

## Syntax

```javascript
// Example syntax here
```

## Parameters

| Name | Type | Required | Description | Constraints |
|------|------|----------|-------------|-------------|

## Return Value

| Type | Description |
|------|-------------|

## Reads

List objects or state read by the method.

## Mutates

List objects or state modified by the method.

## Creates

List objects created by the method.

## Does Not Mutate

List important objects that remain unchanged.

## Preconditions

Required state before calling.

## Postconditions

Expected state after successful completion.

## Failure Modes

Known failure cases and symptoms.

## Side Effects

Undo stack, selection state, UI state, cache, render state, background jobs, or file system effects.

## Threading / Blocking Behaviour

State whether the method blocks the UI or requires main-thread context if known.

## Performance Notes

Large project behaviour, batch usage risks, and scaling observations.

## Version Matrix

| Premiere Version | Status | Notes |
|------------------|--------|-------|

## Evidence

List evidence IDs.

## Examples

Code samples with expected output.

## Production Notes

Operational guidance for real projects.

## Related APIs

Links to related object and method pages.
```
