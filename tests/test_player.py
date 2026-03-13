from pathlib import Path
from unittest.mock import patch, MagicMock

from aloud.player import play


def test_play_calls_mpv(tmp_path):
    mp3 = tmp_path / "test.mp3"
    mp3.write_bytes(b"fake mp3")
    with patch("aloud.player.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        play(mp3)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "mpv"
        assert str(mp3) in args


def test_play_deletes_temp_file(tmp_path):
    mp3 = tmp_path / "test.mp3"
    mp3.write_bytes(b"fake mp3")
    with patch("aloud.player.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        play(mp3)
        assert not mp3.exists()


def test_play_missing_mpv():
    import pytest

    with (
        patch("aloud.player.shutil.which", return_value=None),
    ):
        with pytest.raises(SystemExit):
            play(Path("/tmp/fake.mp3"))
