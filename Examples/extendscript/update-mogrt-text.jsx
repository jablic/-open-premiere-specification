/**
 * update-mogrt-text.jsx
 * ---------------------------------------------------------------------------
 * Runtime : ExtendScript (ES3) — Adobe Premiere Pro 14.x+ (New-World scripting)
 * Status  : legacy/frozen (ExtendScript EOL 2026-09). See Knowledge/00-technology-status-matrix.md
 * Topic   : Knowledge/essential-graphics-mogrt-text.md
 *
 * WHAT IT DOES
 *   Imports an After-Effects-authored .mogrt onto the active sequence (optional), then sets its
 *   Source Text — correctly recalculating fontTextRunLength so styling does not corrupt or blank out.
 *
 * REQUIREMENTS
 *   - json2.js bundled next to this file (ExtendScript ES3 has no native JSON).
 *   - The .mogrt MUST be authored in After Effects with "Allow font/style editing" enabled,
 *     otherwise font/size/style writes silently no-op.
 *
 * WHY fontTextRunLength MATTERS
 *   It tells Premiere how many characters the current style run applies to. If it is stale after a
 *   text change, the text renders blank or only partially styled. It MUST equal [newText.length].
 * ---------------------------------------------------------------------------
 */

//@include "json2.js"

(function () {
    if (typeof JSON === "undefined" || !JSON.parse) {
        alert("json2.js is not loaded. Bundle Crockford's json2.js next to this script.");
        return;
    }

    // ---- helpers ----------------------------------------------------------

    function timeAtSeconds(s) {            // 14.1+ wants Time objects, not raw numbers
        var t = new Time();
        t.seconds = s;
        return t;
    }

    function majorVersion() {
        return parseInt(app.version.split(".")[0], 10);
    }

    // Version-correct RGBA: newer Premiere expects normalized 0..1, older expects 0..255.
    function rgbaForVersion(r255, g255, b255, a255) {
        a255 = (a255 == null) ? 255 : a255;
        if (majorVersion() >= 24) {        // normalized era — verify per project/template
            return [r255 / 255, g255 / 255, b255 / 255, a255 / 255];
        }
        return [r255, g255, b255, a255];
    }

    /**
     * Set the Source Text (and optional font) of a MOGRT TrackItem.
     * @return {{ok:Boolean, err:String}}
     */
    function updateMogrtText(trackItem, newText, opts) {
        opts = opts || {};
        try {
            if (!trackItem) { return { ok: false, err: "No trackItem" }; }

            var comp = trackItem.getMGTComponent ? trackItem.getMGTComponent() : null;
            if (!comp) { return { ok: false, err: "Not an AE-authored MOGRT / no MGT component" }; }

            // Display name varies: "Source Text", "Text", or a custom Essential Property name.
            var param = comp.properties.getParamForDisplayName("Source Text")
                     || comp.properties.getParamForDisplayName("Text");
            if (!param) { return { ok: false, err: "Source Text param not exposed by this MOGRT" }; }

            var raw = param.getValue();
            if (raw == null || raw === "") { return { ok: false, err: "Empty Source Text value" }; }

            var blob;
            try { blob = JSON.parse(raw); }
            catch (e) {
                return { ok: false, err: "Source Text is not JSON (Premiere-authored graphic / Legacy Title?): " + String(e) };
            }

            // --- mutate ---
            blob.textEditValue = String(newText);
            blob.fontTextRunLength = [String(newText).length];     // <-- the mandatory line

            if (opts.fontPostScriptName) {
                blob.fontEditValue = [String(opts.fontPostScriptName)];
            }
            // NOTE: fontSizeEditValue can hard-crash Premiere on some builds. Only set if explicitly asked.
            if (typeof opts.fontSize === "number") {
                blob.fontSizeEditValue = [opts.fontSize];
            }
            if (opts.fillColor255 && opts.fillColor255.length >= 3) {
                var c = opts.fillColor255;
                blob.fillColor = rgbaForVersion(c[0], c[1], c[2], c[3]);
            }

            // --- serialize + apply (true => force panel/UI refresh) ---
            param.setValue(JSON.stringify(blob), true);
            return { ok: true, err: "" };
        } catch (e) {
            return { ok: false, err: String(e) };
        }
    }

    /**
     * Import a .mogrt onto the active sequence, then set its text.
     * @return {{ok:Boolean, err:String}}
     */
    function placeMogrtWithText(mogrtPath, atSeconds, vTrackIndex, text, opts) {
        var seq = app.project && app.project.activeSequence;
        if (!seq) { return { ok: false, err: "No active sequence" }; }

        var f = new File(mogrtPath);
        if (!f.exists) { return { ok: false, err: "MOGRT not found: " + mogrtPath }; }

        var t = timeAtSeconds(atSeconds);
        // Windows path gotcha: importMGT has historically needed normalized separators / absolute paths.
        var item = seq.importMGT(mogrtPath, t.ticks, vTrackIndex, 0);
        if (!item) { return { ok: false, err: "importMGT returned null (bad path / unsupported MOGRT)" }; }

        return updateMogrtText(item, text, opts);
    }

    // ---- DEMO -------------------------------------------------------------
    // Two ways to use it. Comment/uncomment as needed.

    // (A) Update the FIRST clip on video track index 1 (the 2nd track):
    var seq = app.project && app.project.activeSequence;
    if (seq && seq.videoTracks.numTracks > 1 && seq.videoTracks[1].clips.numItems > 0) {
        var clip = seq.videoTracks[1].clips[0];
        var res = updateMogrtText(clip, "Easy to adjust", {
            fontPostScriptName: "Montserrat-Bold",
            fillColor255: [255, 255, 255, 255]
        });
        $.writeln(res.ok ? "OK: text updated" : ("FAIL: " + res.err));
    } else {
        $.writeln("Demo A skipped: need a MOGRT clip on video track index 1.");
    }

    // (B) Import a template and set text (edit the path first):
    // var res2 = placeMogrtWithText("/path/to/lower-third.mogrt", 2.0, 1, "Konstantin", {});
    // $.writeln(res2.ok ? "OK: placed + text set" : ("FAIL: " + res2.err));

})();
