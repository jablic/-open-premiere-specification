# ExtendScript Application Reference

Status: Draft reference chapter  
Surface: ExtendScript DOM  
Specification unit: `SU-ES-APP-0001`  
Primary object: `app`  
Evidence level: A/B where sourced from Adobe or Adobe-maintained documentation; C/D/E only when explicitly marked.

## 1. Purpose

`app` is the global ExtendScript entry point for Adobe Premiere Pro automation. It exposes application-level state, preference paths, open project access, Media Encoder integration, QE activation, project opening/creation operations, workspace selection, proxy enablement, extension persistence, scratch disk configuration, event-panel logging, debug tracing, and project-view queries.

This chapter documents `app` as a developer-facing contract rather than as a short API listing. The critical distinction is that many `app` members operate at process or session scope. Code that uses them can affect open projects, proxy state, workspace state, extension lifetime, scratch disk configuration, and the user-visible Events panel.

## 2. Scope

This chapter covers the ExtendScript `app` object only.

Out of scope:

- UXP `Application` classes and modules.
- CEP `CSInterface` host bridge behaviour.
- QE DOM objects exposed after `app.enableQE()`.
- C++ SDK plugin entry points.
- Detailed behaviour of returned objects such as `Project`, `Encoder`, `Production`, `Properties`, and `SourceMonitor`.

Related future chapters:

- `Project`
- `Encoder`
- `Production`
- `Properties`
- `SourceMonitor`
- `QE DOM activation`
- `CEP evalScript bridge`
- `UXP Premiere DOM`

## 3. Object identity and lifetime

### 3.1 Global identity

`app` is a singleton-like global object exposed by Premiere Pro to ExtendScript. Scripts do not construct it. They use the global name directly.

```javascript
var version = app.version;
```

### 3.2 Lifetime

`app` exists for the lifetime of the Premiere Pro host process and is available to ExtendScript code executed inside that process.

### 3.3 Session-level state

Some members are read-only views of process state, while others mutate session or application state. Do not treat `app` as a passive data object.

Examples of session/application-affecting members:

- `app.setEnableProxies(enabled)`
- `app.setWorkspace(workspace)`
- `app.setExtensionPersistent(extensionID, persistent)`
- `app.setScratchDiskPath(path, scratchDiskType)`
- `app.quit()`
- `app.openDocument(...)`
- `app.newProject(path)`

## 4. Ownership and references

`app` does not own media, track items, sequences, or project items directly. It exposes access to higher-level services and containers.

Important references:

| Member | Referenced object or service | Notes |
|---|---|---|
| `app.project` | `Project` | Active project. In multi-project workflows, do not assume it is the only open project. |
| `app.projects` | `ProjectCollection` | Open projects collection. |
| `app.encoder` | `Encoder` | Adobe Media Encoder integration. |
| `app.production` | `Production` or null | Active Production when one is open. |
| `app.properties` | `Properties` | Preferences/properties access. |
| `app.sourceMonitor` | `SourceMonitor` | Source Monitor access. |
| `app.projectManager` | `ProjectManager` | Project management functions. |

## 5. Evidence classification

Evidence notation used in this chapter:

| Code | Meaning |
|---|---|
| A | Official Adobe documentation, Adobe-maintained documentation, SDK documentation, or official Adobe developer site. |
| B | Adobe samples, official starter projects, or documented sample code. |
| C | Reproduced experiment in this repository. |
| D | Community verified. |
| E | Hypothesis or unverified observation. |

No behaviour in this chapter should be treated as production-safe unless it is A, B, or explicitly marked as reproduced.

## 6. Attribute index

The following index is inventory-level. Detailed contract pages will be added per member.

