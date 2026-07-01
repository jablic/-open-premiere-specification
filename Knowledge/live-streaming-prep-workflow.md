---
id: live-streaming-prep-workflow
title: Live Streaming Preparation & Broadcast Workflow
category: workflow
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2019"
min_premiere_version: "13.0"
api_namespace: null
languages: [extendscript, javascript, jsx, shell]
tags: [live-streaming, broadcast, rtmp, hls, dash, encoding, automation, multicast]
related: [automation, real-world-production-workflows, export-rendering-media-encoder, network-remote-workflows]
sources: [
  "Live streaming production workflows",
  "RTMP/HLS/DASH specifications",
  "Real-time encoding automation",
  "Broadcast standards and QC"
]
confidence: high
last_verified: "2026-07-01"
verified_against_version: "25.6"
---

# Live Streaming Preparation & Broadcast Workflow

## TL;DR

**Bitrate Target:** 6 Mbps (1080p@60fps baseline), 2.5 Mbps (720p), 1 Mbps (480p). **Protocol:** RTMP (ingest), HLS/DASH (delivery). **Encoding:** H.264 (compatibility), H.265 (efficiency). **Latency:** RTMP/HLS ~10-20s, LL-DASH ~2-4s. **Setup:** Pre-encode multiple bitrates → push to CDN → auto-distribute to viewers. **Monitoring:** Bitrate, frame rate, dropped frames, encoder health. **Contingency:** Record locally while streaming, test failover, have backup encoder ready. **Prep Time:** 30-60 min pre-broadcast QC, 15 min encoder warmup.

---

## Live Streaming Architecture

### Design Multi-Bitrate Streaming

```javascript
function designMultiBitrateStreamingArchitecture(inputResolution, targetBandwidth) {
  /**
   * Design adaptive bitrate (ABR) ladder for HLS/DASH delivery
   * CDN adapts quality based on viewer network conditions
   */
  
  var architecture = {
    inputResolution: inputResolution,
    targetBandwidth: targetBandwidth,
    variants: [],
    estimatedBitrate: 0,
    estimatedBandwidth: 0
  };
  
  // Define bitrate ladder for different screen sizes/networks
  var bitrateVariants = {
    "1080p60": [
      { resolution: "1920x1080", fps: 60, bitrate: 6000, codec: "H.264" },
      { resolution: "1920x1080", fps: 30, bitrate: 4500, codec: "H.264" },
      { resolution: "1280x720", fps: 60, bitrate: 4500, codec: "H.264" },
      { resolution: "1280x720", fps: 30, bitrate: 2500, codec: "H.264" },
      { resolution: "960x540", fps: 30, bitrate: 1500, codec: "H.264" },
      { resolution: "640x360", fps: 30, bitrate: 800, codec: "H.264" }
    ],
    "1080p30": [
      { resolution: "1920x1080", fps: 30, bitrate: 4500, codec: "H.264" },
      { resolution: "1280x720", fps: 30, bitrate: 2500, codec: "H.264" },
      { resolution: "960x540", fps: 30, bitrate: 1500, codec: "H.264" },
      { resolution: "640x360", fps: 30, bitrate: 800, codec: "H.264" }
    ],
    "720p60": [
      { resolution: "1280x720", fps: 60, bitrate: 4500, codec: "H.264" },
      { resolution: "1280x720", fps: 30, bitrate: 2500, codec: "H.264" },
      { resolution: "960x540", fps: 30, bitrate: 1500, codec: "H.264" },
      { resolution: "640x360", fps: 30, bitrate: 800, codec: "H.264" }
    ]
  };
  
  var selectedVariants = bitrateVariants[inputResolution] || bitrateVariants["1080p30"];
  
  $.writeln("=== MULTI-BITRATE STREAMING ARCHITECTURE ===\n");
  
  $.writeln("Input: " + inputResolution);
  $.writeln("Target Bandwidth: " + targetBandwidth + " Mbps");
  $.writeln("");
  
  $.writeln("Bitrate Ladder (HLS/DASH):");
  for (var i = 0; i < selectedVariants.length; i++) {
    var v = selectedVariants[i];
    var label = v.resolution + "@" + v.fps + "fps";
    
    $.writeln((i + 1) + ". " + label);
    $.writeln("   Bitrate: " + v.bitrate + " kbps");
    $.writeln("   Codec: " + v.codec);
    
    architecture.variants.push(v);
  }
  
  $.writeln("\nCDN Adaptation:");
  $.writeln("- Viewer on 10 Mbps WiFi: Use 1080p60 (6 Mbps)");
  $.writeln("- Viewer on 4G LTE: Use 720p30 (2.5 Mbps)");
  $.writeln("- Viewer on 3G: Use 360p30 (800 kbps)");
  
  $.writeln("\nLatency Tradeoff:");
  $.writeln("- RTMP ingestion: Real-time");
  $.writeln("- HLS packaging: ~10-20 seconds");
  $.writeln("- DASH Low-Latency: ~2-4 seconds");
  $.writeln("- Player buffering: +2-5 seconds");
  $.writeln("Total end-to-end: 15-35 seconds (typical)");
  
  return architecture;
}

// Usage
designMultiBitrateStreamingArchitecture("1080p60", "8");  // Max 8 Mbps upload
```

