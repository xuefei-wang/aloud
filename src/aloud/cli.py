"""CLI entry point for aloud."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from aloud import tts, player, config
from aloud import publish as publish_module
from aloud import feed as feed_module
from aloud.publish import git_commit_and_push
from aloud.config import DEFAULTS


def _read_clipboard() -> str:
    for cmd in [
        ["pbpaste"],  # macOS
        ["powershell.exe", "-command", "Get-Clipboard"],  # Windows / WSL
        ["xclip", "-selection", "clipboard", "-o"],  # Linux X11
        ["xsel", "--clipboard", "--output"],  # Linux X11
        ["wl-paste"],  # Linux Wayland
    ]:
        if shutil.which(cmd[0]):
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
    print(
        "error: no clipboard tool found. Install xclip, xsel, or wl-clipboard (Linux), "
        "or use pbpaste (macOS)",
        file=sys.stderr,
    )
    sys.exit(1)


def _resolve_input(
    file: str | None, clipboard: bool, stdin_data: str | None
) -> tuple[str, str | None]:
    if clipboard:
        text = _read_clipboard()
        source = "__clipboard__"
    elif file:
        path = Path(file)
        if not path.is_file():
            print(f"error: file not found: {file}", file=sys.stderr)
            sys.exit(1)
        text = path.read_text()
        source = file
    elif stdin_data is not None:
        text = stdin_data
        source = None
    else:
        print("error: no file given and nothing on stdin", file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print("error: empty input", file=sys.stderr)
        sys.exit(1)

    return text, source


def _cmd_feed(args):
    cfg = config.load_config()
    if not cfg.get("feed_dir"):
        print("error: no config found. Run 'aloud config' first", file=sys.stderr)
        sys.exit(1)
    feed_dir = Path(cfg["feed_dir"])
    feed_module.generate(feed_dir, cfg["feed_url"])
    from datetime import date

    git_commit_and_push(
        feed_dir, f"update: {date.today().isoformat()} feed", ["feed.xml", "episodes/"]
    )


def _cmd_config(args):
    config.run_config_wizard()


_SUBCOMMANDS = {"feed", "config"}


def main():
    # Detect subcommand before building the full parser to avoid argparse
    # positional-vs-subparsers ambiguity on Python 3.10.
    raw_args = sys.argv[1:]
    first_positional = next((a for a in raw_args if not a.startswith("-")), None)

    if first_positional in _SUBCOMMANDS:
        sub_parser = argparse.ArgumentParser(prog="aloud")
        sub = sub_parser.add_subparsers(dest="command")
        sub.add_parser("feed", help="Regenerate feed.xml and publish")
        sub.add_parser("config", help="Interactive setup wizard")
        args = sub_parser.parse_args()
        if args.command == "feed":
            return _cmd_feed(args)
        if args.command == "config":
            return _cmd_config(args)

    parser = argparse.ArgumentParser(
        prog="aloud", description="Text-to-speech CLI with podcast feed publishing."
    )
    parser.add_argument("file", nargs="?", help="Input text file")
    parser.add_argument(
        "-c", "--clipboard", action="store_true", help="Read from clipboard"
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store_true",
        help="Publish to podcast feed (no playback)",
    )
    parser.add_argument("-s", "--speed", help="TTS speed (e.g. +20%%, -10%%)")
    parser.add_argument("-v", "--voice", help="TTS voice name")

    args = parser.parse_args()

    # Default TTS action
    cfg = config.load_config()
    speed = args.speed or cfg.get("speed", DEFAULTS["speed"])
    voice = args.voice or cfg.get("voice", DEFAULTS["voice"])

    if args.output:
        if not cfg.get("feed_dir"):
            print("error: no config found. Run 'aloud config' first", file=sys.stderr)
            sys.exit(1)

    # Read stdin if not a TTY and no file/clipboard given
    stdin_data = None
    if not args.file and not args.clipboard and not sys.stdin.isatty():
        stdin_data = sys.stdin.read()

    text, source = _resolve_input(
        file=args.file, clipboard=args.clipboard, stdin_data=stdin_data
    )

    print(f"Generating speech (speed: {speed})...", file=sys.stderr)
    mp3_path = tts.synthesize(text, speed, voice)

    if args.output:
        episode_name = publish_module._make_episode_name(source, text)
        publish_module.publish(mp3_path, episode_name, cfg)
    else:
        print("Playing... (Space=pause, Left/Right=skip 5s, q=quit)", file=sys.stderr)
        player.play(mp3_path)

    return 0
