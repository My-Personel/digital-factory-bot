# Digital Factory Bot (100% free)

Roz ek Hindi Short apne aap: topic -> Gemini script -> Hindi voice -> Pexels visuals -> captions -> YouTube upload.

## Setup (ek baar, ~20 min)
1. Free keys lo:
   - GEMINI_API_KEY: aistudio.google.com/apikey
   - PIXABAY_API_KEY: pixabay.com (free signup) -> pixabay.com/api/docs/ par key dikhti hai
   (Pexels abhi naye keys nahi de raha; optional hai)
2. YouTube upload ke liye: console.cloud.google.com -> naya project -> "YouTube Data API v3" enable -> OAuth client (Desktop app) -> client_secret.json download.
   Laptop par: `pip install -r requirements.txt && python get_refresh_token.py client_secret.json`
   Jo 3 values aayein wo save karo.
3. GitHub par private repo banao, ye folder push karo.
   Settings -> Secrets and variables -> Actions: GEMINI_API_KEY, PEXELS_API_KEY, YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
4. Actions tab -> "Daily Short" -> Run workflow (test). Baad me roz 5 PM IST khud chalega.

## Local test (upload ke bina)
    export GEMINI_API_KEY=... PEXELS_API_KEY=...
    sudo apt install ffmpeg fonts-noto-core
    python run.py --topic "CNG gas car me kaise bhari jaati hai"
Video `out/` folder me milega. Pehle 5-10 video dekh kar quality check karo.

## Zaroori baatein
- YT_PRIVACY default `private` hai. Naye API project ke uploads YouTube private hi rakh sakta hai jab tak API audit pass na ho.
  Agar private me atke: video Actions artifact se download karke Studio me schedule karo, ya audit form bharo.
- topics.txt me naye topics daalte raho (har line ek topic). Gas/fuel/energy/factory wale topics aapke data me best chale.
- Policy: har video me apna angle, sahi facts aur strong hook rakho. Bilkul same template ke mass videos demonetize ho sakte hain.

- Apni clips: `clips/` folder banao aur usme mp4 files daalo. Bot pehle unhe use karta hai, phir Pixabay.
