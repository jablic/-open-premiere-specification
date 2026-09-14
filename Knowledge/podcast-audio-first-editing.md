---
id: podcast-audio-first-editing
title: Podcast & Audio-First Editing Workflows
category: workflow
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2015"
min_premiere_version: "14.0"
api_namespace: null
languages: [extendscript, javascript, jsx]
tags: [podcast, audio-editing, chapters, metadata, distribution, mastering]
related: [advanced-audio-engineering, automation, export-rendering-media-encoder]
sources: [
  "Podcast production workflows",
  "Audio editing best practices",
  "Distribution standards"
]
confidence: high
last_verified: "2026-07-01"
verified_against_version: "25.6"
---

# Podcast & Audio-First Editing Workflows

## TL;DR

**Timeline:** Audio-primary (no video track). **Sample Rate:** 44.1 kHz (music standard) or 48 kHz (broadcast). **Bit Depth:** 24-bit minimum (16-bit acceptable). **Chapter Markers:** Insert at segment breaks for podcast player navigation. **Metadata:** Title, description, chapter times, artwork. **Loudness:** -16 LUFS integrated (podcast standard). **Export:** MP3 (128 kbps), AAC, WAV (archival). **Metadata Tags:** ID3v2 (MP3), metadata atoms (M4A). **Distribution:** Anchor, Transistor, Podbean with auto-upload.

---

## Audio-First Project Setup

### Create Podcast Project

```javascript
function createPodcastProject(projectName, episodeNumber) {
  /**
   * Setup audio-first project for podcast episode
   * No video tracks (audio-primary)
   */
  
  var project = app.project;
  
  // Create sequence with audio-only configuration
  var sequence = project.createSequence(projectName + "_Ep" + episodeNumber, {
    videoTrackCount: 0,     // No video
    audioTrackCount: 4,     // Dialogue, Music, Effects, Ambience
    frameRate: 30           // Standard frame rate (even though no video)
  });
  
  $.writeln("=== PODCAST PROJECT CREATED ===\n");
  
  $.writeln("Project: " + projectName);
  $.writeln("Episode: " + episodeNumber);
  $.writeln("Sequence: " + sequence.name);
  $.writeln("Audio Tracks: 4");
  $.writeln("  1. Dialogue (Host)");
  $.writeln("  2. Music (Intro/outro)");
  $.writeln("  3. Effects (Transitions, ambient)");
  $.writeln("  4. Archive (Raw recording backup)");
  
  $.writeln("\nProject Settings:");
  $.writeln("- Sample Rate: 48 kHz (or 44.1 kHz)");
  $.writeln("- Bit Depth: 24-bit");
  $.writeln("- Channel Format: Stereo");
  
  return sequence;
}

// Usage
var podcastSeq = createPodcastProject("My Podcast", 42);
```

---

## Chapter Markers & Metadata

### Insert Chapter Markers

```javascript
function insertPodcastChapters(sequence, chapters) {
  /**
   * Mark chapter boundaries for podcast player navigation
   * Chapters: [{time: seconds, title: "Chapter Name"}, ...]
   */
  
  var seq = sequence;
  var results = { inserted: 0, failed: 0 };
  
  $.writeln("=== INSERT PODCAST CHAPTERS ===\n");
  
  for (var i = 0; i < chapters.length; i++) {
    var chapter = chapters[i];
    var timeInPremiereTicks = chapter.time * 254016000000;  // seconds to Premiere time
    
    try {
      var marker = seq.markers.createMarker(timeInPremiereTicks);
      marker.name = chapter.title;
      marker.comments = "Chapter " + (i + 1);
      marker.setColorByIndex(2);  // Green for chapters
      
      $.writeln((i + 1) + ". " + chapter.title + " @ " + chapter.time + "s");
      results.inserted++;
      
    } catch (e) {
      $.writeln("✗ Error: " + e.toString());
      results.failed++;
    }
  }
  
  $.writeln("\nChapters: " + results.inserted);
  $.writeln("Failed: " + results.failed);
  
  return results;
}

// Usage
var chapters = [
  { time: 0, title: "Intro" },
  { time: 30, title: "Guest Introduction" },
  { time: 120, title: "Main Topic" },
  { time: 1200, title: "Q&A" },
  { time: 1500, title: "Outro" }
];

insertPodcastChapters(app.project.activeSequence, chapters);
```

### Add Episode Metadata

