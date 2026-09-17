/**
 * VFX List Export Tool - UXP Panel v4 - Manual Caption Editor
 * Since caption.setText() not available in UXP 25.6:
 * Implement sequential manual editing UI
 *
 * Workflow:
 * 1. Load all captions
 * 2. Show in list with edit fields
 * 3. User edits each caption text in panel
 * 4. Click "Apply" to save each one
 * 5. Move to next caption
 */

const { application } = require("premierepro");

class VFXListToolV4Manual {
  constructor() {
    this.sequence = null;
    this.project = null;
    this.markers = [];
    this.captions = [];
    this.clips = [];
    this.presets = new Map();
    this.currentEditingCaption = null;
    this.captionEditIndex = 0;

    this.loadPresets();
    this.initializeUI();
    this.log("VFX List Tool v4 initialized (manual caption editor)");
  }

  initializeUI() {
    document.getElementById("executeBtn")?.addEventListener("click", () => this.executeAll());
    document.getElementById("reloadBtn")?.addEventListener("click", () => this.reload());
    document.getElementById("resetBtn")?.addEventListener("click", () => this.resetPatterns());

    document.getElementById("savePresetBtn")?.addEventListener("click", () => this.savePresetDialog());
    document.getElementById("deletePresetBtn")?.addEventListener("click", () => this.deletePreset());
    document.getElementById("presetSelect")?.addEventListener("change", (e) => this.loadPreset(e.target.value));

    // Caption manual editor buttons
    document.getElementById("startCaptionEditBtn")?.addEventListener("click", () => this.startCaptionEditing());
    document.getElementById("applyCaptionBtn")?.addEventListener("click", () => this.applyCurrentCaption());
    document.getElementById("skipCaptionBtn")?.addEventListener("click", () => this.skipToNextCaption());
    document.getElementById("cancelCaptionEditBtn")?.addEventListener("click", () => this.cancelCaptionEditing());

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
        `✓ Loaded: ${this.markers.length} markers | ${this.captions.length} captions (manual edit) | ${this.clips.length} text clips`,
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

    // Captions list - EDITABLE
    const captionList = document.getElementById("captionList");
    if (!captionList) return;

    captionList.innerHTML = "";
    if (this.captions.length === 0) {
      captionList.innerHTML = '<div class="empty-list">No captions</div>';
    } else {
      const info = document.createElement("div");
      info.className = "info-block";
      info.style.padding = "8px";
      info.style.marginBottom = "8px";
      info.style.backgroundColor = "#1e3a5f";
      info.style.borderRadius = "4px";
      info.innerHTML = `📝 ${this.captions.length} captions loaded. Manual edit mode.`;
      captionList.appendChild(info);

      for (let i = 0; i < this.captions.length; i++) {
        const cap = this.captions[i];
        try {
          const text = await cap.text;
          const item = document.createElement("div");
          item.className = "caption-item";
          item.style.padding = "8px";
          item.style.marginBottom = "6px";
          item.style.backgroundColor = "#0a0e27";
          item.style.border = "1px solid #333";
          item.style.borderRadius = "4px";
          item.style.cursor = "pointer";
          item.style.display = "flex";
          item.style.justifyContent = "space-between";
          item.style.alignItems = "center";

          const textSpan = document.createElement("span");
          textSpan.style.flex = "1";
          textSpan.style.marginRight = "8px";
          textSpan.textContent = `[${i + 1}] ${text.substring(0, 40)}${text.length > 40 ? "..." : ""}`;

          const editBtn = document.createElement("button");
          editBtn.textContent = "Edit";
          editBtn.style.padding = "4px 8px";
          editBtn.style.fontSize = "12px";
          editBtn.style.cursor = "pointer";
          editBtn.onclick = (e) => {
            e.stopPropagation();
            this.openCaptionEditor(i);
          };

          item.appendChild(textSpan);
          item.appendChild(editBtn);
          captionList.appendChild(item);
        } catch (e) {
          this.log("Error reading caption:", e);
        }
      }
    }
    document.getElementById("captionCount").textContent = `(${this.captions.length}) [manual edit]`;
  }

