"""Episode publishing to podcast feed repo."""

import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

from aloud import feed


def _check_git():
    if not shutil.which("git"):
        print(
            "error: git not found. Install with: sudo apt install git", file=sys.stderr
        )
        sys.exit(1)


def git_commit_and_push(feed_dir: Path, message: str, paths: list[str]) -> None:
    _check_git()
    subprocess.run(["git", "add"] + paths, cwd=feed_dir, check=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=feed_dir)
    if result.returncode != 0:
        subprocess.run(["git", "commit", "-m", message], cwd=feed_dir, check=True)
        subprocess.run(["git", "push"], cwd=feed_dir, check=True)
        print("Pushed to remote", file=sys.stderr)
    else:
        print("No changes to commit", file=sys.stderr)


def _sanitize(name: str) -> str:
    name = name.lower().replace(" ", "-").replace("_", "-")
    return re.sub(r"[^a-z0-9-]", "", name)


def _make_episode_name(source: str | None, text: str) -> str:
    today = date.today().isoformat()
    if source == "__clipboard__":
        words = text.split()[:6]
        slug = "clipboard-" + "-".join(words)
        return f"{today}-{_sanitize(slug)}.mp3"
    elif source is None:
        words = text.split()[:6]
        slug = "stdin-" + "-".join(words)
        return f"{today}-{_sanitize(slug)}.mp3"
    else:
        slug = Path(source).stem
        return f"{today}-{_sanitize(slug)}.mp3"


def publish(mp3_path: Path, episode_filename: str, config: dict) -> None:
    feed_dir = Path(config["feed_dir"])
    feed_url = config["feed_url"]
    episodes_dir = feed_dir / "episodes"
    episodes_dir.mkdir(parents=True, exist_ok=True)

    dest = episodes_dir / episode_filename
    shutil.copy2(mp3_path, dest)
    mp3_path.unlink(missing_ok=True)
    print(f"Saved: {dest}", file=sys.stderr)

    feed.generate(feed_dir, feed_url)

    episode_slug = Path(episode_filename).stem
    git_commit_and_push(feed_dir, f"add: {episode_slug}", ["feed.xml", "episodes/"])
