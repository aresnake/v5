import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
ADDON_DIR = ROOT / "ares"

EXCLUDES = {
    "__pycache__",
    ".git",
    ".github",
    "dist",
    "venv",
    ".venv",
    ".mypy_cache",
    "tests",
    "scripts",
    "dev",
    ".idea",
    ".vscode",
}


def git_short_sha():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "nogit"


def should_include(p: Path) -> bool:
    parts = set(p.parts)
    return not any(x in parts for x in EXCLUDES)


def main():
    assert ADDON_DIR.exists(), f"Missing {ADDON_DIR}"
    OUT.mkdir(parents=True, exist_ok=True)
    name = f"blade-v5-{git_short_sha()}-{datetime.utcnow().strftime('%Y%m%d')}.zip"
    zpath = OUT / name
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for fp in ADDON_DIR.rglob("*"):
            if fp.is_dir():
                continue
            rel = fp.relative_to(ROOT)
            if should_include(rel):
                z.write(fp, arcname=str(rel))
    print(f"[BUILD] wrote {zpath}")


if __name__ == "__main__":
    main()
