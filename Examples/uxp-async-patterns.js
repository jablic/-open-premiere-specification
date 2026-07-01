/**
 * UXP Async Patterns & Best Practices
 *
 * Runtime: UXP / JavaScript (ES2017+) for Premiere Pro 25.6+
 *
 * Purpose:
 * - Demonstrate correct async/await patterns for UXP
 * - Show createSequenceFromMedia with error handling
 * - Batch operations with executeTransaction
 * - Reading markers, clips, and metadata asynchronously
 *
 * Topic docs: uxp.md, markers-and-annotations.md
 */

const { application } = require("premierepro");

// ============================================================================
// PATTERN 1: Basic async/await with error handling
// ============================================================================

async function getActiveSequenceName() {
  try {
    const project = await application.activeProject;
    if (!project) {
      console.error("No active project");
      return null;
    }

    const seq = await project.activeSequence;
    if (!seq) {
      console.error("No active sequence");
      return null;
    }

    const name = await seq.name;
    return name;
  } catch (error) {
    console.error("Error getting sequence:", error.message);
    return null;
  }
}

// ============================================================================
// PATTERN 2: createSequenceFromMedia with file paths
// ============================================================================

async function createSequenceFromMediaFiles(mediaFilePaths, sequenceName) {
  /**
   * Import media files, create a sequence with them
   * This is the UXP async equivalent of ExtendScript batch import
   */

  try {
    const project = await application.activeProject;
    if (!project) throw new Error("No active project");

    const rootBin = await project.rootBin;

    // Step 1: Import files
    console.log("Importing media files...");
    const importSuccess = await project.importFiles(
      mediaFilePaths,
      false,  // suppressUI
      rootBin
    );

    if (!importSuccess) {
      throw new Error("Import failed");
    }

    console.log("Import successful. Creating sequence...");

    // Step 2: Create sequence with imported media
    // (Note: In UXP 25.6, you must query rootBin.children to find imported items)
    const sequenceObj = await project.createSequence(
      sequenceName || "New Sequence"
    );

    if (!sequenceObj) {
      throw new Error("Sequence creation failed");
    }

    const newSeqName = await sequenceObj.name;
    console.log("Created sequence:", newSeqName);

    return sequenceObj;

  } catch (error) {
    console.error("Error creating sequence from media:", error.message);
    return null;
  }
}

// ============================================================================
// PATTERN 3: Batch marker creation inside executeTransaction
// ============================================================================

async function batchCreateMarkersInTransaction(markers) {
  /**
   * Create multiple markers atomically in a single undo step
   * Best practice: wrap all mutations in executeTransaction
   */

  try {
    const project = await application.activeProject;
    const seq = await project.activeSequence;

    if (!seq) throw new Error("No active sequence");

    let markerCount = 0;

    // Wrap all marker creation in a single transaction
    await project.executeTransaction(async () => {
      for (let i = 0; i < markers.length; i++) {
        const markerSpec = markers[i];

        try {
          // Create marker at time
          const marker = await seq.markers.createMarker(markerSpec.time_sec);

          // Set properties via actions (async)
          await application.executeAction("setMarkerComment", {
            marker: marker,
            comment: markerSpec.text || `Marker ${i + 1}`
          });

          await application.executeAction("setMarkerColor", {
            marker: marker,
            color: Math.max(0, Math.min(7, markerSpec.color || 4))
          });

          markerCount++;
          console.log(`Marker ${i + 1}: created at ${markerSpec.time_sec}s`);

        } catch (markerError) {
          console.error(`Marker ${i + 1} failed:`, markerError.message);
        }
      }
    }, `Batch create ${markers.length} markers`);

    console.log(`Transaction complete: ${markerCount}/${markers.length} markers created`);
    return markerCount;

  } catch (error) {
    console.error("Error in batch marker creation:", error.message);
    return 0;
  }
}

// ============================================================================
// PATTERN 4: Read all clips from a sequence with metadata
// ============================================================================

