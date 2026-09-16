/**
 * VFX List Export Tool - UXP Panel
 * Full automation for batch renaming markers, captions, and text plates
 * Premiere Pro 2026 / 25.6+
 */

const { application } = require("premierepro");

class VFXListTool {
  constructor() {
    this.sequence = null;
    this.project = null;
    this.markers = [];
    this.captions = [];
    this.clips = [];
    this.presets = new Map();
    this.loadPresets();
    this.initializeUI();
  }

  /**
   * Initialize UI event listeners
   */
  initializeUI() {
    // Buttons
    document.getElementById("executeBtn").addEventListener("click", () => this.executeAll());
    document.getElementById("reloadBtn").addEventListener("click", () => this.reload());
    document.getElementById("resetBtn").addEventListener("click", () => this.resetPatterns());

    // Presets
    document.getElementById("savePresetBtn").addEventListener("click", () => this.savePresetDialog());
    document.getElementById("deletePresetBtn").addEventListener("click", () => this.deletePreset());
    document.getElementById("presetSelect").addEventListener("change", (e) => this.loadPreset(e.target.value));

    // Initial load
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
        this.status("No active project", "error");
        return;
      }

      this.project = proj;
      this.sequence = await proj.activeSequence;
      if (!this.sequence) {
        this.status("No active sequence", "error");
        return;
      }

      await this.loadMarkers();
      await this.loadCaptions();
      await this.loadClips();
      await this.renderUI();

