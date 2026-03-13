"""Configuration management for aloud."""

import json
import os

CONFIG_DIR = os.path.join(
    os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
    "aloud",
)
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "feed_dir": "",
    "feed_url": "",
    "speed": "+20%",
    "voice": "en-US-AndrewMultilingualNeural",
}


def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")


def run_config_wizard():
    cfg = load_config()
    print("\naloud configuration\n")

    print("Podcast feed publishing (optional — needed for aloud -o and aloud feed)")
    print("  This should be a local git repo served via GitHub Pages or similar.")
    print("  See: https://github.com/xuefei-wang/aloud#publishing-setup\n")

    current_dir = cfg.get("feed_dir", "")
    prompt_dir = f" [{current_dir}]" if current_dir else ""
    feed_dir = input(f"Feed directory (local git repo path){prompt_dir}: ").strip()

    current_url = cfg.get("feed_url", "")
    prompt_url = f" [{current_url}]" if current_url else ""
    feed_url = input(f"Feed URL (public URL where feed is hosted){prompt_url}: ").strip()

    current_speed = cfg.get("speed", DEFAULTS["speed"])
    speed = input(f"Default speed [{current_speed}]: ").strip()

    if feed_dir:
        cfg["feed_dir"] = feed_dir
    if feed_url:
        cfg["feed_url"] = feed_url
    cfg["speed"] = speed or current_speed
    cfg.setdefault("voice", DEFAULTS["voice"])
    save_config(cfg)
    print(f"\nConfig saved to {CONFIG_PATH}")
