"""edge-tts (free) se Hindi voice + word timings (captions ke liye)."""
import asyncio, edge_tts
import config

async def _run(text, mp3_path):
    com = edge_tts.Communicate(text, config.VOICE, rate=config.RATE, boundary="WordBoundary")
    words = []
    with open(mp3_path, "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 1e7           # 100ns -> sec
                words.append((chunk["text"], start, start + chunk["duration"] / 1e7))
    return words

def synthesize(text: str, mp3_path: str):
    return asyncio.run(_run(text, mp3_path))
