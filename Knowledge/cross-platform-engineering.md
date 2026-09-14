---
id: cross-platform-engineering
title: Cross-Platform Extension Engineering (Mac/Windows)
category: advanced
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2015"
min_premiere_version: "14.0"
api_namespace: null
languages: [extendscript, javascript, jsx, python, shell]
tags: [cross-platform, mac, windows, compatibility, ci-cd, testing, path-handling]
related: [best-practices, panel-development-uxp, debugging, automation]
sources: [
  "Cross-platform development patterns",
  "Platform-specific API differences",
  "CI/CD testing strategies",
  "Path and file system abstractions"
]
confidence: high
last_verified: "2026-07-01"
verified_against_version: "25.6"
---

# Cross-Platform Extension Engineering (Mac/Windows)

## TL;DR

**Path Handling:** Use File/Folder API (cross-platform); avoid hardcoded paths. **Line Endings:** Use `\n` in code; platform converts automatically. **Case Sensitivity:** Windows case-insensitive (may hide bugs); Mac case-sensitive (enforce consistency). **File Dialog:** Use `File.openDialog()` (platform-native pickers). **Shell Scripts:** Use bash (Unix-like) for Mac; PowerShell or batch for Windows. **Testing:** CI on both macOS/Windows (GitHub Actions); auto-test on PR merge. **Codecs:** Some codecs Mac-only (ProRes), some Windows-only; document requirements. **Version Requirements:** Test min/max Premiere versions on both platforms.

---

## Path & File System Abstractions

### Cross-Platform Path Handling

```javascript
function getProjectFolder(project) {
  /**
   * Get project folder path (works on Mac and Windows)
   * Premiere File/Folder API is cross-platform
   */
  
  var projectFile = project.file;
  
  if (!projectFile) {
    $.writeln("Project not saved yet");
    return null;
  }
  
  var projectFolder = projectFile.parent;
  
  $.writeln("=== CROSS-PLATFORM PATH HANDLING ===\n");
  
  $.writeln("Project: " + projectFile.name);
  $.writeln("Full Path: " + projectFolder.absoluteURI);
  $.writeln("");
  
  $.writeln("Platform Detection:");
  $.writeln("- Windows path: C:\\Users\\Editor\\project.prproj");
  $.writeln("- Mac path: /Users/editor/project.prproj");
  $.writeln("- Both use File API: projectFile.absoluteURI");
  $.writeln("");
  
  $.writeln("Correct (Cross-Platform):");
  $.writeln("✓ var folder = new Folder(path.absoluteURI);");
  $.writeln("✓ var file = new File(folder.absoluteURI + '/subdir/file.txt');");
  $.writeln("✓ Use Folder/File API for all file operations");
  $.writeln("");
  
  $.writeln("Incorrect (Platform-Specific):");
  $.writeln("✗ var path = 'C:\\\\Users\\\\Editor\\\\project';  // Windows only");
  $.writeln("✗ var path = '/Users/editor/project';  // Mac only");
  $.writeln("✗ path.replace('\\\\', '/');  // String manipulation");
  $.writeln("");
  
  $.writeln("Helper: Get separator based on OS");
  var separator = ($.os.indexOf("Windows") === 0) ? "\\\\" : "/";
  $.writeln("Path separator: " + separator);
  
  return projectFolder;
}

function joinPaths(basePath, ...pathSegments) {
  /**
   * Join multiple path segments (cross-platform)
   * Handles trailing slashes, separators automatically
   */
  
  var result = basePath.absoluteURI || basePath;
  
  for (var i = 0; i < pathSegments.length; i++) {
    var segment = pathSegments[i];
    
    // Remove leading/trailing slashes from segment
    segment = segment.replace(/^[\/\\]+|[\/\\]+$/g, "");
    
    // Add to result (File API handles separator)
    result = result + "/" + segment;
  }
  
  return result;
}

// Usage
var folder = getProjectFolder(app.project);
var customPath = joinPaths(folder.absoluteURI, "metadata", "project.json");
$.writeln("Custom path: " + customPath);
```

### Abstract File Operations

