---
id: advanced-audio-engineering
title: Advanced Audio Engineering & Standards
category: advanced
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2015"
min_premiere_version: "14.0"
api_namespace: null
languages: [extendscript, javascript, jsx]
tags: [audio, loudness, surround-sound, dolby-atmos, mixing, broadcast-standards, loudness-metering]
related: [audio-api, codec-media-reference, export-rendering-media-encoder, real-world-production-workflows]
sources: [
  "Broadcast loudness standards",
  "Audio engineering practices",
  "Dolby specifications"
]
confidence: high
last_verified: "2026-07-01"
verified_against_version: "25.6"
---

# Advanced Audio Engineering & Standards

## TL;DR

**Sample Rates:** 48 kHz broadcast standard (must verify project settings). **Loudness Metering:** Use LUFS (Loudness Units relative to Full Scale), not dB. Broadcast specs: -23 LUFS (streaming), -24 LUFS (cinema), -27 LUFS (TV). **Surround Sound:** 5.1 (6 channels: L, R, C, LFE, Ls, Rs), 7.1 (8 channels). **Dolby Atmos:** Object-based audio (immersive format). **Audio Workflows:** Separate dialogue/music/effects tracks → mix → master → loudness-normalize → deliver. **Scripting:** Limited API for audio (read track count, verify sample rate); use external tools for mixing.

---

## Audio Standards & Specifications

### Broadcast Loudness Standards

| Standard | Target LUFS | Platform | Notes |
|---|---|---|---|
| **EBU R128** | -23 LUFS | European broadcast | ITU-R BS.1770-4 standard |
| **ATSC A/85** | -24 LUFS | US/Canada broadcast | Dialog loudness -27 LUFS |
| **Netflix** | -27 LUFS | Streaming | Integrated loudness |
| **Spotify/Apple Music** | -14 LUFS | Music streaming | Different target |
| **Dolby Cinema** | -24 LUFS | Cinema (surround) | Requires object-based mix |
| **YouTube** | Normalized | Web | Auto-normalizes on playback |

### Sample Rate & Bit Depth Standards

| Format | Sample Rate | Bit Depth | Use Case |
|---|---|---|---|
| **Broadcast SD** | 48 kHz | 16-bit | PAL/NTSC standard |
| **Broadcast HD** | 48 kHz | 16-24 bit | Modern HD broadcast |
| **Streaming** | 48 kHz | 16-bit | Standard web delivery |
| **Cinema** | 48 kHz | 24-bit | DCI-compliant |
| **Music Production** | 44.1/48 kHz | 24-bit | Studio master |

---

## Loudness Metering & Verification

### Check Project Audio Settings

```javascript
function verifyAudioSettings(sequence) {
  /**
   * Verify audio configuration meets broadcast standards
   * Note: Limited ExtendScript API for audio; mostly read-only
   */
  
  var report = {
    trackCount: 0,
    audioTracks: [],
    sampleRate: "unknown",
    issues: [],
    recommendations: []
  };
  
  if (!sequence) {
    report.issues.push("No active sequence");
    return report;
  }
  
  // Count audio tracks
  if (sequence.audioTracks) {
    report.trackCount = sequence.audioTracks.length;
    
    for (var i = 0; i < sequence.audioTracks.length; i++) {
      var track = sequence.audioTracks[i];
      var clipCount = track.clips ? track.clips.length : 0;
      
      report.audioTracks.push({
        index: i,
        clipCount: clipCount,
        isMuted: track.isMuted,
        isSolo: track.isSolo
      });
    }
  }
  
  // Check project settings (requires external tool to read)
  // In real workflow, user must verify: File → Project Settings → Audio
  report.sampleRate = "48 kHz (verify in Project Settings)";
  report.bitDepth = "16-24 bit (verify in Project Settings)";
  
  // Validate
  if (report.trackCount < 2) {
    report.recommendations.push("Create separate tracks: Dialogue, Music, Effects, Ambience");
  }
  
  report.recommendations.push("Verify sample rate 48 kHz in Project Settings");
  report.recommendations.push("Use loudness meter (Essential Sound panel) to verify LUFS");
  report.recommendations.push("Target loudness depends on delivery platform");
  
  $.writeln("=== AUDIO CONFIGURATION ===");
  $.writeln("Audio tracks: " + report.trackCount);
  $.writeln("Sample rate: " + report.sampleRate);
  $.writeln("Bit depth: " + report.bitDepth);
  $.writeln("\nRecommendations:");
  for (var j = 0; j < report.recommendations.length; j++) {
    $.writeln("- " + report.recommendations[j]);
  }
  
  return report;
}

// Usage
verifyAudioSettings(app.project.activeSequence);
```

