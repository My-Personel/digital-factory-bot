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
