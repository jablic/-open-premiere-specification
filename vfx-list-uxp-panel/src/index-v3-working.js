/**
 * VFX List Export Tool - UXP Panel v3 WORKING (HONEST API LIMITS)
 * Only implements what ACTUALLY works in UXP 25.6
 *
 * Real capabilities (verified):
 * ✅ Markers: full support (rename works)
 * ❌ Captions: read-only (setText() not available - Adobe limitation)
 * ❌ Text clips: read-only (MOGRT internals inaccessible - API gap)
 *
 * Wait for Premiere 26.x for caption/text automation
 */

const { application } = require("premierepro");

class VFXListToolWorking {
  constructor() {
    this.sequence = null;
    this.project = null;
    this.markers = [];
    this.captions = [];
    this.clips = [];
    this.presets = new Map();

    this.loadPresets();
    this.initializeUI();
    this.log("VFX List Tool v3 initialized (minimal working version)");
  }

  initializeUI() {
    document.getElementById("executeBtn")?.addEventListener("click", () => this.executeAll());
    document.getElementById("reloadBtn")?.addEventListener("click", () => this.reload());
    document.getElementById("resetBtn")?.addEventListener("click", () => this.resetPatterns());

    document.getElementById("savePresetBtn")?.addEventListener("click", () => this.savePresetDialog());
    document.getElementById("deletePresetBtn")?.addEventListener("click", () => this.deletePreset());
    document.getElementById("presetSelect")?.addEventListener("change", (e) => this.loadPreset(e.target.value));

    this.reload();
  }

  /**
   * Reload all data from timeline
   */
  async reload() {
    this.status("Loading timeline data...", "info");
    try {
      const proj = await application.activeProject;
      if (!proj) {
        this.status("❌ No active project", "error");
        return;
      }

      this.project = proj;
      this.sequence = await proj.activeSequence;
      if (!this.sequence) {
        this.status("❌ No active sequence", "error");
        return;
      }

      await this.loadMarkers();
      await this.loadCaptions();
      await this.loadClips();
      await this.renderUI();

      this.status(
        `✓ Loaded: ${this.markers.length} markers (ready to rename) | ${this.captions.length} captions (read-only) | ${this.clips.length} text clips (read-only)`,
        "success"
      );
    } catch (e) {
      this.status(`❌ Error: ${e.message}`, "error");
      this.log("Error:", e);
    }
  }

  /**
   * Load markers from sequence
   */
  async loadMarkers() {
    try {
      this.markers = await this.sequence.markers;
      if (!this.markers) this.markers = [];
      this.log(`Loaded ${this.markers.length} markers`);
    } catch (e) {
      this.log("Error loading markers:", e);
      this.markers = [];
    }
  }

  /**
   * Load captions from sequence
   * Note: UXP captions API is limited
   */
  async loadCaptions() {
    try {
      this.captions = await this.sequence.captions;
      if (!this.captions) this.captions = [];
      this.log(`Loaded ${this.captions.length} captions`);
    } catch (e) {
      this.log("Error loading captions:", e);
      this.captions = [];
    }
  }

  /**
   * Load text clips from video tracks
   * Note: Can read names but CANNOT edit text in UXP 25.6
   */
  async loadClips() {
    this.clips = [];
    try {
      const trackCount = await this.sequence.videoTracks.length;

      for (let t = 0; t < trackCount; t++) {
        const track = await this.sequence.videoTracks[t];
        const clipCount = await track.clips.length;

        for (let c = 0; c < clipCount; c++) {
          const clip = await track.clips[c];
          const name = await clip.name;

          const isTextClip =
            name.toLowerCase().includes("title") ||
            name.toLowerCase().includes("text") ||
            name.toLowerCase().includes("plate") ||
            name.toLowerCase().includes("mogrt");

          if (isTextClip) {
            this.clips.push({
              clip,
              name,
              track: t,
              clipIdx: c
            });
          }
        }
      }
      this.log(`Loaded ${this.clips.length} text clips (read-only)`);
    } catch (e) {
      this.log("Error loading clips:", e);
    }
  }