async function readSequenceClips(sequence) {
  /**
   * Iterate through all tracks and clips, async property reads
   */

  try {
    const videoTracks = await sequence.videoTracks;
    const audioTracks = await sequence.audioTracks;

    console.log(`Sequence has ${videoTracks.length} video tracks, ${audioTracks.length} audio tracks`);

    const clipsInfo = [];

    // Read video clips
    for (let trackIdx = 0; trackIdx < videoTracks.length; trackIdx++) {
      const track = videoTracks[trackIdx];
      const clips = await track.clips;

      for (let clipIdx = 0; clipIdx < clips.length; clipIdx++) {
        const clip = clips[clipIdx];

        // All property reads are async
        const name = await clip.name;
        const start = await clip.start;
        const duration = await clip.duration;
        const projectItem = await clip.projectItem;
        const projectItemName = projectItem ? await projectItem.name : "N/A";

        clipsInfo.push({
          trackIdx: trackIdx,
          clipIdx: clipIdx,
          name: name,
          startSeconds: start ? start.seconds : 0,
          durationSeconds: duration ? duration.seconds : 0,
          sourceMedia: projectItemName
        });

        console.log(
          `V${trackIdx}.${clipIdx}: "${name}" @ ${start ? start.seconds : 0}s ← ${projectItemName}`
        );
      }
    }

    return clipsInfo;

  } catch (error) {
    console.error("Error reading clips:", error.message);
    return [];
  }
}

// ============================================================================
// PATTERN 5: Conditional async logic (project item exists?)
// ============================================================================

async function checkProjectItemOffline(projectItemName) {
  /**
   * Find a project item by name, check if offline
   */

  try {
    const project = await application.activeProject;
    const allItems = await project.projectItems;

    for (let i = 0; i < allItems.length; i++) {
      const item = allItems[i];
      const itemName = await item.name;

      if (itemName === projectItemName) {
        const isOffline = await item.isOffline;
        return {
          found: true,
          name: itemName,
          offline: isOffline
        };
      }
    }

    return { found: false, name: projectItemName, offline: null };

  } catch (error) {
    console.error("Error checking item:", error.message);
    return { found: false, error: error.message };
  }
}

// ============================================================================
// PATTERN 6: Error recovery and retry logic
// ============================================================================

async function robustSequenceEdit(sequence, editFn, maxRetries = 2) {
  /**
   * Generic retry wrapper for mutation operations
   * Handles transient failures (UI blocking, etc.)
   */

  let lastError;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await editFn(sequence);
    } catch (error) {
      lastError = error;
      console.warn(`Attempt ${attempt + 1} failed:`, error.message);

      // Exponential backoff
      if (attempt < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, 500 * Math.pow(2, attempt)));
      }
    }
  }

  console.error("All retries exhausted:", lastError.message);
  throw lastError;
}

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

// Example: Run getActiveSequenceName on plugin load
getActiveSequenceName().then(name => {
  if (name) {
    console.log("Active sequence:", name);
  }
});

// Example: Batch create markers
const markerSpecs = [
  { time_sec: 1.5, text: "VFX: Explosion", color: 3 },
  { time_sec: 5.0, text: "Grade checkpoint", color: 2 },
  { time_sec: 10.5, text: "Client approved", color: 5 }
];

// batchCreateMarkersInTransaction(markerSpecs);

// Example: Read sequence clips
const seq = application.activeProject
  .then(p => p.activeSequence)
  .then(s => {
    if (s) return readSequenceClips(s);
  });

// Example: Check if media is offline
checkProjectItemOffline("footage.mov").then(result => {
  console.log("Item check:", result);
});

// ============================================================================
// EXPORT for use in UXP panel scripts
// ============================================================================

module.exports = {
  getActiveSequenceName,
  createSequenceFromMediaFiles,
  batchCreateMarkersInTransaction,
  readSequenceClips,
  checkProjectItemOffline,
  robustSequenceEdit
};