### Loudness Reference Chart

```javascript
function loudnessGuide() {
  /**
   * Quick reference for LUFS targets and headroom
   */
  
  var guide = {
    broadcast: {
      target: -23,
      headroom: 1,
      peak: -20
    },
    cinema: {
      target: -24,
      headroom: 2,
      peak: -18
    },
    streaming: {
      target: -14,
      headroom: 1,
      peak: -3
    }
  };
  
  $.writeln("=== LOUDNESS TARGETS (LUFS) ===\n");
  
  $.writeln("BROADCAST (EBU R128):");
  $.writeln("  Target: " + guide.broadcast.target + " LUFS");
  $.writeln("  Headroom: " + guide.broadcast.headroom + " dB");
  $.writeln("  Peak: " + guide.broadcast.peak + " dBFS");
  
  $.writeln("\nCINEMA (Dolby):");
  $.writeln("  Target: " + guide.cinema.target + " LUFS");
  $.writeln("  Headroom: " + guide.cinema.headroom + " dB");
  $.writeln("  Peak: " + guide.cinema.peak + " dBFS");
  
  $.writeln("\nSTREAMING (Spotify/Apple):");
  $.writeln("  Target: " + guide.streaming.target + " LUFS");
  $.writeln("  Headroom: " + guide.streaming.headroom + " dB");
  $.writeln("  Peak: " + guide.streaming.peak + " dBFS");
  
  $.writeln("\nMEASUREMENT:");
  $.writeln("  Gate: -70 LUFS (ISO 1770-4)");
  $.writeln("  Window: 3-second integrated or 5-minute program");
  $.writeln("  True Peak: Not to exceed -3 dBFS");
  
  return guide;
}

// Usage
loudnessGuide();
```

---

## Surround Sound: 5.1 & 7.1 Configuration

### Setup 5.1 Surround Mix

```javascript
function create51SurroundTracks(sequence) {
  /**
   * Create standard 5.1 surround sound track configuration
   * Channels: L, R, C, LFE (subwoofer), Ls (left surround), Rs (right surround)
   */
  
  var trackConfig = {
    trackNames: [
      "Dialogue",
      "Music",
      "Effects",
      "Ambience",
      "LFE (Subwoofer)"
    ],
    channelLayout: "5.1",
    recommendations: []
  };
  
  $.writeln("=== 5.1 SURROUND CONFIGURATION ===\n");
  
  $.writeln("Track Layout:");
  $.writeln("1. Dialogue (Mono or Stereo L/R)");
  $.writeln("2. Music (Stereo L/R)");
  $.writeln("3. Effects (Stereo L/R with surround positioning)");
  $.writeln("4. Ambience (Surround L/R, R/S channels)");
  $.writeln("5. LFE Track (Low-frequency effects, 0.1 channel)");
  
  $.writeln("\nChannel Assignments:");
  $.writeln("L  = Front Left");
  $.writeln("R  = Front Right");
  $.writeln("C  = Center (Dialogue primary)");
  $.writeln("LFE = Subwoofer (20-120 Hz content)");
  $.writeln("Ls = Left Surround");
  $.writeln("Rs = Right Surround");
  
  trackConfig.recommendations.push("Send dialogue to Center channel");
  trackConfig.recommendations.push("Separate LFE content (subwoofer-only material)");
  trackConfig.recommendations.push("Use surround channels for ambient/background");
  trackConfig.recommendations.push("Peak at -20 dBFS per channel");
  
  $.writeln("\nMix Recommendations:");
  for (var i = 0; i < trackConfig.recommendations.length; i++) {
    $.writeln("- " + trackConfig.recommendations[i]);
  }
  
  return trackConfig;
}

function create71SurroundTracks(sequence) {
  /**
   * Create 7.1 surround configuration (cinema standard)
   * Adds side surrounds for wider spatial field
   */
  
  $.writeln("=== 7.1 SURROUND CONFIGURATION ===\n");
  
  $.writeln("Channels:");
  $.writeln("L   = Front Left");
  $.writeln("R   = Front Right");
  $.writeln("C   = Center");
  $.writeln("LFE = Subwoofer");
  $.writeln("Ls  = Left Surround (side)");
  $.writeln("Rs  = Right Surround (side)");
  $.writeln("Lss = Left Side Surround (rear side, 7.1 only)");
  $.writeln("Rss = Right Side Surround (rear side, 7.1 only)");
  
  $.writeln("\n7.1 Usage: Cinema, immersive streaming, premium platforms");
  
  return { channelLayout: "7.1", trackCount: 8 };
}

// Usage
create51SurroundTracks(app.project.activeSequence);
// create71SurroundTracks(app.project.activeSequence);
```