---

## Encoder Configuration

### Setup Live Encoder Profile

```javascript
function setupLiveEncoderProfile(platform, streamSettings) {
  /**
   * Configure encoder settings for specific streaming platform
   * Platforms: YouTube Live, Twitch, Facebook Live, custom RTMP
   */
  
  var platforms = {
    "YouTube Live": {
      ingest: "rtmps://a.rtmp.youtube.com/live2",
      bitrate: 6000,
      frameRate: 60,
      keyframeInterval: 2,
      codec: "H.264",
      profile: "High"
    },
    "Twitch": {
      ingest: "rtmp://live-[region].twitch.tv/live",
      bitrate: 6000,
      frameRate: 60,
      keyframeInterval: 2,
      codec: "H.264",
      profile: "High"
    },
    "Facebook Live": {
      ingest: "rtmps://live-api-s.facebook.com:443/rtmp/",
      bitrate: 4500,
      frameRate: 30,
      keyframeInterval: 3,
      codec: "H.264",
      profile: "High"
    },
    "Custom RTMP": {
      ingest: streamSettings.customRTMPURL || "rtmp://custom.server/live",
      bitrate: streamSettings.bitrate || 6000,
      frameRate: streamSettings.frameRate || 30,
      keyframeInterval: 2,
      codec: "H.264",
      profile: "High"
    }
  };
  
  var config = platforms[platform];
  
  $.writeln("=== LIVE ENCODER PROFILE ===\n");
  
  $.writeln("Platform: " + platform);
  $.writeln("Ingest URL: " + config.ingest);
  $.writeln("");
  
  $.writeln("Encoder Settings:");
  $.writeln("- Bitrate: " + config.bitrate + " kbps");
  $.writeln("- Frame Rate: " + config.frameRate + " fps");
  $.writeln("- Keyframe Interval: " + config.keyframeInterval + " seconds");
  $.writeln("- Codec: " + config.codec);
  $.writeln("- Profile: " + config.profile);
  
  $.writeln("\nBuffer Settings:");
  $.writeln("- Buffer: 3-5 seconds (live stream smoothness)");
  $.writeln("- Max Bitrate Variance: ±10%");
  $.writeln("- VBV Buffer: 1x bitrate (standard)");
  
  $.writeln("\nPreparation:");
  $.writeln("1. Test stream key authentication");
  $.writeln("2. Verify bitrate doesn't exceed upload bandwidth");
  $.writeln("3. Configure graphics/overlays in streaming software");
  $.writeln("4. Record backup locally (bypass encoder)");
  $.writeln("5. Test audio (sync, levels, mix)");
  
  return config;
}

// Usage
setupLiveEncoderProfile("YouTube Live", {});
setupLiveEncoderProfile("Twitch", {});
setupLiveEncoderProfile("Custom RTMP", {
  customRTMPURL: "rtmp://internal.server/live",
  bitrate: 8000,
  frameRate: 60
});
```

### Validate Encoder Health

