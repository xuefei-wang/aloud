from unittest.mock import patch, MagicMock

from aloud.tts import synthesize


def test_synthesize_returns_mp3_path():
    mock_communicate = MagicMock()
    mock_communicate.save = MagicMock()

    with patch("aloud.tts.edge_tts.Communicate", return_value=mock_communicate):
        with patch("aloud.tts.asyncio.run") as mock_run:
            result = synthesize("hello world", "+20%", "en-US-AndrewMultilingualNeural")
            assert result.suffix == ".mp3"
            mock_run.assert_called_once()


def test_synthesize_passes_voice_and_rate():
    mock_communicate = MagicMock()

    with (
        patch(
            "aloud.tts.edge_tts.Communicate", return_value=mock_communicate
        ) as mock_cls,
        patch("aloud.tts.asyncio.run"),
    ):
        synthesize("test text", "+50%", "en-US-JennyNeural")
        mock_cls.assert_called_once_with(
            "test text", voice="en-US-JennyNeural", rate="+50%"
        )


def test_synthesize_empty_text_raises():
    import pytest

    with pytest.raises(ValueError, match="empty"):
        synthesize("", "+20%", "en-US-AndrewMultilingualNeural")
