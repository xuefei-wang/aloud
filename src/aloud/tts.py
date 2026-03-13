"""Text-to-speech synthesis via edge-tts."""

import asyncio
import tempfile
from pathlib import Path

import edge_tts


def synthesize(text: str, speed: str, voice: str) -> Path:
    if not text.strip():
        raise ValueError("empty input")
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", prefix="aloud-", delete=False)
    tmp.close()
    out = Path(tmp.name)
    comm = edge_tts.Communicate(text, voice=voice, rate=speed)
    try:
        asyncio.run(comm.save(str(out)))
    except Exception:
        out.unlink(missing_ok=True)
        raise
    return out
