/**
 * UXP Plugin: List Sequences
 */
const { application } = require("premierepro");

(async () => {
  try {
    const project = await application.activeProject;
    if (!project) {
      console.error("No active project");
      process.exit(1);
    }
    
    const projectName = await project.name;
    console.log("\n=== Project: " + projectName + " ===\n");
    
    const sequences = await project.sequences;
    const sequenceCount = sequences.length;
    console.log("Total sequences: " + sequenceCount + "\n");
    
    for (let i = 0; i < sequenceCount; i++) {
      const sequence = sequences[i];
      const name = await sequence.name;
      const duration = await sequence.duration;
      const frameRate = await sequence.frameRate;
      const durationSeconds = await duration.seconds;
      const videoTracks = await sequence.videoTracks;
      const audioTracks = await sequence.audioTracks;
      
      console.log("[" + (i + 1) + "] " + name);
      console.log("    Duration: " + durationSeconds.toFixed(2) + " seconds");
      console.log("    Frame rate: " + frameRate + " fps");
      console.log("    Video tracks: " + videoTracks.length);
      console.log("    Audio tracks: " + audioTracks.length);
      console.log("");
    }
    
    console.log("=== Done ===\n");
  } catch (error) {
    console.error("Error:", error.message);
    process.exit(1);
  }
})();
