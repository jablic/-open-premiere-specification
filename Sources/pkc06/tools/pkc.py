#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PKC_ROOT = Path(__file__).resolve().parents[2] / 'Knowledge_OS_PKC_v0_6_0'
# fallback for copied standalone repo: use local vendor if present, otherwise parent builder install
for p in [ROOT, PKC_ROOT, Path('/Users/konstantinguryanov/Desktop/APP_AI_MD/Knowledge_OS_PKC_v0_6_0')]:
    if (p/'knowledge_os').exists(): sys.path.insert(0, str(p)); break
from knowledge_os.cli import main
if __name__ == '__main__': main()
