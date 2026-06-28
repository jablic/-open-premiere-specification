# Master Table of Contents

Working title: **Adobe Premiere Pro Developer Reference**.

Purpose: define the complete editorial map for technical documentation about Adobe Premiere Pro developer interfaces.

## Volume 0 — Orientation

### 0.1 Scope
- What this reference covers.
- What it does not cover.
- Intended audience: plugin, panel, extension, scripting, automation, and pipeline developers.

### 0.2 Developer Surface Map
- ExtendScript DOM.
- UXP Premiere API.
- CEP Panels.
- QE DOM.
- C++ SDK.
- XML / FCPXML.
- Caption formats.
- MOGRT / Essential Graphics.
- Media pipeline and cache interfaces.

### 0.3 Evidence and Trust Levels
- Official Adobe.
- Adobe samples.
- Reproduced experiment.
- Community verified.
- Hypothesis.

### 0.4 Versioning Model
- Premiere Pro version.
- API surface version.
- SDK version.
- CEP runtime version.
- UXP runtime version.

## Volume 1 — Host Architecture

### 1.1 Premiere Process Model
- Host application process.
- Panel/runtime process boundaries.
- Native plugin loading.
- Scripting execution context.

### 1.2 Extension Communication
- CEP JavaScript to ExtendScript bridge.
- UXP module access.
- Native plugin boundaries.
- File-based and IPC-based integration patterns.

### 1.3 Execution Models
- ExtendScript synchronous execution.
- CEP browser runtime.
- UXP async model.
- Native SDK callbacks.

### 1.4 Safety Model
- Project mutation.
- Undo implications.
- Destructive vs non-destructive operations.
- Media file vs project reference.

## Volume 2 — ExtendScript DOM Reference

### 2.1 Application
- Overview.
- Global `app` object.
- Project access.
- QE enablement.
- Encoder access.
- Application-level commands.

### 2.2 Project
- Identity and lifecycle.
- `rootItem`.
- Import operations.
- Save and close operations.
- Sequence creation.
- Metadata operations.

### 2.3 ProjectItem
- Identity.
- Bin item vs media item vs sequence item.
- Media references.
- Proxy / relink behaviour.
- Metadata.

### 2.4 Sequence
- Timeline identity.
- Track collections.
- Timebase and frame rate.
- Clip insertion.
- Export operations.
- Marker collections.
- XML relationships.

### 2.5 Tracks
- Video tracks.
- Audio tracks.
- Caption tracks.
- Track item collections.
- Locking, targeting, muting, visibility.

### 2.6 TrackItem
- Timeline instance semantics.
- Reference to ProjectItem.
- In/out points.
- Time remapping.
- Components and effects.

### 2.7 Markers
- Project markers.
- Sequence markers.
- Clip markers.
- Scope and identity.

### 2.8 Components and Parameters
- Component model.
- Effect components.
- Motion / opacity / volume.
- Parameter typing.
- Keyframes.

### 2.9 Encoder
- Export calls.
- Media Encoder interaction.
- Presets.
- Queueing.

### 2.10 Time and Timecode
- Ticks.
- Seconds.
- Frames.
- Drop-frame and non-drop-frame.
- Conversion risks.

## Volume 3 — QE DOM Reference

### 3.1 QE Scope and Disclaimer
- Undocumented status.
- Stability risk.
- Version drift.
- Required evidence level.

### 3.2 QE Application Entry Points
- `app.enableQE()`.
- `qe` global object.
- Project and sequence access.

### 3.3 QE Project
- Project accessors.
- Item enumeration.
- Known differences from ExtendScript DOM.

### 3.4 QE Sequence
- Timeline access.
- Track manipulation.
- Editing operations.
- Known unsupported behaviours.

### 3.5 QE Validation Protocol
- How to verify QE calls.
- Required experiment format.
- Compatibility matrix requirements.

## Volume 4 — CEP Panels

### 4.1 CEP Runtime
- Chromium Embedded Framework.
- Extension folders.
- Manifest.
- Host application targeting.