  /**
   * Open caption editor for specific index
   */
  async openCaptionEditor(index) {
    if (index < 0 || index >= this.captions.length) return;

    this.captionEditIndex = index;
    const cap = this.captions[index];
    const text = await cap.text;

    // Show editor UI
    const editorContainer = document.getElementById("captionEditorContainer");
    if (!editorContainer) return;

    editorContainer.style.display = "block";
    editorContainer.innerHTML = `
      <div style="padding: 12px; background: #1a1f3a; border: 2px solid #2563eb; border-radius: 6px;">
        <div style="margin-bottom: 8px; font-weight: bold; color: #60a5fa;">
          Editing Caption ${index + 1} / ${this.captions.length}
        </div>

        <div style="margin-bottom: 8px; font-size: 12px; color: #999;">
          Original text:
        </div>
        <div style="margin-bottom: 12px; padding: 8px; background: #0a0e27; border: 1px solid #333; border-radius: 4px; max-height: 60px; overflow-y: auto;">
          ${text}
        </div>

        <div style="margin-bottom: 8px; font-size: 12px; color: #999;">
          Edit text:
        </div>
        <textarea id="captionEditField" style="
          width: 100%;
          padding: 8px;
          background: #0a0e27;
          color: #fff;
          border: 1px solid #444;
          border-radius: 4px;
          font-family: monospace;
          font-size: 13px;
          min-height: 80px;
          resize: vertical;
        "></textarea>

        <div style="display: flex; gap: 8px; margin-top: 12px;">
          <button id="applyCaptionBtn" style="flex: 1; padding: 8px; background: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">✓ Apply</button>
          <button id="skipCaptionBtn" style="flex: 1; padding: 8px; background: #6b7280; color: white; border: none; border-radius: 4px; cursor: pointer;">→ Skip</button>
          <button id="cancelCaptionEditBtn" style="flex: 1; padding: 8px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer;">✕ Cancel</button>
        </div>
      </div>
    `;

    const field = document.getElementById("captionEditField");
    if (field) {
      field.value = text;
      field.focus();
      field.select();
    }

    // Rebind buttons
    document.getElementById("applyCaptionBtn")?.addEventListener("click", () => this.applyCurrentCaption());
    document.getElementById("skipCaptionBtn")?.addEventListener("click", () => this.skipToNextCaption());
    document.getElementById("cancelCaptionEditBtn")?.addEventListener("click", () => this.cancelCaptionEditing());

    this.status(`✏️ Editing caption ${index + 1}/${this.captions.length}`, "info");
  }

  /**
   * Apply changes to current caption
   */
  async applyCurrentCaption() {
    const field = document.getElementById("captionEditField");
    if (!field) return;

    const newText = field.value.trim();
    if (!newText) {
      this.status("⚠️ Caption text cannot be empty", "error");
      return;
    }

    try {
      const cap = this.captions[this.captionEditIndex];

      // Try to set caption text
      await cap.setText(newText);

      this.status(`✓ Caption ${this.captionEditIndex + 1} updated`, "success");
      this.log(`Updated caption ${this.captionEditIndex + 1}: ${newText.substring(0, 50)}...`);

      // Move to next
      if (this.captionEditIndex < this.captions.length - 1) {
        await this.openCaptionEditor(this.captionEditIndex + 1);
      } else {
        this.status(`✓ All captions done! Reloading...`, "success");
        this.cancelCaptionEditing();
        await this.reload();
      }
    } catch (e) {
      this.status(`❌ Error updating caption: ${e.message}`, "error");
      this.log("Caption update error:", e);
    }
  }

  /**
   * Skip to next caption
   */
  async skipToNextCaption() {
    if (this.captionEditIndex < this.captions.length - 1) {
      await this.openCaptionEditor(this.captionEditIndex + 1);
    } else {
      this.status(`All captions reviewed`, "info");
      this.cancelCaptionEditing();
    }
  }

  /**
   * Cancel caption editing
   */
  cancelCaptionEditing() {
    const editorContainer = document.getElementById("captionEditorContainer");
    if (editorContainer) {
      editorContainer.style.display = "none";
      editorContainer.innerHTML = "";
    }
    this.status("Ready", "info");
  }

  /**
   * Start caption editing workflow
   */
  async startCaptionEditing() {
    if (this.captions.length === 0) {
      this.status("⚠️ No captions to edit", "error");
      return;
    }

    this.captionEditIndex = 0;
    await this.openCaptionEditor(0);
  }

