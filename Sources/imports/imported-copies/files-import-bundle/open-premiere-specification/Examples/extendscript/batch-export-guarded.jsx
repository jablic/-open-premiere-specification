/**
 * batch-export-guarded.jsx
 * ---------------------------------------------------------------------------
 * Runtime : ExtendScript (ES3) — Adobe Premiere Pro 14.x+
 * Status  : legacy/frozen (ExtendScript EOL 2026-09). See Knowledge/00-technology-status-matrix.md
 * Topic   : Knowledge/export-rendering-media-encoder.md
 *
 * WHAT IT DOES
 *   Queues every sequence in the open project to Adobe Media Encoder using a given .epr preset.
 *   - Verifies AME is installed before queueing.
 *   - GUARDS against HEVC/H.265 presets, which are programmatically BLOCKED since Premiere 25.5
 *     (encodeSequence returns a non-zero job id but queues nothing, and throws no error).
 *
 * USAGE
 *   Edit OUTPUT_DIR and EPR_PATH below, then run. Use an H.264 preset (HEVC will be refused).
 * ---------------------------------------------------------------------------
 */

(function () {

    // ======= EDIT THESE =======
    var OUTPUT_DIR = Folder.desktop.fsName + "/ppro_exports";
    var EPR_PATH   = "/path/to/H264-1080p.epr";   // absolute path to an H.264 preset
    // ==========================

    function ameAvailable() {
        try {
            var status = BridgeTalk.getStatus("ame");   // "ISNOTINSTALLED" | "ISNOTRUNNING" | running
            if (status === "ISNOTINSTALLED") {
                return { ok: false, err: "Adobe Media Encoder is not installed." };
            }
            return { ok: true, status: String(status) };
        } catch (e) {
            return { ok: false, err: String(e) };
        }
    }

    // Heuristic HEVC detection: filename first, then scan the .epr XML.
    function isLikelyHevcPreset(eprPath) {
        var f = new File(eprPath);
        if (!f.exists) { return false; }
        var name = decodeURI(f.name).toLowerCase();
        if (name.indexOf("hevc") !== -1 || name.indexOf("h265") !== -1 || name.indexOf("h.265") !== -1) {
            return true;
        }
        if (f.open("r")) {
            var s = f.read().toLowerCase();
            f.close();
            return s.indexOf("hevc") !== -1;
        }
        return false;
    }

    function hevcIsBlocked() {
        var parts = app.version.split(".");
        var major = parseInt(parts[0], 10);
        var minor = parseInt(parts[1] || "0", 10);
        return (major > 25) || (major === 25 && minor >= 5);
    }

    function ensureDir(path) {
        var fo = new Folder(path);
        if (!fo.exists) { fo.create(); }
        return fo.exists;
    }

    function run() {
        if (!app.project) { $.writeln("No project open."); return; }

        var ame = ameAvailable();
        if (!ame.ok) { $.writeln("ABORT: " + ame.err); return; }

        var f = new File(EPR_PATH);
        if (!f.exists) { $.writeln("ABORT: preset not found: " + EPR_PATH); return; }

        if (hevcIsBlocked() && isLikelyHevcPreset(EPR_PATH)) {
            $.writeln("ABORT: HEVC/H.265 programmatic export is blocked on Premiere 25.5+. " +
                      "Use an H.264 preset, or render HEVC manually in AME.");
            return;
        }

        if (!ensureDir(OUTPUT_DIR)) { $.writeln("ABORT: cannot create output dir: " + OUTPUT_DIR); return; }

        app.encoder.launchEncoder();

        var seqs = app.project.sequences;     // SequenceCollection (.numSequences)
        var queued = 0, failed = 0;
        for (var i = 0; i < seqs.numSequences; i++) {
            app.project.openSequence(seqs[i].sequenceID);
            var active = app.project.activeSequence;
            var safe = active.name.replace(/[^\w\-]+/g, "_");
            var ext = active.getExportFileExtension(EPR_PATH);   // e.g. ".mp4"
            var outPath = OUTPUT_DIR + "/" + safe + ext;

            var jobID = app.encoder.encodeSequence(active, outPath, EPR_PATH, app.encoder.ENCODE_ENTIRE, 1);
            if (jobID === 0 || jobID === "0" || !jobID) {
                failed++;
                $.writeln("QUEUE FAIL: " + active.name);
            } else {
                queued++;
                $.writeln("QUEUED [" + jobID + "]: " + active.name + " -> " + outPath);
            }
        }

        if (queued > 0) { app.encoder.startBatch(); }
        $.writeln("Summary: queued=" + queued + " failed=" + failed);
    }

    run();
})();