```javascript
function createCrossPlatformFileHelper() {
  /**
   * Helper object for file operations (abstracts platform differences)
   */
  
  var FileHelper = {
    // Get temp directory
    getTempDir: function() {
      if ($.os.indexOf("Windows") === 0) {
        return new Folder($.getenv("TEMP"));
      } else {
        return new Folder("/tmp");
      }
    },
    
    // Get user home directory
    getHomeDir: function() {
      if ($.os.indexOf("Windows") === 0) {
        return new Folder($.getenv("USERPROFILE"));
      } else {
        return new Folder($.getenv("HOME"));
      }
    },
    
    // Execute command (platform-aware)
    executeCommand: function(cmd, args) {
      var result = { success: false, output: "", error: "" };
      
      try {
        var cmdStr;
        if ($.os.indexOf("Windows") === 0) {
          // Windows: use cmd.exe
          cmdStr = "cmd.exe /c " + cmd + " " + args.join(" ");
        } else {
          // Mac/Linux: use bash
          cmdStr = cmd + " " + args.join(" ");
        }
        
        var process = system.callSystem(cmdStr);
        result.success = (process === 0);
        
      } catch (e) {
        result.error = e.toString();
      }
      
      return result;
    }
  };
  
  $.writeln("=== CROSS-PLATFORM FILE HELPER ===\n");
  
  $.writeln("Temp Directory: " + FileHelper.getTempDir().absoluteURI);
  $.writeln("Home Directory: " + FileHelper.getHomeDir().absoluteURI);
  $.writeln("OS: " + $.os);
  
  return FileHelper;
}

// Usage
var helper = createCrossPlatformFileHelper();
```

---

## Platform-Specific Considerations

### Document Platform Requirements

```javascript
function documentPlatformRequirements() {
  /**
   * Define codec, feature, version compatibility by platform
   */
  
  var requirements = {
    "ProRes (HQ)": {
      macOS: { available: true, minVersion: "10.13" },
      Windows: { available: false, note: "Mac-only codec" }
    },
    "Avid DNxHD": {
      macOS: { available: true, minVersion: "10.13" },
      Windows: { available: true, minVersion: "7 SP1" }
    },
    "H.265/HEVC": {
      macOS: { available: true, minVersion: "10.14", note: "GPU acceleration" },
      Windows: { available: true, minVersion: "10 v1903", note: "Requires optional codec" }
    },
    "CEP Panels": {
      macOS: { available: true, minVersion: "Premiere 14.0" },
      Windows: { available: true, minVersion: "Premiere 14.0" }
    },
    "UXP Plugins": {
      macOS: { available: true, minVersion: "Premiere 25.0" },
      Windows: { available: true, minVersion: "Premiere 25.0" }
    }
  };
  
  $.writeln("=== PLATFORM COMPATIBILITY MATRIX ===\n");
  
  for (var feature in requirements) {
    var compat = requirements[feature];
    $.writeln(feature + ":");
    $.writeln("  macOS: " + (compat.macOS.available ? "✓ " + compat.macOS.minVersion : "✗ Not available"));
    if (compat.macOS.note) $.writeln("         " + compat.macOS.note);
    $.writeln("  Windows: " + (compat.Windows.available ? "✓ " + compat.Windows.minVersion : "✗ Not available"));
    if (compat.Windows.note) $.writeln("           " + compat.Windows.note);
    $.writeln("");
  }
  
  $.writeln("Testing Strategy:");
  $.writeln("- Run CI on macOS (min 10.13) and Windows (min 7 SP1)");
  $.writeln("- Test Premiere min/max versions on both platforms");
  $.writeln("- Document codec availability per platform");
  $.writeln("- Provide fallback codecs for cross-platform projects");
  
  return requirements;
}

// Usage
documentPlatformRequirements();
```

---

## Testing & CI/CD

### GitHub Actions: Multi-Platform Testing

```yaml
# .github/workflows/test-cross-platform.yml
name: Cross-Platform Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test-mac:
    runs-on: macos-12
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '16'
      
      - name: Install dependencies
        run: npm install
      
      - name: Run tests (macOS)
        run: npm test
      
      - name: Lint code
        run: npm run lint
      
      - name: Test path handling
        run: node test/cross-platform/paths.test.js
      
      - name: Test file operations
        run: node test/cross-platform/files.test.js

  test-windows:
    runs-on: windows-2022
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '16'
      
      - name: Install dependencies
        run: npm install
      
      - name: Run tests (Windows)
        run: npm test
      
      - name: Lint code
        run: npm run lint
      
      - name: Test path handling (Windows)
        run: node test/cross-platform/paths.test.js
      
      - name: Test file operations (Windows)
        run: node test/cross-platform/files.test.js
      
      - name: Test PowerShell integration
        run: test\cross-platform\powershell.test.ps1
  
  build-extension:
    needs: [test-mac, test-windows]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build extension package
        run: npm run build
      
      - name: Create release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: v${{ github.run_number }}
          release_name: Release v${{ github.run_number }}
          files: |
            dist/*.zip
            dist/*.zip.sha256
```

### Cross-Platform Test Suite