---

## Dolby Atmos: Object-Based Audio

### Atmos Configuration Basics

```javascript
function atmosPreparation(sequence) {
  /**
   * Prepare mix for Dolby Atmos delivery
   * Object-based audio: treat sound as objects with position/metadata
   * 
   * Requires: Dolby Atmos for Premiere plugin
   * Delivery: Master file with metadata (ADM file format)
   */
  
  var atmosConfig = {
    format: "Dolby Atmos",
    trackLayout: "7.1.4",  // 7.1 base + 4 overhead channels
    loudness: -24,  // LUFS target for cinema
    deliverables: []
  };
  
  $.writeln("=== DOLBY ATMOS PREPARATION ===\n");
  
  $.writeln("Format: 7.1.4 (object-based immersive audio)");
  $.writeln("Channels:");
  $.writeln("  - 7.1 Speaker layer (surround)");
  $.writeln("  - 4 Height channels (overhead/ceiling)");
  $.writeln("  - Object tracks (moveable sound objects)");
  
  $.writeln("\nAtmos Metadata:");
  $.writeln("- Speak position (X, Y, Z coordinates)");
  $.writeln("- Size (point source vs diffuse)");
  $.writeln("- Distance (near vs far field)");
  $.writeln("- Divergence (spread pattern)");
  
  atmosConfig.deliverables = [
    { format: "Atmos Master (ADM BWF)", use: "Premium cinema/streaming" },
    { format: "Dolby Digital Plus (E-AC-3)", use: "Broadcast fallback" },
    { format: "Stereo M&E", use: "Standard broadcast" }
  ];
  
  $.writeln("\nDeliverables required:");
  for (var i = 0; i < atmosConfig.deliverables.length; i++) {
    var d = atmosConfig.deliverables[i];
    $.writeln("- " + d.format + " (" + d.use + ")");
  }
  
  $.writeln("\nNote: Dolby Atmos plugin required for object authoring");
  $.writeln("Recommend: Professional mix engineer with Atmos certification");
  
  return atmosConfig;
}

// Usage
atmosPreparation(app.project.activeSequence);
```

---

## Audio Workflow: Mixing & Mastering

### Mixing Best Practices

