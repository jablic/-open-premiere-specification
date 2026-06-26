#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
for p in [ROOT, Path(__file__).resolve().parents[2] / 'Knowledge_OS_PKC_v0_7_0', Path('/Users/konstantinguryanov/Desktop/APP_AI_MD/Knowledge_OS_PKC_v0_7_0')]:
    if (p/'knowledge_os').exists():
        sys.path.insert(0, str(p)); break
from knowledge_os.cli import main
if __name__ == '__main__': main()
