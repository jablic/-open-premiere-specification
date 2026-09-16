from pathlib import Path
import shutil

src = Path(__file__).resolve().parent
dst = Path('/Users/konstantinguryanov/Desktop/APP_AI_MD/PPAIKB_Builder')
dst.parent.mkdir(parents=True, exist_ok=True)
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '.DS_Store'))
print(f'Installed PPAIKB Builder to {dst}')
