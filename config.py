import os

# ---- Keys (environment variables se aate hain, code me mat likhna) ----
GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL     = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
PEXELS_API_KEY   = os.getenv("PEXELS_API_KEY", "")     # optional (abhi naye keys band hain)
PIXABAY_API_KEY  = os.getenv("PIXABAY_API_KEY", "")    # free, recommended
YT_CLIENT_ID     = os.getenv("YT_CLIENT_ID", "")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN", "")

# private = safe default (API audit pending ho to YouTube private hi rakhta hai)
YT_PRIVACY = os.getenv("YT_PRIVACY", "private")   # private | unlisted | public

# ---- Voice (free, Microsoft Edge TTS) ----
VOICE = os.getenv("VOICE", "hi-IN-MadhurNeural")  # ya hi-IN-SwaraNeural
RATE  = os.getenv("RATE", "+8%")                  # thoda fast = better retention

# ---- Video ----
WIDTH, HEIGHT, FPS = 1080, 1920, 30
FONT = os.getenv("FONT", "Noto Sans Devanagari")
CHANNEL_NAME = "Digital Factory"

# Aapke best videos (data se) - Gemini ko style samjhane ke liye
WINNING_TITLES = [
    "LPG Cylinder में Gas कैसे भरी जाती है? 😳 | LPG Factory",
    "Cylinder नहीं, Pipe से Gas! PNG System कैसे काम करता है?",
    "आपकी बाइक का पेट्रोल… 30 करोड़ साल पुराना है!",
    "India Me LNG Gas Kahan Se Aati Hai? 😱",
    "🥈 Silver (चांदी) Factory में कैसे बनती है?",
]
