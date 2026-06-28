#!/usr/bin/env python3
"""
parse_premiere_fcpxml.py
---------------------------------------------------------------------------
Runtime : Python 3.8+  (standard library only)
Status  : interop, current. See Knowledge/xml-fcpxml.md
Topic   : Knowledge/xml-fcpxml.md

WHAT IT DOES
  Parses an Adobe Premiere Pro "Final Cut Pro 7 XML" (xmeml) export and extracts:
    1. Markers  (sequence-level and clip-level): name, comment, frame in/out, timecode.
    2. A best-effort pass at Essential Graphics / title TEXT, which Premiere often stores as
       Base64 inside <data>/<value> nodes within nested <filter>/<effect> elements.

CAVEAT (important)
  Adobe staff have noted that Essential Graphics text is frequently UNRECOVERABLE once flattened to
  FCPXML. Treat the text extraction as best-effort; for reliable text, round-trip the live scripting
  API instead (see Knowledge/essential-graphics-mogrt-text.md).

USAGE
  python3 parse_premiere_fcpxml.py export.xml > out.json
---------------------------------------------------------------------------
"""

import sys
import re
import json
import base64
import xml.etree.ElementTree as ET


def first_timebase(root: ET.Element) -> int:
    """Return the first sequence <rate><timebase> (fps) found, default 25."""
    for rate in root.iter("rate"):
        tb = rate.findtext("timebase")
        if tb and tb.strip().isdigit():
            return int(tb.strip())
    # Fallback: a bare <timebase> somewhere.
    tb = root.findtext(".//timebase")
    return int(tb) if (tb and tb.strip().isdigit()) else 25


def frames_to_tc(frames, fps: int) -> str:
    """Non-drop HH:MM:SS:FF. frames may be None/'-1' (open-ended)."""
    try:
        f = int(frames)
    except (TypeError, ValueError):
        return ""
    if f < 0:
        return ""
    s, ff = divmod(f, fps)
    h, rem = divmod(s, 3600)
    m, ss = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{ss:02d}:{ff:02d}"


def extract_markers(root: ET.Element, fps: int):
    markers = []
    for m in root.iter("marker"):
        name = (m.findtext("name") or "").strip()
        comment = (m.findtext("comment") or "").strip()
        m_in = m.findtext("in")
        m_out = m.findtext("out")
        markers.append({
            "name": name,
            "comment": comment,
            "in_frames": m_in,
            "out_frames": m_out,
            "timecode_in": frames_to_tc(m_in, fps),
            "timecode_out": frames_to_tc(m_out, fps),
        })
    return markers


_PRINTABLE = re.compile(r"[ -~\u00a0-\uffff]{3,}")  # runs of >=3 printable/unicode chars


def _try_base64_text(blob: str):
    """Attempt to decode a Base64 blob and pull readable strings out of it."""
    cleaned = re.sub(r"\s+", "", blob)
    if len(cleaned) < 8:
        return []
    # Base64 alphabet check (allow padding).
    if not re.fullmatch(r"[A-Za-z0-9+/=]+", cleaned):
        return []
    try:
        raw = base64.b64decode(cleaned, validate=False)
    except Exception:
        return []
    # Decode permissively; Essential Graphics payloads are often UTF-8/UTF-16 fragments.
    for enc in ("utf-8", "utf-16-le", "latin-1"):
        try:
            text = raw.decode(enc, errors="ignore")
        except Exception:
            continue
        hits = [h.strip() for h in _PRINTABLE.findall(text)]
        # Filter obvious noise: keep tokens with letters, drop pure-symbol/hex runs.
        hits = [h for h in hits if re.search(r"[A-Za-z\u00c0-\uffff]", h) and not re.fullmatch(r"[0-9a-fA-F]+", h)]
        if hits:
            return hits
    return []


def extract_text_elements(root: ET.Element):
    """
    Best-effort: scan clip/generator items for filters/effects whose name hints at graphics/text,
    then mine their parameter <data>/<value> nodes for Base64-embedded strings.
    """
    out = []
    hint = re.compile(r"(graphic|text|title|livetype|live text|mogrt)", re.IGNORECASE)

    for item in list(root.iter("clipitem")) + list(root.iter("generatoritem")):
        item_name = (item.findtext("name") or "").strip()
        for fx in list(item.iter("filter")) + list(item.iter("effect")):
            fx_name = (fx.findtext("name") or fx.findtext("effectid") or "")
            instance = (fx.findtext("instancename") or "")
            if not (hint.search(fx_name) or hint.search(instance) or hint.search(item_name)):
                continue
            found = []
            # Candidate payload nodes.
            for tag in ("data", "value"):
                for node in fx.iter(tag):
                    if node.text and len(node.text.strip()) >= 8:
                        found.extend(_try_base64_text(node.text))
            # De-dup, keep order.
            seen, uniq = set(), []
            for t in found:
                if t not in seen:
                    seen.add(t)
                    uniq.append(t)
            if uniq:
                out.append({
                    "clip": item_name,
                    "effect": fx_name.strip(),
                    "instance": instance.strip(),
                    "text_candidates": uniq,
                })
    return out


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: python3 parse_premiere_fcpxml.py <export.xml>\n")
        sys.exit(2)

    tree = ET.parse(sys.argv[1])
    root = tree.getroot()
    fps = first_timebase(root)

    result = {
        "fps": fps,
        "markers": extract_markers(root, fps),
        "text_elements": extract_text_elements(root),
        "_note": "text_elements is best-effort; EGL text is often unrecoverable from FCPXML "
                 "(see Knowledge/essential-graphics-mogrt-text.md).",
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
