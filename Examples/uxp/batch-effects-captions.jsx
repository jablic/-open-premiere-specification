/**
 * UXP Plugin: Batch Apply Effects & Captions
 */
const { application } = require("premierepro");

(async () => {
  try {
    const proj = await application.activeProject;
    const seq = await proj.activeSequence;
    
    if (!seq) {
      console.error("No active sequence");
      return;
    }
    
    await application.executeTransaction(async () => {
      const videoTracks = await seq.videoTracks;
      const track = videoTracks[0];
      const clips = await track.clips;
      
      for (let i = 0; i < clips.length; i++) {
        const clip = clips[i];
        const clipName = await clip.name;
        
        try {
          const effect = await clip.createComponent("Lumetri Color");
          console.log("Applied effect to: " + clipName);
        } catch (err) {
          console.log("Could not apply effect to: " + clipName);
        }
      }
    });
    
    console.log("Batch operation complete");
  } catch (error) {
    console.error("Error:", error.message);
  }
})();