| Attribute | Type / return | Contract summary | Evidence |
|---|---|---|---|
| `app.anywhere` | `Anywhere` | Access to Anywhere servers when running in discontinued Anywhere configuration. | A |
| `app.build` | `String`, read-only | Host build number as a string. | A |
| `app.encoder` | `Encoder` | Access to Adobe Media Encoder integration on the same system. Known Mac issue in Premiere 14.3.1–15, fixed in 22+. | A/D |
| `app.getAppPrefPath` | `String`, read-only | Path containing the active Premiere preference file. | A |
| `app.bind` | `Boolean` | Registers a callback for a named event. | A |
| `app.getAppSystemPrefPath` | `String`, read-only | Active non-user-specific configuration path. | A |
| `app.getPProPrefPath` | `String`, read-only | Path containing active Premiere preference file. | A |
| `app.getPProSystemPrefPath` | `String`, read-only | Active non-user-specific Premiere configuration path. | A |
| `app.learnPanelContentDirPath` | `String`, read-only | Learn panel content path. | A |
| `app.learnPanelExampleProjectDirPath` | `String`, read-only | Learn panel example projects path. | A |
| `app.metadata` | `Metadata`, read-only | Application metadata object. | A |
| `app.path` | `String`, read-only | Path to the Premiere Pro executable/application bundle. | A |
| `app.production` | `Production` or `null` | Active Production, if one is open. | A |
| `app.project` | `Project` | Active project. | A |
| `app.projectManager` | `ProjectManager` | Project management functions. | A |
| `app.projects` | `ProjectCollection`, read-only | Collection of open projects. | A |
| `app.properties` | `Properties`, read-only | Preference/property access object. | A |
| `app.sourceMonitor` | `SourceMonitor` | Source Monitor access. | A |
| `app.userGuid` | `String`, read-only | Creative Cloud user GUID. Treat as sensitive identifier. | A |
| `app.version` | `String`, read-only | Premiere Pro version string. | A |

## 7. Method index

The following index is inventory-level. Method-specific contract pages will be added under `Methods/`.

| Method | Return | Contract summary | Evidence |
|---|---|---|---|
| `app.enableQE()` | `true` when enabled | Enables QE DOM access. Treat QE usage as a separate, risk-classified surface. | A |
| `app.getEnableProxies()` | `1` or `0` | Returns current proxy enablement state. | A |
| `app.getWorkspaces()` | `Array<String>` or `null` | Returns available workspace names. | A |
| `app.isDocument(path)` | `Boolean` | Tests whether a file can be opened as a Premiere project. | A |
| `app.isDocumentOpen()` | `Boolean` | Tests whether at least one project is open. | A |
| `app.newProject(path)` | `Boolean` | Creates a new `.prproj` project at the specified path. | A |
| `app.openDocument(path, suppressConversionDialog, bypassLocateFileDialog, bypassWarningDialog, doNotAddToMRUList)` | `Boolean` | Opens a Premiere project file. | A |
| `app.openFCPXML(path, projPath)` | `Boolean` | Opens/imports an FCP XML into a Premiere project path. | A |
| `app.quit()` | Nothing | Quits Premiere Pro; user may be prompted to save. | A |
| `app.setEnableProxies(enabled)` | `1` if changed | Sets global proxy usage state. | A |
| `app.setExtensionPersistent(extensionID, persistent)` | `Boolean` | Controls whether a CEP extension remains loaded during session. | A |
| `app.setScratchDiskPath(path, scratchDiskType)` | `Boolean` | Sets a scratch disk path for a specified scratch disk type. | A |
| `app.setSDKEventMessage(message, decorator)` | Varies by implementation/docs | Writes a message to the Events panel. | A |
| `app.setWorkspace(workspace)` | `Boolean` | Switches active workspace. | A |
| `app.trace()` | `Boolean` | Writes to Premiere Pro debug console. | A |
| `app.getProjectViewIDs()` | `Array` or `null` | Returns IDs for open project views. | A |
| `app.getProjectFromViewID(viewID)` | `Project` or null-like | Resolves a project from a project view ID. | A |
| `app.getCurrentProjectViewSelection(viewID)` | collection-like result | Returns selected project-view items for a view. | A |
| `app.broadcastPrefsChanged()` | unspecified | Broadcasts preferences-changed notification. | A |

## 8. Developer contracts

### 8.1 Active project contract

