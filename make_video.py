"""Pexels (free) stock clips + ffmpeg se vertical Short banata hai, captions ke saath."""
import os, random, subprocess, requests
import config

def ffprobe_duration(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "default=nw=1:nk=1", path])
    return float(out.strip())

def _run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def pexels_clip(keywords, dest, used):
    headers = {"Authorization": config.PEXELS_API_KEY}
    for kw in keywords + ["factory machine", "industrial"]:
        r = requests.get("https://api.pexels.com/videos/search", headers=headers,
                         params={"query": kw, "orientation": "portrait", "per_page": 8}, timeout=30)
        if r.status_code != 200:
            continue
        vids = [v for v in r.json().get("videos", []) if v["id"] not in used]
        random.shuffle(vids)
        for v in vids:
            files = [f for f in v["video_files"] if f["file_type"] == "video/mp4" and f.get("height", 0) >= 1280]
            if not files:
                continue
            f = min(files, key=lambda x: x["height"])
            with requests.get(f["link"], stream=True, timeout=60) as resp:
                resp.raise_for_status()
                with open(dest, "wb") as out:
                    for part in resp.iter_content(1 << 20):
                        out.write(part)
            used.add(v["id"])
            return True
    return False


def pixabay_clip(keywords, dest, used):
    for kw in keywords + ["factory machine", "industrial"]:
        r = requests.get("https://pixabay.com/api/videos/",
                         params={"key": config.PIXABAY_API_KEY, "q": kw[:90], "per_page": 15,
                                 "safesearch": "true"}, timeout=30)
        if r.status_code != 200:
            continue
        hits = [h for h in r.json().get("hits", []) if h["id"] not in used]
        random.shuffle(hits)
        for h in hits:
            for size in ("large", "medium", "small"):
                v = h["videos"].get(size) or {}
                if v.get("url"):
                    with requests.get(v["url"], stream=True, timeout=90) as resp:
                        resp.raise_for_status()
                        with open(dest, "wb") as out:
                            for part in resp.iter_content(1 << 20):
                                out.write(part)
                    used.add(h["id"])
                    return True
    return False

def local_clip(dest, used):
    """clips/ folder me aapki apni video files (mp4/mov) - random uthata hai."""
    import glob, shutil
    files = [f for f in glob.glob("clips/*") if f.lower().endswith((".mp4", ".mov", ".mkv")) and f not in used]
    if not files:
        return False
    f = random.choice(files)
    used.add(f)
    shutil.copy(f, dest)
    return True

def fallback_clip(dest, dur, color):
    _run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c={color}:s={config.WIDTH}x{config.HEIGHT}:r={config.FPS}",
          "-t", f"{dur:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", dest])

def normalize(src, dest, dur):
    vf = (f"scale={config.WIDTH}:{config.HEIGHT}:force_original_aspect_ratio=increase,"
          f"crop={config.WIDTH}:{config.HEIGHT},fps={config.FPS},setsar=1,format=yuv420p")
    _run(["ffmpeg", "-y", "-stream_loop", "-1", "-i", src, "-t", f"{dur:.2f}", "-an", "-vf", vf,
          "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", dest])

def _ts(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def write_ass(words, scene_texts, total, path, chunk=3):
    """Word timings se 3-3 shabd ke bade captions. Timing na mile to scene text barabar baant do."""
    if not words:
        step = total / max(len(scene_texts), 1)
        words = []
        for i, t in enumerate(scene_texts):
            ws = t.split()
            for j, w in enumerate(ws):
                words.append((w, i * step + j * step / len(ws), i * step + (j + 1) * step / len(ws)))
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {config.WIDTH}
PlayResY: {config.HEIGHT}

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,{config.FONT},84,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,6,2,2,60,60,520,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = []
    for i in range(0, len(words), chunk):
        grp = words[i:i + chunk]
        end = grp[-1][2] if i + chunk >= len(words) else words[i + chunk][1]
        lines.append(f"Dialogue: 0,{_ts(grp[0][1])},{_ts(end)},Default,,0,0,0,,{' '.join(w[0] for w in grp)}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(head + "\n".join(lines) + "\n")

def build(scenes, words, audio, workdir, out_path):
    os.makedirs(workdir, exist_ok=True)
    total = ffprobe_duration(audio)
    weights = [max(len(s["text"]), 1) for s in scenes]
    durs = [total * w / sum(weights) for w in weights]
    used, parts = set(), []
    palette = ["0x0f2027", "0x1b1b2f", "0x2c1810", "0x102a43"]
    for i, (s, d) in enumerate(zip(scenes, durs)):
        raw, norm = f"{workdir}/raw{i}.mp4", f"{workdir}/n{i}.mp4"
        ok = False
        for name, fn, enabled in (
            ("local",   lambda: local_clip(raw, used),                         os.path.isdir("clips")),
            ("pixabay", lambda: pixabay_clip(s.get("keywords", []), raw, used), bool(config.PIXABAY_API_KEY)),
            ("pexels",  lambda: pexels_clip(s.get("keywords", []), raw, used),  bool(config.PEXELS_API_KEY)),
        ):
            if ok or not enabled:
                continue
            try:
                ok = bool(fn())
            except Exception as e:
                print(name, "error:", e)
        if not ok:
            fallback_clip(raw, d + 1, palette[i % 4])
        normalize(raw, norm, d)
        parts.append(norm)
    lst = f"{workdir}/list.txt"
    with open(lst, "w") as f:
        f.writelines(f"file '{os.path.abspath(p)}'\n" for p in parts)
    joined = f"{workdir}/joined.mp4"
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    ass = f"{workdir}/subs.ass"
    write_ass(words, [s["text"] for s in scenes], total, ass)
    _run(["ffmpeg", "-y", "-i", joined, "-i", audio, "-vf", f"ass={ass}",
          "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out_path])
    return out_path
