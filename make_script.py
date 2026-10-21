"""Gemini (free tier) se Hindi Short ka script + metadata banata hai."""
import json, requests
import config

PROMPT = """Tum "{channel}" naam ke Hindi YouTube Shorts channel ke scriptwriter ho.
Topic: {topic}

Rules:
- Total narration 30-38 second ki ho (~80-95 Hindi shabd). Sirf Devanagari Hindi, simple bolchaal wali bhasha.
- Pehla scene HOOK ho: pehle 2 second me hairan karne wala sawal ya fact. "Namaste/Hello doston" bilkul nahi.
- 5 se 7 scenes. Har scene 1-2 chhote vakya. Fast pace, koi fillaar nahi.
- Sirf sahi, verify kiye ja sakne wale facts. Agar number pakka nahi pata to mat likho.
- Aakhri scene me ek chhota sawal/CTA jo comment ya subscribe karwaye.
- Har scene ke liye 2-3 ENGLISH keywords do jo stock video (Pexels) me mil sakein (e.g. "gas cylinder factory", "industrial machine").

Mere channel ke best titles ka style: {titles}

Sirf is JSON me jawab do:
{{
 "title": "<=70 char, Hindi+English mix, ek emoji, 'कैसे' ya sawal wala",
 "description": "2-3 line Hindi description + 5 hashtags (#shorts shaamil)",
 "tags": ["...", "..."],
 "scenes": [{{"text": "...", "keywords": ["...", "..."]}}]
}}"""

def generate(topic: str) -> dict:
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{config.GEMINI_MODEL}:generateContent?key={config.GEMINI_API_KEY}")
    body = {
        "contents": [{"parts": [{"text": PROMPT.format(
            channel=config.CHANNEL_NAME, topic=topic,
            titles=" | ".join(config.WINNING_TITLES))}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.8},
    }
    r = requests.post(url, json=body, timeout=90)
    r.raise_for_status()
    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    data = json.loads(text)
    assert data.get("scenes"), "Gemini ne scenes nahi diye"
    if "#shorts" not in data["description"].lower():
        data["description"] += "\n#shorts"
    return data


TOPIC_PROMPT = """Tum "{channel}" Hindi YouTube Shorts channel ke liye topic researcher ho.
Channel "kaise banta hai / kaise kaam karta hai" (factory, gas, fuel, bijli, machine) type ke Shorts banata hai.
Best chale topics: LPG cylinder filling, PNG gas, petrol kaise bana, LNG, silver factory, cricket ball, battery.
{count} NAYE topics do (Hinglish me, ek line each). Interesting, hairan karne wale, aam aadmi se jude.
Ye topics pehle ho chuke hain, repeat mat karo:
{done}
Sirf JSON array of strings do."""

def suggest_topics(done, count=15):
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{config.GEMINI_MODEL}:generateContent?key={config.GEMINI_API_KEY}")
    body = {"contents": [{"parts": [{"text": TOPIC_PROMPT.format(
                channel=config.CHANNEL_NAME, count=count, done="\n".join(done[-60:]) or "(none)")}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.9}}
    r = requests.post(url, json=body, timeout=90)
    r.raise_for_status()
    items = json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
    done_l = {d.lower() for d in done}
    return [t.strip() for t in items if isinstance(t, str) and t.strip().lower() not in done_l]