  /**
   * Render UI with current data
   */
  async renderUI() {
    // Markers list
    const markerList = document.getElementById("markerList");
    if (!markerList) return;

    markerList.innerHTML = "";
    if (this.markers.length === 0) {
      markerList.innerHTML = '<div class="empty-list">No markers</div>';
    } else {
      for (let m of this.markers) {
        const name = await m.name;
        const item = document.createElement("div");
        item.className = "item";
        item.textContent = name;
        markerList.appendChild(item);
      }
    }
    document.getElementById("markerCount").textContent = `(${this.markers.length})`;

    // Captions list (read-only warning)
    const captionList = document.getElementById("captionList");
    if (!captionList) return;

    captionList.innerHTML = "";
    if (this.captions.length === 0) {
      captionList.innerHTML = '<div class="empty-list">No captions</div>';
    } else {
      const warning = document.createElement("div");
      warning.className = "empty-list";
      warning.style.color = "#ff9900";
      warning.style.padding = "8px";
      warning.textContent = "⚠️ Read-only (UXP 25.6). Use Premiere 26.x for automation.";
      captionList.appendChild(warning);

      for (let cap of this.captions) {
        try {
          const text = await cap.text;
          const item = document.createElement("div");
          item.className = "item";
          item.style.opacity = "0.6";
          item.textContent = text.substring(0, 50) + (text.length > 50 ? "..." : "");
          captionList.appendChild(item);
        } catch (e) {
          this.log("Error reading caption:", e);
        }
      }
    }
    document.getElementById("captionCount").textContent = `(${this.captions.length}) [read-only]`;
    document.getElementById("captionPattern").disabled = true;
    document.getElementById("captionPattern").placeholder = "Not supported in UXP 25.6";

    // Text clips list (read-only - API gap)
    const plateList = document.getElementById("plateList");
    if (!plateList) return;

    plateList.innerHTML = "";
    if (this.clips.length === 0) {
      plateList.innerHTML = '<div class="empty-list">No text clips</div>';
    } else {
      const warning = document.createElement("div");
      warning.className = "empty-list";
      warning.style.color = "#ff9900";
      warning.style.padding = "8px";
      warning.textContent = "⚠️ Read-only (UXP 25.6). MOGRT internals not accessible. See v2 Hybrid for workaround.";
      plateList.appendChild(warning);

      for (let c of this.clips) {
        const item = document.createElement("div");
        item.className = "item";
        item.style.opacity = "0.6";
        item.textContent = c.name;
        plateList.appendChild(item);
      }
    }
    document.getElementById("plateCount").textContent = `(${this.clips.length}) [read-only]`;
    document.getElementById("platePattern").disabled = true;
    document.getElementById("platePattern").placeholder = "MOGRT editing not supported in UXP 25.6";
  }

  /**
   * Execute rename operations
   * ONLY markers work - captions/text are API limitations in UXP 25.6
   */
  async executeAll() {
    const markerPattern = document.getElementById("markerPattern").value;

    if (!markerPattern) {
      this.status("⚠️ No marker pattern specified", "error");
      return;
    }

    this.status("Executing marker batch operations...", "info");

    try {
      let results = [];

      await application.executeTransaction(async () => {
        // Rename markers (ONLY this works)
        if (markerPattern) {
          const markerResults = await this.renameMarkers(markerPattern);
          if (markerResults > 0) {
            results.push(`✓ Renamed ${markerResults} markers`);
          }
        }
      });

      const message = results.length > 0
        ? `✓ Complete:\n${results.join("\n")}\n\n⚠️ Captions & text clips: UXP 25.6 API limitation (read-only). Use Premiere 26.x or manual edit.`
        : "⚠️ No markers renamed";

      this.status(message, results.length > 0 ? "success" : "error");

      if (document.getElementById("autoReload").checked) {
        await this.reload();
      }
    } catch (e) {
      this.status(`❌ Error: ${e.message}`, "error");
      this.log("Execute error:", e);
    }
  }

