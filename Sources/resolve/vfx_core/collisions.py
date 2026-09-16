from pathlib import Path

def collision_safe_path(folder: str | Path, stem: str, extension: str, *, existing=(), overwrite=False) -> Path:
    """Return a deterministic non-overwriting path; no filesystem writes occur."""
    root = Path(folder)
    ext = extension if extension.startswith(".") else "." + extension
    candidate = root / f"{stem}{ext}"
    occupied = {Path(p) for p in existing}
    if overwrite or candidate not in occupied:
        return candidate
    index = 2
    while (root / f"{stem}_{index}{ext}") in occupied:
        index += 1
    return root / f"{stem}_{index}{ext}"