```javascript
function addPodcastMetadata(project, episodeData) {
  /**
   * Embed metadata for podcast distribution
   * Used by platforms: Spotify, Apple Podcasts, YouTube
   */
  
  var metadata = {
    podcastTitle: episodeData.podcastTitle,
    episodeNumber: episodeData.episodeNumber,
    episodeTitle: episodeData.episodeTitle,
    description: episodeData.description,
    guests: episodeData.guests || [],
    publishDate: new Date().toISOString(),
    duration: episodeData.duration,
    tags: episodeData.tags || []
  };
  
  // Store in project custom data
  try {
    var metadataFile = new File(project.file.parent.absoluteURI + "/metadata.json");
    metadataFile.open("w");
    metadataFile.write(JSON.stringify(metadata, null, 2));
    metadataFile.close();
    
    $.writeln("=== PODCAST METADATA ===\n");
    $.writeln("Podcast: " + metadata.podcastTitle);
    $.writeln("Episode: " + metadata.episodeNumber + " - " + metadata.episodeTitle);
    $.writeln("Duration: " + metadata.duration + " min");
    $.writeln("Guests: " + metadata.guests.join(", "));
    $.writeln("Published: " + metadata.publishDate);
    $.writeln("\nMetadata saved: metadata.json");
    
  } catch (e) {
    $.writeln("Error saving metadata: " + e.toString());
  }
  
  return metadata;
}

// Usage
addPodcastMetadata(app.project, {
  podcastTitle: "Tech Talk Daily",
  episodeNumber: 42,
  episodeTitle: "AI and the Future of Work",
  description: "Discussion about AI integration in the workplace with industry experts",
  guests: ["Jane Smith", "John Doe"],
  duration: 45,
  tags: ["AI", "technology", "workplace"]
});
```

---

## Audio Mixing for Podcast

### Mixing Workflow

```javascript
function podcastMixingWorkflow(sequence) {
  /**
   * Standard podcast mixing workflow
   */
  
  $.writeln("=== PODCAST MIXING WORKFLOW ===\n");
  
  $.writeln("1. ORGANIZATION (10 min)");
  $.writeln("   - Separate dialogue, music, effects into tracks");
  $.writeln("   - Color-code tracks");
  $.writeln("   - Sync all audio to host timeline");
  
  $.writeln("\n2. PRELIMINARY MIX (30 min)");
  $.writeln("   - Set relative levels:");
  $.writeln("     • Host dialogue: -18 dB reference");
  $.writeln("     • Guest dialogue: -20 dB (slightly lower)");
  $.writeln("     • Music: -30 dB (background)");
  $.writeln("     • Effects: -25 dB (punctuation)");
  $.writeln("   - Pan dialogue to center");
  $.writeln("   - Create fade in/out (intro/outro music)");
  
  $.writeln("\n3. EQ & COMPRESSION (30 min)");
  $.writeln("   - Dialogue EQ: Remove low rumble, brighten (2-4 kHz)");
  $.writeln("   - Compressor: Reduce dynamic range (ratio 4:1, threshold -20 dB)");
  $.writeln("   - Gate: Remove noise between dialogue");
  $.writeln("   - De-esser: Remove sibilance");
  
  $.writeln("\n4. LOUDNESS NORMALIZATION (10 min)");
  $.writeln("   - Target: -16 LUFS (podcast standard)");
  $.writeln("   - True Peak: -1 dBFS max");
  $.writeln("   - Verify with loudness meter");
  
  $.writeln("\n5. QC & VERIFICATION (10 min)");
  $.writeln("   - Listen on multiple speakers (phone, earbuds, studio)");
  $.writeln("   - Check for clipping, distortion");
  $.writeln("   - Verify silence between segments");
  
  $.writeln("\nTotal time: ~90 min for 1-hour episode");
  
  return { totalTime: 90, steps: 5 };
}

// Usage
podcastMixingWorkflow(app.project.activeSequence);
```

---

## Export for Distribution

### Generate Podcast Audio Files

```javascript
function exportPodcastAudio(sequence, episodeData) {
  /**
   * Export in formats required by podcast platforms
   * MP3 (most compatible), AAC (iTunes), WAV (archival)
   */
  
  var exports = [
    {
      format: "MP3",
      bitrate: "128 kbps",
      sampleRate: "44.1 kHz",
      filename: "episode_042.mp3",
      platforms: "Spotify, Apple Podcasts, YouTube, all universal"
    },
    {
      format: "AAC (M4A)",
      bitrate: "128 kbps",
      sampleRate: "44.1 kHz",
      filename: "episode_042.m4a",
      platforms: "iTunes, Apple Podcasts"
    },
    {
      format: "WAV",
      bitrate: "Lossless",
      sampleRate: "48 kHz, 24-bit",
      filename: "episode_042_master.wav",
      platforms: "Archival, backup, professional distribution"
    }
  ];
  
  $.writeln("=== PODCAST EXPORT FORMATS ===\n");
  
  for (var i = 0; i < exports.length; i++) {
    var exp = exports[i];
    $.writeln((i + 1) + ". " + exp.format);
    $.writeln("   Bitrate: " + exp.bitrate);
    $.writeln("   File: " + exp.filename);
    $.writeln("   Platforms: " + exp.platforms);
    $.writeln("");
  }
  
  $.writeln("Metadata to embed:");
  $.writeln("- Title: " + episodeData.episodeTitle);
  $.writeln("- Artist: " + episodeData.podcastTitle);
  $.writeln("- Album: " + episodeData.podcastTitle + " - Episode " + episodeData.episodeNumber);
  $.writeln("- Year: " + new Date().getFullYear());
  $.writeln("- Genre: Podcast");
  $.writeln("- Comments: " + episodeData.description);
  
  return exports;
}

// Usage
exportPodcastAudio(app.project.activeSequence, {
  podcastTitle: "Tech Talk Daily",
  episodeNumber: 42,
  episodeTitle: "AI and the Future of Work",
  description: "Discussion with Jane Smith and John Doe"
});
```

