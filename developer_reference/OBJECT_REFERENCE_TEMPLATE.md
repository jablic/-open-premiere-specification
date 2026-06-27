# Object Reference Template

Use this template for every object page.

```markdown
# ObjectName

## Summary

What this object represents in Premiere Pro.

## Developer Surfaces

| Surface | Name | Status |
|---------|------|--------|
| ExtendScript | | |
| UXP | | |
| CEP | | |
| QE | | |
| C++ SDK | | |

## Identity

How object identity is established, retained, lost, or serialized.

## Lifetime

When the object is created, modified, invalidated, and destroyed.

## Ownership and References

What owns this object and what this object references.

## State Machine

Lifecycle states and valid transitions.

## Properties

| Name | Type | Mutable | Description | Evidence |
|------|------|---------|-------------|----------|

## Methods

| Name | Summary | Mutates | Returns | Evidence |
|------|---------|---------|---------|----------|

## Mutation Rules

Contract-level rules affecting this object.

## Serialization Mapping

XML, project file, caption JSON, or other representation if known.

## Cross-Surface Mapping

How this object maps across ExtendScript, UXP, CEP, QE, and SDK.

## Known Issues

Known bugs, undocumented behaviours, and version-specific caveats.

## Version Matrix

| Premiere Version | Status | Notes |
|------------------|--------|-------|

## Reverse Engineering Notes

Experimental observations only.

## Production Notes

Practical notes for automation, large projects, and pipeline tools.

## Examples

Minimal and production-grade examples.

## See Also

Related pages.
```