      this.status(
        `✓ Loaded ${this.markers.length} markers, ${this.captions.length} captions, ${this.clips.length} text plates`,
        "success"
      );
    } catch (e) {
      this.status(`Error: ${e.message}`, "error");
      console.error(e);
    }
  }

  /**
   * Load markers from sequence
   */
  async loadMarkers() {
    try {
      this.markers = await this.sequence.markers;
      if (!this.markers) {
        this.markers = [];
      }
    } catch (e) {
      console.error("Error loading markers:", e);
      this.markers = [];
    }
  }

  /**
   * Load captions from sequence
   */
  async loadCaptions() {
    try {
      this.captions = await this.sequence.captions;
      if (!this.captions) {
        this.captions = [];
      }
    } catch (e) {
      console.error("Error loading captions:", e);
      this.captions = [];
    }
  }

  /**
   * Load text clips from video tracks
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

          // Filter for text/title/plate clips
          const isTextClip =
            name.toLowerCase().includes("title") ||
            name.toLowerCase().includes("text") ||
            name.toLowerCase().includes("plate") ||
            name.toLowerCase().includes("mogrt");

          if (isTextClip) {
            this.clips.push({ clip, name, track: t, clipIdx: c });
          }
        }
      }
    } catch (e) {
      console.error("Error loading clips:", e);
    }
  }

  /**
   * Render UI with current data
   */
  async renderUI() {
    // Render markers
    const markerList = document.getElementById("markerList");
    markerList.innerHTML = "";

    if (this.markers.length === 0) {
      markerList.innerHTML = '<div class="empty-list">No markers found</div>';
    } else {
      for (let m of this.markers) {
        const name = await m.name;
        const color = await m.customColor;

        const item = document.createElement("div");
        item.className = "item";

        const nameSpan = document.createElement("span");
        nameSpan.className = "item-name";
        nameSpan.textContent = name;

        const colorSpan = document.createElement("span");
        colorSpan.className = "item-color";
        colorSpan.style.backgroundColor = this.getColorHex(color);

        item.appendChild(nameSpan);
        item.appendChild(colorSpan);
        markerList.appendChild(item);
      }
    }

    document.getElementById("markerCount").textContent = `(${this.markers.length})`;

    // Render captions
    const captionList = document.getElementById("captionList");
    captionList.innerHTML = "";

    if (this.captions.length === 0) {
      captionList.innerHTML = '<div class="empty-list">No captions found</div>';
    } else {
      for (let cap of this.captions) {
        const text = await cap.text;

        const item = document.createElement("div");
        item.className = "item";
        item.textContent = text.substring(0, 50) + (text.length > 50 ? "..." : "");

        captionList.appendChild(item);
      }
    }

    document.getElementById("captionCount").textContent = `(${this.captions.length})`;

    // Render clips
    const plateList = document.getElementById("plateList");
    plateList.innerHTML = "";

    if (this.clips.length === 0) {
      plateList.innerHTML = '<div class="empty-list">No text plates found</div>';
    } else {
      for (let c of this.clips) {
        const item = document.createElement("div");
        item.className = "item";
        item.textContent = c.name;

        plateList.appendChild(item);
      }
    }

    document.getElementById("plateCount").textContent = `(${this.clips.length})`;
  }

  /**
   * Get hex color from Premiere color name
   */
  getColorHex(colorName) {
    const colors = {
      Red: "#ff4444",
      Blue: "#4488ff",
      Green: "#44ff44",
      Yellow: "#ffff44",
      Cyan: "#44ffff",
      Magenta: "#ff44ff",
      White: "#ffffff"
    };
    return colors[colorName] || "#909090";
  }

  /**
   * Execute all rename operations
   */
  async executeAll() {
    const markerPattern = document.getElementById("markerPattern").value;
    const captionPattern = document.getElementById("captionPattern").value;
    const platePattern = document.getElementById("platePattern").value;
    const limitToRange = document.getElementById("limitToRange").checked;

    if (!markerPattern && !captionPattern && !platePattern) {
      this.status("No patterns specified", "error");
      return;
    }

    this.status("Executing batch operations...", "info");

    try {
      // Execute all changes in a single transaction
      await application.executeTransaction(async () => {
        const results = [];

        // Rename markers
        if (markerPattern) {
          const markerResults = await this.renameMarkers(markerPattern, limitToRange);
          if (markerResults > 0) {
            results.push(`Renamed ${markerResults} markers`);
          }
        }

        // Rename captions
        if (captionPattern) {
          const captionResults = await this.renameCaptions(captionPattern, limitToRange);
          if (captionResults > 0) {
            results.push(`Renamed ${captionResults} captions`);
          }
        }

        // Rename text plates
        if (platePattern) {
          const plateResults = await this.renamePlates(platePattern, limitToRange);
          if (plateResults > 0) {
            results.push(`Renamed ${plateResults} text plates`);
          }
        }

        const message = results.join(" • ");
        this.status(`✓ Batch complete:\n${message}`, "success");
      });

      // Reload if auto-reload is enabled
      if (document.getElementById("autoReload").checked) {
        await this.reload();
      }
    } catch (e) {
      this.status(`Error: ${e.message}`, "error");
      console.error(e);
    }
  }

  /**
   * Rename markers
   */
  async renameMarkers(pattern, limitToRange) {
    let count = 0;
    let counter = 1;

    for (let m of this.markers) {
      const name = await m.name;

      // Skip IN/OUT markers
      if (
        name.toUpperCase().includes("IN") ||
        name.toUpperCase().includes("OUT")
      ) {
        continue;
      }

      const newName = pattern.replace("{shot}", String(counter).padStart(4, "0"));
      await m.setName(newName);
      count++;
      counter++;
    }

    return count;
  }

  /**
   * Rename captions
   */
  async renameCaptions(pattern, limitToRange) {
    let count = 0;
    let counter = 1;

    for (let cap of this.captions) {
      const newText = pattern.replace("{shot}", String(counter).padStart(4, "0"));
      await cap.setText(newText);
      count++;
      counter++;
    }

    return count;
  }

  /**
   * Rename text plates
   */
  async renamePlates(pattern, limitToRange) {
    let count = 0;
    let counter = 1;

    for (let c of this.clips) {
      const newName = pattern.replace("{shot}", String(counter).padStart(4, "0"));
      await c.clip.setName(newName);
      count++;
      counter++;
    }

    return count;
  }

  /**
   * Reset patterns to defaults
   */
  resetPatterns() {
    document.getElementById("markerPattern").value = "CG_{shot}";
    document.getElementById("captionPattern").value = "CAP_{shot}";
    document.getElementById("platePattern").value = "PLATE_{shot}";
    this.status("Patterns reset", "info");
  }

  /**
   * Preset management
   */
  loadPresets() {
    try {
      const stored = localStorage.getItem("vfx-presets");
      if (stored) {
        const presets = JSON.parse(stored);
        for (const [name, data] of Object.entries(presets)) {
          this.presets.set(name, data);
        }
      }

      // Built-in defaults
      if (!this.presets.has("Default")) {
        this.presets.set("Default", {
          markerPattern: "CG_{shot}",
          captionPattern: "CAP_{shot}",
          platePattern: "PLATE_{shot}"
        });
      }

      this.updatePresetSelect();
    } catch (e) {
      console.error("Error loading presets:", e);
    }
  }

  savePresetDialog() {
    const name = prompt("Preset name:");
    if (!name) return;

    const preset = {
      markerPattern: document.getElementById("markerPattern").value,
      captionPattern: document.getElementById("captionPattern").value,
      platePattern: document.getElementById("platePattern").value
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
    document.getElementById("captionPattern").value = preset.captionPattern || "";
    document.getElementById("platePattern").value = preset.platePattern || "";

    this.status(`✓ Loaded preset: ${name}`, "success");
  }

  deletePreset() {
    const select = document.getElementById("presetSelect");
    const name = select.value;

    if (!name || name === "Default") {
      this.status("Cannot delete Default preset", "error");
      return;
    }

    if (confirm(`Delete preset "${name}"?`)) {
      this.presets.delete(name);
      this.savePresetsToStorage();
      this.updatePresetSelect();
      this.status(`✓ Preset deleted: ${name}`, "success");
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
      localStorage.setItem("vfx-presets", JSON.stringify(obj));
    } catch (e) {
      console.error("Error saving presets:", e);
    }
  }

  /**
   * Status message
   */
  status(message, type = "info") {
    const area = document.getElementById("status");
    area.textContent = message;
    area.className = `status-area ${type}`;
  }
}

// Initialize when panel loads
document.addEventListener("DOMContentLoaded", () => {
  try {
    window.vfxTool = new VFXListTool();
  } catch (e) {
    console.error("Failed to initialize VFX Tool:", e);
    document.getElementById("status").textContent = `Initialization error: ${e.message}`;
    document.getElementById("status").className = "status-area error";
  }
});
