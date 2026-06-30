#!/usr/bin/env python3
"""
Parse Premiere FCP7 XML Export
Extracts clips, markers, timing
"""

import xml.etree.ElementTree as ET
import base64
import json
from pathlib import Path

TICKS_PER_SECOND = 254016000000

def ticks_to_seconds(ticks):
    return ticks / TICKS_PER_SECOND

def seconds_to_timecode(seconds, fps=30):
    frames = int(seconds * fps)
    hours = frames // (fps * 3600)
    minutes = (frames % (fps * 3600)) // (fps * 60)
    secs = (frames % (fps * 60)) // fps
    frame = frames % fps
    return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frame:02d}"

def parse_fcp7_xml(filepath):
    """Parse FCP7 XML file"""
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    sequences = []
    for seq in root.findall('.//sequence'):
        seq_data = {
            'name': seq.findtext('name', 'Untitled'),
            'timebase': int(seq.findtext('timebase', '30')),
            'clips': [],
            'markers': []
        }
        
        for clipitem in seq.findall('.//clipitem'):
            clip = {
                'name': clipitem.findtext('name'),
                'duration': int(clipitem.findtext('duration', '0')),
                'in': int(clipitem.findtext('in', '0')),
                'out': int(clipitem.findtext('out', '0'))
            }
            seq_data['clips'].append(clip)
        
        for marker in seq.findall('.//marker'):
            marker_data = {
                'name': marker.findtext('name'),
                'in': int(marker.findtext('in', '0')),
                'comment': marker.findtext('comment', '')
            }
            try:
                decoded = base64.b64decode(marker_data['comment']).decode('utf-8')
                marker_data['data'] = decoded
            except:
                pass
            seq_data['markers'].append(marker_data)
        
        sequences.append(seq_data)
    
    return sequences

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 parse_premiere_fcpxml.py <file.xml>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    result = parse_fcp7_xml(filepath)
    
    for seq in result:
        print(f"Sequence: {seq['name']}")
        print(f"  Timebase: {seq['timebase']} fps")
        print(f"  Clips: {len(seq['clips'])}")
        print(f"  Markers: {len(seq['markers'])}")
        print()
        
        for clip in seq['clips'][:3]:
            duration = clip['duration'] / TICKS_PER_SECOND
            timecode = seconds_to_timecode(duration, seq['timebase'])
            print(f"    - {clip['name']}: {timecode}")
        
        for marker in seq['markers'][:3]:
            marker_time = marker['in'] / TICKS_PER_SECOND
            marker_tc = seconds_to_timecode(marker_time, seq['timebase'])
            print(f"    [MARKER] {marker['name']} @ {marker_tc}")
