from unittest.mock import patch, MagicMock

from aloud.feed import generate, _slug_to_title, _fmt_duration


def test_slug_to_title():
    assert _slug_to_title("my-great-article") == "My Great Article"
    assert _slug_to_title("stdin-hello-world") == "Stdin Hello World"


def test_fmt_duration_minutes():
    assert _fmt_duration(125.7) == "2:05"


def test_fmt_duration_hours():
    assert _fmt_duration(3661.0) == "1:01:01"


def test_fmt_duration_zero():
    assert _fmt_duration(0) == "0:00"


def test_generate_no_episodes_dir(tmp_path, capsys):
    import pytest

    with pytest.raises(SystemExit):
        generate(tmp_path / "nonexistent", "https://example.com")
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_generate_no_episodes(tmp_path, capsys):
    episodes = tmp_path / "episodes"
    episodes.mkdir()
    generate(tmp_path, "https://example.com")
    captured = capsys.readouterr()
    assert "No episodes found" in captured.err
    assert not (tmp_path / "feed.xml").exists()


def test_generate_missing_ffprobe(tmp_path):
    import pytest

    episodes = tmp_path / "episodes"
    episodes.mkdir()
    (episodes / "2026-03-13-test.mp3").write_bytes(b"\x00" * 100)
    with patch("aloud.feed.shutil.which", return_value=None):
        with pytest.raises(SystemExit):
            generate(tmp_path, "https://example.com")


def test_generate_creates_feed_xml(tmp_path):
    episodes = tmp_path / "episodes"
    episodes.mkdir()
    mp3 = episodes / "2026-03-13-test-episode.mp3"
    mp3.write_bytes(b"\x00" * 1000)

    mock_result = MagicMock()
    mock_result.stdout = "60.5"
    mock_result.returncode = 0

    with patch("aloud.feed.subprocess.run", return_value=mock_result):
        generate(tmp_path, "https://example.com")

    feed = tmp_path / "feed.xml"
    assert feed.exists()
    content = feed.read_text()
    assert '<?xml version="1.0" encoding="UTF-8"?>' in content
    assert "<title>Read Aloud</title>" in content
    assert "<title>Test Episode</title>" in content
    assert 'url="https://example.com/episodes/2026-03-13-test-episode.mp3"' in content
    assert "length=" in content
    assert "<itunes:duration>1:00</itunes:duration>" in content


def test_generate_orders_newest_first(tmp_path):
    episodes = tmp_path / "episodes"
    episodes.mkdir()
    (episodes / "2026-03-01-old.mp3").write_bytes(b"\x00" * 100)
    (episodes / "2026-03-13-new.mp3").write_bytes(b"\x00" * 100)

    mock_result = MagicMock()
    mock_result.stdout = "30.0"
    mock_result.returncode = 0

    with patch("aloud.feed.subprocess.run", return_value=mock_result):
        generate(tmp_path, "https://example.com")

    content = (tmp_path / "feed.xml").read_text()
    pos_new = content.index("new")
    pos_old = content.index("old")
    assert pos_new < pos_old
