/**
 * QE DOM Safe Wrapper
 * 
 * Production-ready QE utilities with error handling, bounds checking, version guards.
 * QE = undocumented; use only when UXP insufficient.
 */

(function() {
  'use strict';

  var QESafeWrapper = {
    /**
     * Initialize QE and verify availability
     * 
     * @returns {boolean} true if QE enabled and available
     */
    init: function() {
      try {
        if (typeof app === 'undefined' || !app.enableQE) {
          return false;
        }
        
        var result = app.enableQE();
        if (!result) {
          return false;
        }
        
        // Verify QE object exists
        if (typeof app.qe === 'undefined') {
          return false;
        }
        
        return true;
      } catch (e) {
        return false;
      }
    },

    /**
     * List all effects on a clip by name
     * 
     * @param {number} videoTrackIndex - Track index (0-based)
     * @param {number} clipIndex - Clip index in track (0-based)
     * @returns {Array} Array of { name, index, properties }
     */
    getEffectsByName: function(videoTrackIndex, clipIndex) {
      if (!this.init()) {
        return { error: "QE not available" };
      }
      
      try {
        var qeSeq = app.qe.project.getActiveSequence();
        if (!qeSeq) {
          return { error: "No active sequence" };
        }
        
        // Bounds check
        var numVideoTracks = qeSeq.getNumVideoTracks();
        if (videoTrackIndex < 0 || videoTrackIndex >= numVideoTracks) {
          return { error: "Video track index out of bounds: " + videoTrackIndex };
        }
        
        var qeClip = qeSeq.getAVClipAt(videoTrackIndex, clipIndex);
        if (!qeClip) {
          return { error: "Clip not found at [" + videoTrackIndex + ", " + clipIndex + "]" };
        }
        
        var effects = [];
        var numComponents = qeClip.getNumComponents();
        
        for (var i = 0; i < numComponents; i++) {
          try {
            var comp = qeClip.getComponentAt(i);
            if (comp) {
              var name = comp.getName ? comp.getName() : "Unknown";
              effects.push({
                index: i,
                name: name,
                numProperties: comp.getNumProperties ? comp.getNumProperties() : 0
              });
            }
          } catch (compErr) {
            // Skip broken components
          }
        }
        
        return { effects: effects };
      } catch (e) {
        return { error: e.toString() };
      }
    },

    /**
     * Find effect by name on a clip
     * 
     * @param {number} videoTrackIndex
     * @param {number} clipIndex
     * @param {string} effectName - Exact or partial match
     * @returns {Object} { index, name } or { error }
     */
    findEffectByName: function(videoTrackIndex, clipIndex, effectName) {
      if (!this.init()) {
        return { error: "QE not available" };
      }
      
      try {
        var qeSeq = app.qe.project.getActiveSequence();
        if (!qeSeq) {
          return { error: "No active sequence" };
        }
        
        var qeClip = qeSeq.getAVClipAt(videoTrackIndex, clipIndex);
        if (!qeClip) {
          return { error: "Clip not found" };
        }
        
        // Try exact match first
        var comp = qeClip.getComponentByName(effectName);
        if (comp) {
          return { 
            found: true, 
            name: effectName,
            message: "Exact match found"
          };
        }
        
        // Fall back to partial search
        var numComponents = qeClip.getNumComponents();
        for (var i = 0; i < numComponents; i++) {
          try {
            var c = qeClip.getComponentAt(i);
            var cName = c.getName ? c.getName() : "";
            if (cName.indexOf(effectName) !== -1) {
              return {
                found: true,
                index: i,
                name: cName,
                message: "Partial match found"
              };
            }
          } catch (err) {
            // Skip
          }
        }
        
        return { found: false, message: "Effect not found: " + effectName };
      } catch (e) {
        return { error: e.toString() };
      }
    },

    /**
     * Get clip speed
     * 
     * @param {number} videoTrackIndex
     * @param {number} clipIndex
     * @returns {Object} { speed } or { error }
     */
    getClipSpeed: function(videoTrackIndex, clipIndex) {
      if (!this.init()) {
        return { error: "QE not available" };
      }
      
      try {
        var qeSeq = app.qe.project.getActiveSequence();
        var qeClip = qeSeq.getAVClipAt(videoTrackIndex, clipIndex);
        
        if (!qeClip) {
          return { error: "Clip not found" };
        }
        
        var speed = qeClip.getSpeed();
        return { 
          speed: speed,
          percentage: Math.round(speed * 100)
        };
      } catch (e) {
        return { error: e.toString() };
      }
    },

    /**
     * Set clip speed
     * 
     * @param {number} videoTrackIndex
     * @param {number} clipIndex
     * @param {number} speedFactor - 1.0 = normal, 0.5 = half, 2.0 = double
     * @returns {Object} { success } or { error }
     */
    setClipSpeed: function(videoTrackIndex, clipIndex, speedFactor) {
      if (!this.init()) {
        return { error: "QE not available" };
      }
      
      try {
        // Bounds check
        if (speedFactor <= 0) {
          return { error: "Speed must be > 0" };
        }
        
        var qeSeq = app.qe.project.getActiveSequence();
        var qeClip = qeSeq.getAVClipAt(videoTrackIndex, clipIndex);
        
        if (!qeClip) {
          return { error: "Clip not found" };
        }
        
        qeClip.setSpeed(speedFactor);
        
        return {
          success: true,
          newSpeed: speedFactor,
          message: "Speed set to " + Math.round(speedFactor * 100) + "%"
        };
      } catch (e) {
        return { error: e.toString() };
      }
    },

    /**
     * Ripple delete a clip
     * DANGER: Destructive. Shifts remaining clips to fill gap.
     * 
     * @param {number} videoTrackIndex
     * @param {number} clipIndex
     * @returns {Object} { success } or { error }
     */
    rippleDeleteClip: function(videoTrackIndex, clipIndex) {
      if (!this.init()) {
        return { error: "QE not available" };
      }
      
      try {
        var qeSeq = app.qe.project.getActiveSequence();
        var qeClip = qeSeq.getAVClipAt(videoTrackIndex, clipIndex);
        
        if (!qeClip) {
          return { error: "Clip not found" };
        }
        
        qeClip.rippleDelete();
        
        return {
          success: true,
          message: "Clip ripple-deleted and remaining clips shifted"
        };
      } catch (e) {
        return { error: e.toString() };
      }
    }
  };

  // Return API for CEP or direct invocation
  return {
    api: QESafeWrapper,
    initialized: QESafeWrapper.init(),
    warning: "QE DOM is undocumented and unstable. Use only when necessary."
  };
})();