  /**
   * Rename markers only
   */
  async renameMarkers(pattern) {
    let count = 0;
    let counter = 1;

    for (let m of this.markers) {
      try {
        const name = await m.name;

        // Skip IN/OUT markers
        if (name.toUpperCase().includes("IN") || name.toUpperCase().includes("OUT")) {
          continue;
        }

        const newName = pattern.replace("{shot}", String(counter).padStart(4, "0"));
        await m.setName(newName);
        count++;
        counter++;
        this.log(`Renamed marker: ${name} → ${newName}`);
      } catch (e) {
        this.log(`Error renaming marker:`, e);
      }
    }

    return count;
  }

  /**
   * Captions NOT supported in UXP 25.6
   * Adobe marked caption API as "partial" - read-only, no setText()
   */
  async renameCaptions(pattern) {
    this.log("Caption renaming: UXP 25.6 API limitation - setText() not available");
    return 0;
  }

  /**
   * Reset marker pattern
   */
  resetPatterns() {
    document.getElementById("markerPattern").value = "CG_{shot}";
    this.status("✓ Marker pattern reset", "info");
  }

  /**
   * Preset management
   */
  loadPresets() {
    try {
      const stored = localStorage.getItem("vfx-presets-v3");
      if (stored) {
        const presets = JSON.parse(stored);
        for (const [name, data] of Object.entries(presets)) {
          this.presets.set(name, data);
        }
      }

      if (!this.presets.has("Default")) {
        this.presets.set("Default", {
          markerPattern: "CG_{shot}"
        });
      }

      this.updatePresetSelect();
    } catch (e) {
      this.log("Error loading presets:", e);
    }
  }

  savePresetDialog() {
    const name = prompt("Preset name:");
    if (!name) return;

    const preset = {
      markerPattern: document.getElementById("markerPattern").value
    };

    this.presets.set(name, preset);
    this.savePresetsToStorage();
    this.updatePresetSelect();
    this.status(`✓ Preset saved: ${name}`, "success");
  }

  loadPreset(name) {
    if (!name) return;

    const preset = this.presets.get(name);
    if (!preset) return;

    document.getElementById("markerPattern").value = preset.markerPattern || "";

    this.status(`✓ Loaded: ${name}`, "success");
  }

  deletePreset() {
    const select = document.getElementById("presetSelect");
    const name = select.value;

    if (!name || name === "Default") {
      this.status("Cannot delete Default preset", "error");
      return;
    }

    if (confirm(`Delete "${name}"?`)) {
      this.presets.delete(name);
      this.savePresetsToStorage();
      this.updatePresetSelect();
      this.status(`✓ Deleted: ${name}`, "success");
    }
  }

  updatePresetSelect() {
    const select = document.getElementById("presetSelect");
    const currentValue = select.value;

    select.innerHTML = '<option value="">Load Preset...</option>';

    for (const name of this.presets.keys()) {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      select.appendChild(option);
    }

    if (currentValue && this.presets.has(currentValue)) {
      select.value = currentValue;
    }
  }

  savePresetsToStorage() {
    try {
      const obj = {};
      for (const [name, data] of this.presets) {
        obj[name] = data;
      }
      localStorage.setItem("vfx-presets-v3", JSON.stringify(obj));
    } catch (e) {
      this.log("Error saving presets:", e);
    }
  }

  /**
   * Status message
   */
  status(message, type = "info") {
    const area = document.getElementById("status");
    if (!area) return;
    area.textContent = message;
    area.className = `status-area ${type}`;
  }

  /**
   * Debug logging
   */
  log(...args) {
    console.log("[VFX Tool]", ...args);
  }
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  try {
    window.vfxTool = new VFXListToolWorking();
  } catch (e) {
    console.error("Init error:", e);
    const status = document.getElementById("status");
    if (status) {
      status.textContent = `❌ ${e.message}`;
      status.className = "status-area error";
    }
  }
});
