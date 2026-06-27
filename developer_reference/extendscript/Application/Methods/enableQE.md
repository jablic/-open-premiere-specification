# app.enableQE()

Status: Draft method contract  
Surface: ExtendScript DOM  
Specification unit: `SU-ES-APP-METHOD-0001`  
Evidence level: A for existence/signature; C required for detailed behavioural claims.

## Purpose

Enables access to Premiere Pro's QE DOM from ExtendScript.

## Syntax

```javascript
app.enableQE()
```

## Parameters

None.

## Return value

The scripting reference documents a truthy result when QE DOM was enabled.

## Mutates

- Application scripting environment.
- Availability of the `qe` global object/surface.

## Does not imply

- That QE DOM calls are officially supported for all production use.
- That QE APIs are stable across versions.
- That QE methods follow the same contracts as ExtendScript DOM methods.

## Preconditions

- Script is executed in Premiere Pro ExtendScript context.
- Host version exposes `app.enableQE()`.

## Postconditions

- QE DOM can be addressed by scripts, subject to host/version availability.

## Failure modes requiring experiments

- Behaviour when called multiple times in the same session.
- Behaviour in headless or panel-invoked scripts.
- Behaviour when the host has no open project.
- Version-specific differences.

## Production notes

Use `app.enableQE()` only when the desired operation is unavailable through documented ExtendScript/UXP APIs. All QE usage must be isolated, logged, and guarded by version/evidence checks.

## Evidence

- `https://ppro-scripting.docsforadobe.dev/application/application/#appenableqe`
