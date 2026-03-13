import os
from unittest.mock import patch

from aloud.config import load_config, save_config, run_config_wizard, DEFAULTS


def test_load_config_missing(tmp_path):
    path = str(tmp_path / "config.json")
    with patch("aloud.config.CONFIG_PATH", path):
        assert load_config() == {}


def test_save_and_load_config(tmp_path):
    path = str(tmp_path / "config.json")
    with patch("aloud.config.CONFIG_PATH", path):
        save_config({"feed_dir": "/tmp/feed"})
        cfg = load_config()
        assert cfg["feed_dir"] == "/tmp/feed"


def test_save_config_creates_dir(tmp_path):
    path = str(tmp_path / "subdir" / "config.json")
    with patch("aloud.config.CONFIG_PATH", path):
        save_config({"speed": "+30%"})
        assert os.path.exists(path)


def test_wizard_defaults(tmp_path):
    path = str(tmp_path / "config.json")
    with (
        patch("aloud.config.CONFIG_PATH", path),
        patch("builtins.input", side_effect=["", "", ""]),
    ):
        run_config_wizard()
        cfg = load_config()
        assert "feed_dir" not in cfg
        assert "feed_url" not in cfg
        assert cfg["speed"] == DEFAULTS["speed"]


def test_wizard_custom_values(tmp_path):
    path = str(tmp_path / "config.json")
    with (
        patch("aloud.config.CONFIG_PATH", path),
        patch(
            "builtins.input",
            side_effect=["/tmp/my-feed", "https://example.com/feed", "+50%"],
        ),
    ):
        run_config_wizard()
        cfg = load_config()
        assert cfg["feed_dir"] == "/tmp/my-feed"
        assert cfg["feed_url"] == "https://example.com/feed"
        assert cfg["speed"] == "+50%"


def test_load_config_corrupt_json(tmp_path):
    path = str(tmp_path / "config.json")
    with open(path, "w") as f:
        f.write("not json")
    with patch("aloud.config.CONFIG_PATH", path):
        assert load_config() == {}
