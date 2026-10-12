"""YouTube Data API v3 (free quota) se upload."""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import config

def upload(video_path, title, description, tags, publish_at=None):
    creds = Credentials(None, refresh_token=config.YT_REFRESH_TOKEN,
                        token_uri="https://oauth2.googleapis.com/token",
                        client_id=config.YT_CLIENT_ID, client_secret=config.YT_CLIENT_SECRET,
                        scopes=["https://www.googleapis.com/auth/youtube.upload"])
    yt = build("youtube", "v3", credentials=creds)
    status = {"privacyStatus": config.YT_PRIVACY, "selfDeclaredMadeForKids": False}
    if publish_at:                       # ISO8601 UTC, e.g. 2026-10-13T12:30:00Z
        status.update(privacyStatus="private", publishAt=publish_at)
    body = {"snippet": {"title": title[:100], "description": description, "tags": tags[:15],
                        "categoryId": "27", "defaultLanguage": "hi", "defaultAudioLanguage": "hi"},
            "status": status}
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    return resp["id"]