```javascript
function audioMixingWorkflow(sequence) {
  /**
   * Standard audio mixing workflow: organize → mix → master → verify
   */
  
  var workflow = {
    stages: [],
    timeline: []
  };
  
  var stages = [
    {
      stage: 1,
      name: "Organization",
      tasks: [
        "Separate dialogue/music/effects/ambience",
        "Color-code tracks for visual organization",
        "Verify all clips synced to timecode"
      ]
    },
    {
      stage: 2,
      name: "Preliminary Mix",
      tasks: [
        "Set relative levels (dialogue = -18 dB reference)",
        "Pan positioning (dialogue center, effects stereo)",
        "Add EQ and compression per track",
        "Create fades and transitions"
      ]
    },
    {
      stage: 3,
      name: "Final Mix",
      tasks: [
        "Balance across full duration",
        "Check headroom (peak -3 dBFS)",
        "Verify surround panning",
        "Automation for dynamic content"
      ]
    },
    {
      stage: 4,
      name: "Mastering",
      tasks: [
        "Apply master bus compression/EQ",
        "Verify loudness (target LUFS)",
        "Check stereo imaging",
        "A/B reference against professional mixes"
      ]
    },
    {
      stage: 5,
      name: "Verification",
      tasks: [
        "Loudness metering (integrated LUFS)",
        "True peak analysis (-3 dBFS max)",
        "Mono compatibility check",
        "Export multiple formats (stereo, 5.1, Atmos)"
      ]
    }
  ];
  
  $.writeln("=== AUDIO MIXING WORKFLOW ===\n");
  
  for (var i = 0; i < stages.length; i++) {
    var s = stages[i];
    $.writeln(s.stage + ". " + s.name);
    for (var j = 0; j < s.tasks.length; j++) {
      $.writeln("   - " + s.tasks[j]);
    }
    $.writeln("");
  }
  
  $.writeln("TIMELINE:");
  $.writeln("Dialogue mix: 2-3 days");
  $.writeln("Effects/music layer: 2-3 days");
  $.writeln("Final mix: 1-2 days");
  $.writeln("Mastering: 1 day");
  $.writeln("Total: 6-9 days for professional broadcast");
  
  return stages;
}

// Usage
audioMixingWorkflow(app.project.activeSequence);
```

---

## Audio Export & Delivery

### Export Loudness-Normalized Audio

```javascript
function exportAudioWithLoudnessNorm(sequence, outputPath, platform) {
  /**
   * Export audio meeting loudness specifications
   * platform: "broadcast" (-23 LUFS), "streaming" (-14 LUFS), "cinema" (-24 LUFS)
   */
  
  var loudnessTargets = {
    broadcast: -23,
    streaming: -14,
    cinema: -24
  };
  
  var target = loudnessTargets[platform] || -24;
  
  $.writeln("=== AUDIO EXPORT ===");
  $.writeln("Platform: " + platform);
  $.writeln("Target: " + target + " LUFS");
  $.writeln("Output: " + outputPath);
  
  $.writeln("\nExport checklist:");
  $.writeln("☐ Verify loudness is " + target + " LUFS ±0.5 LU");
  $.writeln("☐ Check true peak does not exceed -3 dBFS");
  $.writeln("☐ Verify all tracks are enabled");
  $.writeln("☐ Confirm no clipping on master bus");
  $.writeln("☐ Test stereo imaging (mono compatibility)");
  
  $.writeln("\nNote: Use Adobe Audition or external tool for loudness normalization");
  $.writeln("Premiere's export does not auto-normalize to LUFS");
  
  return {
    platform: platform,
    targetLUFS: target,
    note: "Manual loudness normalization required post-export"
  };
}

// Usage
exportAudioWithLoudnessNorm(app.project.activeSequence, "/tmp/audio.wav", "broadcast");
```

---

## Audio Verification Checklist

- ☐ Project sample rate: 48 kHz
- ☐ Bit depth: 24-bit minimum
- ☐ Loudness: Target LUFS met (broadcast: -23, cinema: -24, streaming: -14)
- ☐ Headroom: -3 dB minimum on master bus
- ☐ Peak levels: No clipping
- ☐ Mono compatibility: Verified (no phase issues)
- ☐ Surround panning: Objects properly positioned
- ☐ Dialogue intelligibility: Center channel clear
- ☐ Music/effects balance: Not masking dialogue
- ☐ Dynamic range: Preserved (not over-compressed)
- ☐ Audio sync: All clips properly aligned to timecode
- ☐ Format exports: All platforms generated (stereo, 5.1, Atmos if required)

---

## See Also

- Knowledge/audio-api.md — Audio API reference
- Knowledge/codec-media-reference.md — Audio codec specifications
- Knowledge/export-rendering-media-encoder.md — Export loudness settings
- Knowledge/real-world-production-workflows.md — Broadcasting specs

---

## Sources

- EBU R128 Standard: https://tech.ebu.ch/loudness
- ATSC A/85 Loudness: FCC guidelines
- Dolby Atmos: https://www.dolby.com/atmos/
- ITU-R BS.1770-4: https://www.itu.int/rec/R-REC-BS.1770-4/en
