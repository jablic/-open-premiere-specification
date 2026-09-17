from pathlib import Path
import shutil
src = Path(__file__).resolve().parent
dst = Path('/Users/konstantinguryanov/Desktop/APP_AI_MD/Knowledge_OS_PKC_v0_7_0')
dst.parent.mkdir(parents=True, exist_ok=True)
if dst.exists(): shutil.rmtree(dst)
shutil.copytree(src, dst)
print(f'Installed Knowledge OS / PKC to {dst}')