### 4.2 CSInterface
- Lifecycle.
- Host environment access.
- Extension events.
- Host events.

### 4.3 `evalScript()` Bridge
- JavaScript to ExtendScript invocation.
- Callback behaviour.
- Error handling.
- Platform-specific caveats.

### 4.4 Packaging and Deployment
- Extension signing.
- Debug mode.
- Install locations.
- ZXP packaging.

### 4.5 CEP Security and Compatibility
- CEF version constraints.
- Node integration.
- CSP issues.
- Runtime deprecation risks.

## Volume 5 — UXP Extensions

### 5.1 UXP Runtime
- Plugin manifest.
- Panels.
- Commands.
- Permissions.

### 5.2 Premiere API Entry Point
- `require("premierepro")`.
- Application module.
- Async behaviours.

### 5.3 UXP vs ExtendScript
- Execution model differences.
- API naming differences.
- Migration constraints.

### 5.4 UXP Hybrid Plugins
- Native extension boundary.
- C++ integration.
- Performance-critical workloads.

## Volume 6 — C++ SDK

### 6.1 SDK Structure
- Headers.
- Samples.
- Resources.
- Build requirements.

### 6.2 Importers
- Plugin discovery.
- Resources.
- Format registration.
- Import callbacks.

### 6.3 Exporters
- Exporter lifecycle.
- Presets.
- AME integration.
- Import-into-project behaviour.

### 6.4 Effects
- Video effects.
- Audio effects.
- Parameter suites.
- GPU and pixel formats.

### 6.5 Playback and Rendering
- Playback pipeline.
- Mercury engine.
- Memory management.
- Threading.

## Volume 7 — Interchange and Internal Formats

### 7.1 Premiere XML / FCPXML
- Export model.
- Import model.
- Roundtrip risk.
- Unsupported nodes.
- Safe transformations.

### 7.2 Captions
- Caption tracks.
- Caption items.
- Text runs.
- Styling.
- Time mapping.
- Serialization.

### 7.3 MOGRT and Essential Graphics
- Template import.
- Parameter editing.
- Media replacement.
- After Effects dependencies.

### 7.4 Media References
- Source media.
- Proxies.
- Offline media.
- Relink workflows.

### 7.5 Cache and Derived Files
- Media Cache.
- Peak files.
- Conformed audio.
- Preview files.

## Volume 8 — Behaviour Contracts

### 8.1 Mutation Contracts
- What each API mutates.
- What each API must not mutate.
- Undo implications.

### 8.2 Failure Modes
- Null references.
- Offline media.
- Locked tracks.
- Invalid project state.
- Unsupported formats.

### 8.3 Performance Contracts
- Large project behaviours.
- Batch operation risks.
- UI blocking.
- Background processing.

## Volume 9 — Version Compatibility

### 9.1 Premiere Version Matrix
- 2022.
- 2023.
- 2024.
- 2025.
- 2026.

### 9.2 API Surface Matrix
- ExtendScript.
- CEP.
- UXP.
- QE.
- C++ SDK.

### 9.3 Deprecation and Migration
- CEP to UXP.
- ExtendScript to UXP.
- Legacy SDK behaviours.

## Volume 10 — Reverse Engineering

### 10.1 Experiment Protocol
- Hypothesis.
- Environment.
- Procedure.
- Observation.
- Conclusion.
- Confidence.

### 10.2 QE Experiments
- Discovery.
- Invocation.
- Version testing.

### 10.3 Serialization Experiments
- Project file observations.
- XML roundtrip.
- Caption serialization.

## Volume 11 — Production Cookbook

### 11.1 VFX Pull Lists
- Marker-based workflows.
- Shot identifiers.
- Thumbnail extraction.
- XLSX output.

### 11.2 Relink and Proxy Workflows
- ProjectItem-level relink.
- TrackItem implications.
- Safety checks.

### 11.3 Caption and Localization Workflows
- Text replacement.
- Styling preservation.
- Timing preservation.

### 11.4 Delivery and QC
- Export automation.
- XML verification.
- Project integrity reports.
