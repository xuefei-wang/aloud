from unittest.mock import patch, MagicMock

from aloud.publish import publish, _make_episode_name, _sanitize


def test_sanitize():
    assert _sanitize("My Article") == "my-article"
    assert _sanitize("hello_world") == "hello-world"
    assert _sanitize("Test!@#$File") == "testfile"
    assert _sanitize("UPPER CASE") == "upper-case"


def test_make_episode_name_from_file():
    name = _make_episode_name("article.txt", "The contents of the article here")
    assert name.startswith("20")  # starts with date
    assert "article" in name
    assert name.endswith(".mp3")


def test_make_episode_name_stdin():
    name = _make_episode_name(None, "Hello world this is a test of stdin input")
    assert "stdin-hello-world-this-is" in name


def test_make_episode_name_clipboard():
    name = _make_episode_name("__clipboard__", "Some clipboard text for testing today")
    assert "clipboard-some-clipboard-text-for" in name


def test_publish_copies_file_and_calls_feed(tmp_path):
    feed_dir = tmp_path / "feed"
    mp3 = tmp_path / "input.mp3"
    mp3.write_bytes(b"fake mp3 data")

    config = {"feed_dir": str(feed_dir), "feed_url": "https://example.com"}

    with (
        patch("aloud.publish.feed.generate") as mock_feed,
        patch("aloud.publish.shutil.which", return_value="/usr/bin/git"),
        patch("aloud.publish.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        publish(mp3, "2026-03-13-test-episode.mp3", config)

    episodes = feed_dir / "episodes"
    assert episodes.is_dir()
    episode_files = list(episodes.glob("*.mp3"))
    assert len(episode_files) == 1
    assert "test-episode" in episode_files[0].name
    mock_feed.assert_called_once()


def test_publish_skips_git_when_no_changes(tmp_path):
    feed_dir = tmp_path / "feed"
    mp3 = tmp_path / "input.mp3"
    mp3.write_bytes(b"fake mp3 data")

    config = {"feed_dir": str(feed_dir), "feed_url": "https://example.com"}

    # Simulate git diff --cached --quiet returning 0 (no changes)
    git_commands = []

    def mock_run_side_effect(cmd, **kwargs):
        git_commands.append(cmd)
        result = MagicMock(returncode=0)
        return result

    with (
        patch("aloud.publish.feed.generate"),
        patch("aloud.publish.shutil.which", return_value="/usr/bin/git"),
        patch("aloud.publish.subprocess.run", side_effect=mock_run_side_effect),
    ):
        publish(mp3, "2026-03-13-test-episode.mp3", config)

    # Should have git add and git diff, but NOT git commit or git push
    cmd_names = [c[1] for c in git_commands if c[0] == "git"]
    assert "add" in cmd_names
    assert "diff" in cmd_names
    assert "commit" not in cmd_names
    assert "push" not in cmd_names