  /**
   * Execute all rename operations (markers only, captions manual)
   */
  async executeAll() {
    const markerPattern = document.getElementById("markerPattern").value;
    const limitToRange = document.getElementById("limitToRange").checked;

    if (!markerPattern) {
      this.status("⚠️ No marker pattern specified", "error");
      return;
    }

    this.status("Executing marker batch operations...", "info");

    try {
      let results = [];

      // Get TC range if limited
      let inOutRange = null;
      if (limitToRange) {
        inOutRange = await this.getTCRange();
        if (!inOutRange) {
          this.status("⚠️ TC Range limiting enabled but IN/OUT markers not found", "error");
          return;
        }
      }

      await application.executeTransaction(async () => {
        // Rename markers
        if (markerPattern) {
          const markerResults = await this.renameMarkers(markerPattern, inOutRange);
          if (markerResults > 0) {
            results.push(`✓ Renamed ${markerResults} markers`);
            if (limitToRange && inOutRange) {
              results.push(`   (Limited to TC: ${inOutRange.inTime} - ${inOutRange.outTime})`);
            }
          }
        }
      });

      const message = results.length > 0
        ? `✓ Complete:\n${results.join("\n")}\n\n📝 For captions: Click "Edit Captions" button to open manual editor`
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
   * Get TC range from IN/OUT markers
   */
  async getTCRange() {
    try {
      let inMarker = null;
      let outMarker = null;

      for (let m of this.markers) {
        const name = await m.name;
        const start = await m.start;

        if (name.toUpperCase() === "IN") {
          inMarker = { name, start };
        } else if (name.toUpperCase() === "OUT") {
          outMarker = { name, start };
        }
      }

      if (!inMarker || !outMarker) {
        return null;
      }

      // Convert ticks to timecode string
      const inTime = this.ticksToTimecode(inMarker.start);
      const outTime = this.ticksToTimecode(outMarker.start);

      return {
        inTicks: inMarker.start,
        outTicks: outMarker.start,
        inTime,
        outTime
      };
    } catch (e) {
      this.log("Error getting TC range:", e);
      return null;
    }
  }

  /**
   * Convert ticks to timecode string (HH:MM:SS:FF)
   */
  ticksToTimecode(ticks) {
    try {
      const seq = this.sequence;
      if (!seq) return "00:00:00:00";

      // Basic conversion (simplified - real implementation would use sequence settings)
      const frameRate = 30; // Default, should read from sequence
      const totalFrames = Math.floor(ticks / (254016000 / frameRate)); // 254016000 ticks per second

      const hours = Math.floor(totalFrames / (frameRate * 3600));
      const minutes = Math.floor((totalFrames % (frameRate * 3600)) / (frameRate * 60));
      const seconds = Math.floor((totalFrames % (frameRate * 60)) / frameRate);
      const frames = totalFrames % frameRate;

      return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}:${String(frames).padStart(2, "0")}`;
    } catch (e) {
      return "00:00:00:00";
    }
  }

  /**
   * Check if marker is within TC range
   */
  isMarkerInRange(markerStart, tcRange) {
    if (!tcRange) return true;
    return markerStart >= tcRange.inTicks && markerStart <= tcRange.outTicks;
  }

  /**
   * Rename markers only
   */
  async renameMarkers(pattern, tcRange) {
    let count = 0;
    let counter = 1;
    let skipped = 0;

    for (let m of this.markers) {
      try {
        const name = await m.name;
        const start = await m.start;

        // Skip IN/OUT markers
        if (name.toUpperCase().includes("IN") || name.toUpperCase().includes("OUT")) {
          continue;
        }

        // Check TC range if enabled
        if (tcRange && !this.isMarkerInRange(start, tcRange)) {
          skipped++;
          this.log(`Skipped marker (outside TC range): ${name}`);
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

    if (skipped > 0) {
      this.log(`Skipped ${skipped} markers outside TC range`);
    }

    return count;
  }

  /**
   * Reset patterns
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
      const stored = localStorage.getItem("vfx-presets-v4");
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
      localStorage.setItem("vfx-presets-v4", JSON.stringify(obj));
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
    console.log("[VFX Tool v4]", ...args);
  }
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  try {
    window.vfxTool = new VFXListToolV4Manual();
  } catch (e) {
    console.error("Init error:", e);
    const status = document.getElementById("status");
    if (status) {
      status.textContent = `❌ ${e.message}`;
      status.className = "status-area error";
    }
  }
});