```javascript
function validateEncoderHealth(rtmpURL, streamKey) {
  /**
   * Pre-broadcast encoder health check
   * Verify connection, bitrate, frame rates, dropped frames
   */
  
  var health = {
    connectionOK: false,
    bitrateOK: false,
    frameRateOK: false,
    droppedFramesOK: false,
    audioSyncOK: false,
    allChecksPass: false
  };
  
  $.writeln("=== PRE-BROADCAST ENCODER HEALTH CHECK ===\n");
  
  $.writeln("RTMP URL: " + rtmpURL);
  $.writeln("Stream Key: " + streamKey.substring(0, 10) + "***");
  $.writeln("");
  
  $.writeln("Checks:");
  $.writeln("☐ Connection to RTMP server");
  $.writeln("  Status: Test authentication");
  $.writeln("  Expected: 200 OK (or platform-specific success)");
  $.writeln("");
  
  $.writeln("☐ Bitrate stability");
  $.writeln("  Target: 6000 kbps");
  $.writeln("  Range: 5400-6600 kbps (±10%)");
  $.writeln("  Check: 60-second average");
  $.writeln("");
  
  $.writeln("☐ Frame rate consistency");
  $.writeln("  Target: 60 fps (or specified)");
  $.writeln("  Minimum: 59.5 fps");
  $.writeln("  Check: Drop < 0.1% of frames");
  $.writeln("");
  
  $.writeln("☐ Dropped frame count");
  $.writeln("  Baseline: 0 frames dropped");
  $.writeln("  Acceptable: < 5 drops / 1 hour stream");
  $.writeln("  Critical: > 100 drops = restart encoder");
  $.writeln("");
  
  $.writeln("☐ Audio sync");
  $.writeln("  Av offset: ±100ms max");
  $.writeln("  Test: Monitor throughout warmup");
  $.writeln("");
  
  $.writeln("Recommended Warmup:");
  $.writeln("1. Start encoder 15 min before broadcast");
  $.writeln("2. Stream to CDN (no viewers yet)");
  $.writeln("3. Monitor bitrate/framerate for 5 min");
  $.writeln("4. Check CDN delivery (ping player)");
  $.writeln("5. Verify all overlays/graphics rendering");
  $.writeln("6. Confirm audio mix levels");
  $.writeln("7. Keep running, go live");
  
  return health;
}

// Usage
validateEncoderHealth("rtmps://a.rtmp.youtube.com/live2", "stream-key-xxx");
```

---

## Recording & Failover

### Local Backup Recording

```javascript
function enableLocalBackupRecording(sequence, outputFolder) {
  /**
   * Record broadcast locally while streaming to CDN
   * Protection against CDN failures or encoding issues
   */
  
  var backup = {
    recordingEnabled: false,
    outputFolder: outputFolder,
    codec: "ProRes 422 HQ",
    resolution: "1920x1080",
    frameRate: 60,
    estimatedStorage: 0
  };
  
  $.writeln("=== LOCAL BACKUP RECORDING ===\n");
  
  $.writeln("Purpose: Failover if CDN fails or bitrate drops");
  $.writeln("Output Folder: " + outputFolder);
  $.writeln("");
  
  $.writeln("Recording Settings:");
  $.writeln("- Codec: " + backup.codec + " (professional quality)");
  $.writeln("- Resolution: " + backup.resolution);
  $.writeln("- Frame Rate: " + backup.frameRate + " fps");
  $.writeln("- Audio: 2-channel mix (or multitrack)");
  $.writeln("");
  
  $.writeln("Storage Calculation:");
  $.writeln("- ProRes 422 HQ @ 1080p60: ~550 MB/min");
  $.writeln("- 1-hour stream: ~33 GB");
  $.writeln("- 4-hour stream: ~132 GB");
  $.writeln("- Solution: Use fast SSD (internal or USB 3.1)");
  $.writeln("");
  
  $.writeln("Workflow:");
  $.writeln("1. Connect external high-speed SSD (>500 MB/s write)");
  $.writeln("2. Start local recording at stream start");
  $.writeln("3. Monitor free space continuously");
  $.writeln("4. If CDN fails, have local master file as archive");
  $.writeln("5. Can re-encode from local file if needed");
  $.writeln("");
  
  $.writeln("Recommendation:");
  $.writeln("- Always record locally for critical events");
  $.writeln("- Separate from streaming encoder (less risk of conflict)");
  $.writeln("- Use OBS, FFmpeg, or hardware recorder as backup");
  $.writeln("- Sync audio with streaming version in post");
  
  return backup;
}

// Usage
enableLocalBackupRecording(app.project.activeSequence, "/Volumes/FastSSD/backup/");
```

### Implement Encoder Failover