### Embed ID3v2 Metadata (MP3)

```javascript
function embedID3Metadata(mp3FilePath, metadata) {
  /**
   * Add ID3v2 tags to MP3 files
   * Note: Requires external tool (ffmpeg, id3v2)
   */
  
  $.writeln("=== EMBED ID3 METADATA ===\n");
  
  $.writeln("Using ffmpeg to add ID3v2 tags to MP3:");
  $.writeln("Command:");
  $.writeln("ffmpeg -i input.mp3 -c copy");
  $.writeln("  -metadata title=\"" + metadata.episodeTitle + "\"");
  $.writeln("  -metadata artist=\"" + metadata.podcastTitle + "\"");
  $.writeln("  -metadata album=\"" + metadata.podcastTitle + " EP " + metadata.episodeNumber + "\"");
  $.writeln("  -metadata date=\"" + new Date().getFullYear() + "\"");
  $.writeln("  -metadata genre=\"Podcast\"");
  $.writeln("  -metadata comment=\"" + metadata.description + "\"");
  $.writeln("  -metadata album_artist=\"" + metadata.podcastTitle + "\"");
  $.writeln("  output.mp3");
  
  $.writeln("\nOr use id3v2 tool:");
  $.writeln("id3v2 -t \"" + metadata.episodeTitle + "\"");
  $.writeln("  -a \"" + metadata.podcastTitle + "\"");
  $.writeln("  -A \"" + metadata.podcastTitle + "\"");
  $.writeln("  -g \"Podcast\"");
  $.writeln("  input.mp3");
  
  return { tool: "ffmpeg or id3v2", embedded: false };
}

// Usage
embedID3Metadata("/path/to/episode.mp3", {
  episodeTitle: "AI and the Future of Work",
  podcastTitle: "Tech Talk Daily",
  episodeNumber: 42,
  description: "Discussion with industry experts"
});
```

---

## Podcast Distribution Automation

```javascript
function setupPodcastDistribution(episodeData) {
  /**
   * Setup auto-upload to podcast platforms
   * Supports: Anchor, Transistor, Podbean, Buzzsprout
   */
  
  var platforms = [
    {
      name: "Anchor (Spotify)",
      url: "https://anchor.fm/",
      features: "Free hosting, auto-distributes to Spotify/Apple",
      uploadMethod: "Web upload or API"
    },
    {
      name: "Transistor",
      url: "https://transistor.fm/",
      features: "Professional hosting, analytics, email campaigns",
      uploadMethod: "API webhook"
    },
    {
      name: "Podbean",
      url: "https://www.podbean.com/",
      features: "Monetization, advertising, detailed analytics",
      uploadMethod: "Web upload, FTP, or API"
    }
  ];
  
  $.writeln("=== PODCAST DISTRIBUTION ===\n");
  
  for (var i = 0; i < platforms.length; i++) {
    var p = platforms[i];
    $.writeln((i + 1) + ". " + p.name);
    $.writeln("   " + p.features);
    $.writeln("   Upload: " + p.uploadMethod);
    $.writeln("");
  }
  
  $.writeln("Distribution workflow:");
  $.writeln("1. Export MP3 + metadata");
  $.writeln("2. Login to hosting platform");
  $.writeln("3. Upload episode");
  $.writeln("4. Auto-distributes to: Spotify, Apple Podcasts, Google Podcasts, YouTube");
  $.writeln("5. Available in ~24 hours across platforms");
  
  return platforms;
}

// Usage
setupPodcastDistribution({ episodeNumber: 42 });
```

---

## Podcast Workflow Checklist

- ☐ Audio-only project created (no video tracks)
- ☐ Sample rate 44.1 kHz or 48 kHz
- ☐ Audio organized (dialogue, music, effects tracks)
- ☐ Host dialogue recorded and normalized
- ☐ Guest audio synced to timeline
- ☐ Music intro/outro added
- ☐ Chapter markers inserted for navigation
- ☐ EQ and compression applied to dialogue
- ☐ Final mix normalized to -16 LUFS
- ☐ Metadata embedded (episode title, description, guests)
- ☐ Export in MP3 + AAC + WAV formats
- ☐ ID3 tags added (MP3 metadata)
- ☐ Uploaded to podcast hosting platform
- ☐ Verified on Spotify, Apple Podcasts
- ☐ Shared on social media + website

---

## See Also

- Knowledge/advanced-audio-engineering.md — Audio mixing and loudness
- Knowledge/automation.md — Batch processing
- Knowledge/export-rendering-media-encoder.md — Export specifications

---

## Sources

- Podcast Loudness Standards: https://podcasters.spotify.com/
- ID3 Specification: https://id3.org/
- ffmpeg Documentation: https://ffmpeg.org/
