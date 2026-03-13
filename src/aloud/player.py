"""Audio playback via mpv."""

import shutil
import subprocess
import sys
from pathlib import Path


def play(mp3_path: Path) -> None:
    if not shutil.which("mpv"):
        print(
            "error: mpv not found. Install with: sudo apt install mpv", file=sys.stderr
        )
        sys.exit(1)
    try:
        subprocess.run(
            [
                "mpv",
                "--no-video",
                "--term-osd-bar",
                "--msg-level=all=no",
                str(mp3_path),
            ],
            check=False,
        )
    finally:
        mp3_path.unlink(missing_ok=True)
