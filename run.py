"""Main: topic -> script -> voice -> video -> (upload).
  python run.py                 # sirf video banao (out/ me), upload nahi
  python run.py --upload        # banao + YouTube par upload
  python run.py --topic "..."   # specific topic
"""
import argparse, json, os, re, datetime
import config, make_script, make_voice, make_video


def read_lines(path):
    """File na hoy to khali list (crash nahi)."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]


def pop_topic():
    lines = read_lines("topics.txt")
    if not lines:                       # queue khali -> Gemini se naye topics
        lines = make_script.suggest_topics(read_lines("done.txt"))
        if not lines:
            raise SystemExit("Naye topics nahi mile - topics.txt me khud daalo.")
        print("Auto topics generated:", len(lines))
    return lines[0], lines[1:]


def mark_done(topic, rest):
    """Topic use ho gaya -> queue update + done.txt me add."""
    with open("topics.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(rest) + ("\n" if rest else ""))
    with open("done.txt", "a", encoding="utf-8") as f:
        f.write(topic + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--publish-at", help="ISO UTC time, e.g. 2026-10-13T12:30:00Z")
    a = ap.parse_args()

    topic, rest = (a.topic, None) if a.topic else pop_topic()
    print("Topic:", topic)
    data = make_script.generate(topic)
    narration = " ".join(s["text"] for s in data["scenes"])
    slug = re.sub(r"\W+", "_", topic.lower())[:40] + datetime.datetime.now().strftime("_%H%M%S")
    os.makedirs("out", exist_ok=True)
    mp3 = f"out/{slug}.mp3"
    words = make_voice.synthesize(narration, mp3)
    mp4 = make_video.build(data["scenes"], words, mp3, f"out/work_{slug}", f"out/{slug}.mp4")
    with open(f"out/{slug}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Video ready:", mp4, "| title:", data["title"])

    if a.upload:
        import upload_youtube
        vid = upload_youtube.upload(mp4, data["title"], data["description"], data["tags"], a.publish_at)
        print("Uploaded: https://youtube.com/shorts/" + vid)
    if rest is not None:
        mark_done(topic, rest)


if __name__ == "__main__":
    main()