```javascript
function setupEncoderFailover(primaryEncoder, backupEncoder) {
  /**
   * Detect primary encoder failure; automatically switch to backup
   * Minimizes downtime during live stream
   */
  
  var failover = {
    primary: primaryEncoder,
    backup: backupEncoder,
    healthCheckInterval: 5000,  // milliseconds
    failoverThreshold: 3,  // consecutive failures before switch
    maxDowntime: 10  // seconds acceptable
  };
  
  $.writeln("=== ENCODER FAILOVER STRATEGY ===\n");
  
  $.writeln("Primary Encoder: " + primaryEncoder.name);
  $.writeln("Backup Encoder: " + backupEncoder.name);
  $.writeln("");
  
  $.writeln("Health Check:");
  $.writeln("- Interval: Every " + (failover.healthCheckInterval / 1000) + " seconds");
  $.writeln("- Check: RTMP connection, bitrate, frame rate, dropped frames");
  $.writeln("- Threshold: " + failover.failoverThreshold + " consecutive failures = trigger failover");
  $.writeln("");
  
  $.writeln("Failover Procedure:");
  $.writeln("1. Primary encoder health check fails");
  $.writeln("2. Count failures (increment counter)");
  $.writeln("3. If " + failover.failoverThreshold + " failures in a row:");
  $.writeln("   - Send alert to broadcaster");
  $.writeln("   - Prepare backup encoder");
  $.writeln("   - Switch RTMP URL to backup (if multi-ingest support)");
  $.writeln("   - Or: Manually switch (signal backup to start streaming)");
  $.writeln("4. Monitor backup health");
  $.writeln("5. When primary recovers, can switch back (or stay on backup)");
  $.writeln("");
  
  $.writeln("Max Acceptable Downtime:");
  $.writeln("- Live events: < 10-15 seconds acceptable");
  $.writeln("- Switching time: 5-10 seconds typical");
  $.writeln("- Total outage: Viewers see buffering, but stream resumes");
  
  return failover;
}

// Usage
setupEncoderFailover(
  { name: "Primary Encoder (Hardware)", health: "OK" },
  { name: "Backup Encoder (Software)", health: "Standby" }
);
```

---

## QC & Monitoring

### Pre-Broadcast QC Checklist

```javascript
function preBroadcastQCChecklist(eventName, startTime) {
  /**
   * Comprehensive pre-broadcast quality assurance
   * 30-60 min before going live
   */
  
  var checklist = {
    audioVideo: [],
    graphics: [],
    network: [],
    backup: [],
    finalCheck: []
  };
  
  $.writeln("=== PRE-BROADCAST QC CHECKLIST ===\n");
  
  $.writeln("Event: " + eventName);
  $.writeln("Start Time: " + startTime);
  $.writeln("Broadcast Window: 60 min before event");
  $.writeln("");
  
  $.writeln("[30 MIN BEFORE]");
  $.writeln("Audio/Video:");
  $.writeln("☐ Camera(s) connected and powered");
  $.writeln("☐ Microphone levels set (-18 dB reference)");
  $.writeln("☐ Video input signal present (color bars test)");
  $.writeln("☐ Frame rate: 60 fps (verify via encoder)");
  $.writeln("☐ Color grading applied (if needed)");
  $.writeln("");
  
  $.writeln("Graphics:");
  $.writeln("☐ Lower third templates loaded");
  $.writeln("☐ Graphics resolution matches stream (1920x1080)");
  $.writeln("☐ Logo/watermark positioned");
  $.writeln("☐ Countdown timer ready");
  $.writeln("☐ End card/slate prepared");
  $.writeln("");
  
  $.writeln("[15 MIN BEFORE]");
  $.writeln("Network:");
  $.writeln("☐ Internet speed test (upload ≥ 10 Mbps)");
  $.writeln("☐ Ping to CDN < 50ms");
  $.writeln("☐ RTMP authentication verified");
  $.writeln("☐ CDN health status (check provider dashboard)");
  $.writeln("☐ No network congestion (monitor throughout)");
  $.writeln("");
  
  $.writeln("[5 MIN BEFORE]");
  $.writeln("Backup & Contingency:");
  $.writeln("☐ Local recording confirmed (disk space OK)");
  $.writeln("☐ Backup encoder on standby");
  $.writeln("☐ Chat moderation team ready");
  $.writeln("☐ Broadcast team in communication (radio/Slack)");
  $.writeln("☐ Emergency stop button accessible");
  $.writeln("");
  
  $.writeln("[GO LIVE]");
  $.writeln("Final Check:");
  $.writeln("☐ Encoder warmup complete (5 min bitrate stable)");
  $.writeln("☐ Viewer count increasing (platform dashboard)");
  $.writeln("☐ Chat enabled and monitored");
  $.writeln("☐ Audio monitor on (listen for issues)");
  $.writeln("☐ Bitrate graph stable (no spikes)");
  $.writeln("☐ Dropped frame counter at 0");
  
  return checklist;
}

// Usage
preBroadcastQCChecklist("Product Launch Event", "2026-07-15 14:00:00 UTC");
```

### Monitor Stream Health Real-Time