`app.project` is the currently active project, not necessarily the only open project. For multi-project-aware tooling, prefer explicit project enumeration through `app.projects` where available and avoid silently assuming that operations should target `app.project`.

### 8.2 Project opening contract

`app.openDocument()` changes application/project state by opening a project. Treat it as a mutating operation. Tooling should report the path, dialog-suppression options, and MRU behaviour before executing unattended.

### 8.3 Project creation contract

`app.newProject(path)` creates a project file at a path. The documented signature does not automatically add `.prproj`; callers should pass a complete intended path and validate directory existence and write permissions before calling.

### 8.4 QE activation contract

`app.enableQE()` enables access to the QE DOM. This does not make QE DOM an ordinary supported scripting surface. QE calls must be documented separately with evidence level and risk classification.

### 8.5 Proxy enablement contract

`app.getEnableProxies()` and `app.setEnableProxies(enabled)` operate at application/session level. They should not be treated as per-project or per-sequence state unless a reproduced experiment proves otherwise.

### 8.6 Extension persistence contract

`app.setExtensionPersistent(extensionID, persistent)` affects CEP extension lifetime within the current session. Use persistence `0` during development/reload workflows and persistence `1` only when the extension must remain loaded while hidden.

### 8.7 Scratch disk contract

`app.setScratchDiskPath(path, scratchDiskType)` changes scratch disk configuration. Because scratch disks affect generated files and project workflows, production tools should log the previous path and requested new path.

## 9. Failure modes to document experimentally

The official method inventory is not enough. The following behaviours require repository experiments before being documented as facts:

- Does `app.openDocument()` return `false`, throw, or block when a file path does not exist?
- How do dialog-suppression flags interact with missing media, project conversion, and warning dialogs across versions?
- Does `app.newProject(path)` overwrite an existing `.prproj`, fail, or prompt?
- Does `app.setEnableProxies()` persist across project close, application restart, or only session?
- Does `app.setWorkspace()` fail silently for localized workspace names?
- Which event names are accepted by `app.bind()` in each supported Premiere version?
- What exact values can be used for `decorator` in `app.setSDKEventMessage()`?

## 10. Production guidance

- Never call `app.quit()` from a production automation flow without an explicit operator confirmation step.
- Treat `app.openDocument()` and `app.newProject()` as mutating operations; log inputs and user-dialog flags.
- Do not use QE DOM merely because it is available. Prefer documented ExtendScript or UXP APIs where they provide the required operation.
- Do not store `app.userGuid` in logs or exported diagnostics unless there is a clear privacy/legal reason.
- For CEP development, use `app.setExtensionPersistent(extensionID, 0)` while iterating and avoid shipping persistent extensions without a lifecycle reason.

## 11. Minimal examples

### Read version and build

```javascript
$.writeln('Premiere version: ' + app.version);
$.writeln('Premiere build: ' + app.build);
```

### Check whether a project is open

```javascript
if (app.isDocumentOpen()) {
    $.writeln('At least one project is open.');
} else {
    $.writeln('No project is currently open.');
}
```

### Enable QE with explicit risk boundary

```javascript
var enabled = app.enableQE();
if (enabled) {
    $.writeln('QE DOM enabled. Use only documented or separately verified QE calls.');
}
```

## 12. Evidence

Primary inventory source:

- `https://ppro-scripting.docsforadobe.dev/application/application/`

Related Adobe developer sources:

- `https://developer.adobe.com/premiere-pro/uxp/`
- `https://developer.adobe.com/premiere-pro/uxp/resources/fundamentals/apis/`

## 13. Open research tasks

- `EXP-ES-APP-0001`: Verify `app.openDocument()` failure behaviour for nonexistent paths.
- `EXP-ES-APP-0002`: Verify `app.newProject()` behaviour when the target file already exists.
- `EXP-ES-APP-0003`: Verify proxy enablement persistence across application restart.
- `EXP-ES-APP-0004`: Enumerate supported `app.bind()` events in Premiere 2024, 2025, and 2026.
- `EXP-ES-APP-0005`: Verify localized workspace handling in `app.setWorkspace()`.