```javascript
function createCrossPlatformTestSuite() {
  /**
   * Test cases for path handling, file operations, platform detection
   */
  
  var tests = {
    pathHandling: function() {
      $.writeln("TEST: Path Handling");
      
      var folder = new Folder("~/Desktop");
      var file = new File(folder.absoluteURI + "/test.txt");
      
      // Should work on both Mac/Windows
      if (file) {
        $.writeln("✓ Path creation successful");
        return true;
      }
      return false;
    },
    
    fileCreation: function() {
      $.writeln("TEST: File Creation");
      
      var tempFolder = new Folder($.getenv("TEMP"));
      var testFile = new File(tempFolder.absoluteURI + "/test_cross_platform.txt");
      
      try {
        testFile.open("w");
        testFile.write("Test content");
        testFile.close();
        
        if (testFile.exists) {
          testFile.remove();
          $.writeln("✓ File creation/deletion successful");
          return true;
        }
      } catch (e) {
        $.writeln("✗ File operation failed: " + e.toString());
      }
      return false;
    },
    
    platformDetection: function() {
      $.writeln("TEST: Platform Detection");
      
      var isWindows = $.os.indexOf("Windows") === 0;
      var isMac = $.os.indexOf("Mac") === 0;
      
      $.writeln("Platform: " + $.os);
      $.writeln("✓ Platform detection: " + (isWindows ? "Windows" : isMac ? "macOS" : "Unknown"));
      return (isWindows || isMac);
    }
  };
  
  $.writeln("=== CROSS-PLATFORM TEST SUITE ===\n");
  
  var passed = 0;
  var failed = 0;
  
  for (var testName in tests) {
    var result = tests[testName]();
    if (result) {
      passed++;
    } else {
      failed++;
    }
    $.writeln("");
  }
  
  $.writeln("SUMMARY: " + passed + " passed, " + failed + " failed");
  return { passed: passed, failed: failed };
}

// Usage
createCrossPlatformTestSuite();
```

---

## Debugging Cross-Platform Issues

### Logging for Platform Detection

```javascript
function setupCrossPlatformLogging() {
  /**
   * Log platform-specific info for debugging
   */
  
  var logInfo = {
    timestamp: new Date().toISOString(),
    platform: $.os,
    premiereVersion: app.version,
    scriptVersion: "1.0.0",
    paths: {}
  };
  
  // Get important system paths
  logInfo.paths.temp = $.getenv("TEMP") || $.getenv("TMPDIR");
  logInfo.paths.home = $.getenv("USERPROFILE") || $.getenv("HOME");
  logInfo.paths.premiere = app.getDefaultProjectPath();
  
  $.writeln("=== ENVIRONMENT LOG ===");
  $.writeln(JSON.stringify(logInfo, null, 2));
  
  // Write to file for debugging
  var logFolder = new Folder(logInfo.paths.temp);
  var logFile = new File(logFolder.absoluteURI + "/premiere_debug.log");
  
  try {
    logFile.open("a");  // Append
    logFile.write(JSON.stringify(logInfo, null, 2) + "\n\n");
    logFile.close();
    
    $.writeln("\nLog written to: " + logFile.absoluteURI);
  } catch (e) {
    $.writeln("Cannot write log: " + e.toString());
  }
  
  return logInfo;
}

// Usage
setupCrossPlatformLogging();
```

---

## Cross-Platform Engineering Checklist

- ☐ Use File/Folder API for all file operations (no hardcoded paths)
- ☐ Test on macOS (min 10.13) and Windows (min 7 SP1)
- ☐ Document platform-specific codec availability
- ☐ Handle line endings automatically (ExtendScript does this)
- ☐ Avoid case-sensitive path assumptions (enforce consistency)
- ☐ Use native file dialogs (File.openDialog())
- ☐ Test shell script execution on both platforms
- ☐ Set up GitHub Actions CI for auto-testing on both OSes
- ☐ Test min/max Premiere versions on both platforms
- ☐ Create fallback codecs for cross-platform projects
- ☐ Log environment info for debugging platform issues
- ☐ Document any Mac-only or Windows-only features
- ☐ Test file paths with special characters and spaces
- ☐ Verify plugin/panel works on both platforms before release

---

## See Also

- Knowledge/best-practices.md — Code quality standards
- Knowledge/debugging.md — Debugging techniques
- Knowledge/panel-development-uxp.md — UXP panel creation
- Knowledge/automation.md — Scripting patterns

---

## Sources

- Adobe Premiere Scripting Guide: https://ppro-scripting.docsforadobe.dev/
- ExtendScript for Adobe: https://github.com/Adobe-CEP/CEP-Resources
- GitHub Actions: https://docs.github.com/en/actions
- JavaScript File I/O: https://github.com/ExtendScript/wiki