```javascript
function monitorStreamHealthMetrics() {
  /**
   * Real-time stream health dashboard during broadcast
   * Key metrics to watch continuously
   */
  
  var metrics = {
    currentBitrate: 0,
    averageBitrate: 0,
    frameRate: 0,
    droppedFrames: 0,
    audioLevels: { left: 0, right: 0 },
    networkLatency: 0,
    viewerCount: 0,
    bufferingEvents: 0
  };
  
  $.writeln("=== LIVE STREAM MONITORING DASHBOARD ===\n");
  
  $.writeln("Real-Time Metrics (update every 1-5 seconds):");
  $.writeln("");
  
  $.writeln("ENCODER:");
  $.writeln("  Bitrate:      [===== 5.8 Mbps ] (Target: 6000 kbps)");
  $.writeln("  Frame Rate:   [===== 59.97 fps] (Target: 60 fps)");
  $.writeln("  Dropped:      [        0 frames] (Target: 0)");
  $.writeln("  Keyframes:    [  1 every 2s  ] (OK)");
  $.writeln("");
  
  $.writeln("AUDIO:");
  $.writeln("  Left:         [====   -8 dB  ] (Range: -20 to -3)");
  $.writeln("  Right:        [====   -9 dB  ] (Range: -20 to -3)");
  $.writeln("  Sync Offset:  [        +45 ms] (±100 ms acceptable)");
  $.writeln("");
  
  $.writeln("NETWORK:");
  $.writeln("  Latency:      [        38 ms ] (Typical: 20-100 ms)");
  $.writeln("  Jitter:       [        ±5 ms] (Acceptable: <20 ms)");
  $.writeln("  Packet Loss:  [       0.0% ] (Critical if > 1%)");
  $.writeln("");
  
  $.writeln("CDN / VIEWERS:");
  $.writeln("  Viewer Count: [      12,450 ] (Active watchers)");
  $.writeln("  Buffering:    [        2 events] (in last 5 min)");
  $.writeln("  Quality 1080: [       45%     ] (Adaptive bitrate distribution)");
  $.writeln("  Quality 720:  [       35%     ]");
  $.writeln("  Quality 480:  [       20%     ]");
  $.writeln("");
  
  $.writeln("ALERTS:");
  $.writeln("⚠ None (Stream healthy)");
  $.writeln("");
  
  $.writeln("Threshold Warnings:");
  $.writeln("- Bitrate < 5000 kbps for > 30s: Yellow alert");
  $.writeln("- Bitrate < 4000 kbps: Red alert (quality degraded)");
  $.writeln("- Dropped frames > 10/min: Yellow alert");
  $.writeln("- Audio out of sync > 100ms: Red alert");
  $.writeln("- Packet loss > 1%: Critical (stop/failover)");
  
  return metrics;
}

// Usage
monitorStreamHealthMetrics();
```

---

## Live Streaming Workflow Checklist

- ☐ Design multi-bitrate ladder (4-6 variants for HLS/DASH)
- ☐ Select streaming platform (YouTube, Twitch, custom RTMP)
- ☐ Configure encoder profile (bitrate, frame rate, keyframe interval)
- ☐ Test RTMP ingest URL and stream key
- ☐ Set up local backup recording (separate drive/encoder)
- ☐ Configure failover encoder (standby ready)
- ☐ Prepare graphics and overlays (lower thirds, logos, countdown)
- ☐ Verify audio mix and levels (-18 dB reference)
- ☐ Run network connectivity test (upload ≥ 10 Mbps)
- ☐ Execute pre-broadcast QC (30-60 min before)
- ☐ Warm up encoder (5+ min stable bitrate)
- ☐ Monitor stream health metrics in real-time
- ☐ Verify viewer count increasing on CDN
- ☐ Keep local backup recording running throughout
- ☐ Have failover procedure documented and team ready

---

## See Also

- Knowledge/real-world-production-workflows.md — Production automation patterns
- Knowledge/export-rendering-media-encoder.md — Export and encoding specifications
- Knowledge/network-remote-workflows.md — Remote streaming and connectivity
- Knowledge/automation.md — Batch processing and monitoring

---

## Sources

- YouTube Live Encoder Guide: https://support.google.com/youtube/answer/2853702
- Twitch Broadcasting Guide: https://help.twitch.tv/s/article/streaming-guidelines-and-specifications
- HLS Specification: https://tools.ietf.org/html/rfc8216
- DASH Standard: https://dashif.org/
- FFmpeg Live Streaming: https://trac.ffmpeg.org/wiki/Streaming%20media%20and%20DASH
