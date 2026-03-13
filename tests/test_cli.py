from unittest.mock import patch, MagicMock
from pathlib import Path

from aloud.cli import main, _resolve_input


def test_resolve_input_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello world")
    text, source = _resolve_input(file=str(f), clipboard=False, stdin_data=None)
    assert text == "hello world"
    assert source == str(f)


def test_resolve_input_clipboard():
    with (
        patch("aloud.cli.shutil.which", return_value="/usr/bin/xclip"),
        patch("aloud.cli.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(stdout="clipboard text", returncode=0)
        text, source = _resolve_input(file=None, clipboard=True, stdin_data=None)
        assert text == "clipboard text"
        assert source == "__clipboard__"


def test_resolve_input_stdin():
    text, source = _resolve_input(file=None, clipboard=False, stdin_data="stdin text")
    assert text == "stdin text"
    assert source is None


def test_resolve_input_empty_raises():
    import pytest

    with pytest.raises(SystemExit):
        _resolve_input(file=None, clipboard=False, stdin_data="")


def test_resolve_input_file_not_found():
    import pytest

    with pytest.raises(SystemExit):
        _resolve_input(file="/nonexistent/file.txt", clipboard=False, stdin_data=None)


def test_main_playback_mode(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello world")

    with (
        patch(
            "aloud.cli.tts.synthesize", return_value=Path("/tmp/fake.mp3")
        ) as mock_synth,
        patch("aloud.cli.player.play") as mock_play,
        patch("sys.argv", ["aloud", str(f)]),
    ):
        main()
        mock_synth.assert_called_once()
        mock_play.assert_called_once_with(Path("/tmp/fake.mp3"))


def test_main_publish_mode(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello world")

    with (
        patch(
            "aloud.cli.tts.synthesize", return_value=Path("/tmp/fake.mp3")
        ) as mock_synth,
        patch("aloud.cli.publish_module.publish") as mock_pub,
        patch(
            "aloud.cli.config.load_config",
            return_value={
                "feed_dir": "/tmp",
                "feed_url": "https://x.com",
                "speed": "+20%",
                "voice": "en-US-AndrewMultilingualNeural",
            },
        ),
        patch("sys.argv", ["aloud", "-o", str(f)]),
    ):
        main()
        mock_synth.assert_called_once()
        mock_pub.assert_called_once()


def test_main_publish_no_config(capsys):
    import pytest

    with (
        patch("aloud.cli.config.load_config", return_value={}),
        patch("sys.argv", ["aloud", "-o", "file.txt"]),
    ):
        with pytest.raises(SystemExit):
            main()
    captured = capsys.readouterr()
    assert "aloud config" in captured.err


def test_main_feed_subcommand():
    with (
        patch(
            "aloud.cli.config.load_config",
            return_value={"feed_dir": "/tmp/feed", "feed_url": "https://example.com"},
        ),
        patch("aloud.cli.feed_module.generate") as mock_gen,
        patch("aloud.cli.git_commit_and_push") as mock_git,
        patch("sys.argv", ["aloud", "feed"]),
    ):
        main()
        mock_gen.assert_called_once()
        mock_git.assert_called_once()


def test_main_config_subcommand():
    with (
        patch("aloud.cli.config.run_config_wizard") as mock_wizard,
        patch("sys.argv", ["aloud", "config"]),
    ):
        main()
        mock_wizard.assert_called_once()
