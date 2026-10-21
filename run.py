"""Main: topic -> script -> voice -> video -> (upload).
  python run.py                 # sirf video banao (out/ me), upload nahi
  python run.py --upload        # banao + YouTube par upload
  python run.py --topic "..."   # specific topic
"""
import argparse, json, os, re, datetime
import config, make_script, make_voice, make_video

def pop_topic():
    with open("topics.txt", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    if not lines:                       # queue khali -> Gemini se naye topics
        done = [l.strip() for l in open("done.txt", encoding="utf-8") if l.strip()]
        lines = make_script.suggest_topics(done)
        if not lines:
            raise SystemExit("Naye topics nahi mile - topics.txt me khud daalo.")
        print("Auto topics generated:", len(lines))
    topic, rest = lines[0], lines[1:]
    return topic, rest

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic"); ap.add_argument("--upload", action="store_true")
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
    if rest is not None:                      # topic use ho gaya -> done.txt me
        open("topics.txt", "w", encoding="utf-8").write("\n".join(rest) + ("\n" if rest else ""))
        open("done.txt", "a", encoding="utf-8").write(topic + "\n")

if __name__ == "__main__":
    main()
