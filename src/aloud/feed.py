"""Podcast RSS feed generation."""

import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path


def _check_ffprobe():
    if not shutil.which("ffprobe"):
        print(
            "error: ffprobe not found. Install with: sudo apt install ffmpeg",
            file=sys.stderr,
        )
        sys.exit(1)


def _slug_to_title(slug: str) -> str:
    return slug.replace("-", " ").title()


def _fmt_duration(seconds: float) -> str:
    total = int(seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _get_duration(mp3_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(mp3_path),
        ],
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def _to_rfc2822(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return format_datetime(dt)


def generate(feed_dir: Path, feed_url: str) -> None:
    episodes_dir = feed_dir / "episodes"
    if not episodes_dir.is_dir():
        print(f"error: {episodes_dir} not found", file=sys.stderr)
        print(f"hint: create it with: mkdir -p {episodes_dir}", file=sys.stderr)
        sys.exit(1)

    mp3s = sorted(episodes_dir.glob("*.mp3"), reverse=True)

    if not mp3s:
        print(f"No episodes found in {episodes_dir}", file=sys.stderr)
        return

    _check_ffprobe()
    print(f"Building feed.xml ({len(mp3s)} episodes)...", file=sys.stderr)

    items = []
    for mp3 in mp3s:
        name = mp3.stem
        date_str = name[:10]
        slug = name[11:]
        title = _slug_to_title(slug)
        duration = _fmt_duration(_get_duration(mp3))
        fsize = os.path.getsize(mp3)
        pub_date = _to_rfc2822(date_str)

        items.append(
            f"    <item>\n"
            f"      <title>{title}</title>\n"
            f'      <enclosure url="{feed_url}/episodes/{mp3.name}" length="{fsize}" type="audio/mpeg"/>\n'
            f"      <guid>{feed_url}/episodes/{mp3.name}</guid>\n"
            f"      <pubDate>{pub_date}</pubDate>\n"
            f"      <itunes:duration>{duration}</itunes:duration>\n"
            f"    </item>"
        )

    feed_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"\n'
        '     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"\n'
        '     xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        "    <title>Read Aloud</title>\n"
        "    <description>Personal TTS podcast feed</description>\n"
        "    <language>en</language>\n"
        f'    <atom:link href="{feed_url}/feed.xml" rel="self" type="application/rss+xml"/>\n'
        + "\n".join(items)
        + "\n"
        "  </channel>\n"
        "</rss>\n"
    )

    (feed_dir / "feed.xml").write_text(feed_xml)
    print("Wrote feed.xml", file=sys.stderr)
