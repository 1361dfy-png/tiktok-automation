"""
Uploads output/final.mp4 to TikTok using the Content Posting API (direct post).

BEFORE THIS WORKS YOU NEED:
1. A TikTok developer app with the "Content Posting API" product added,
   approved for the scopes you need (video.publish).
2. A user access token with that scope, refreshed as needed, stored as the
   TIKTOK_ACCESS_TOKEN secret in your repo.

TikTok's API fields and endpoints do change over time — before relying on
this in production, cross-check the request body (especially the exact key
used to flag AI-generated content for TikTok's disclosure requirement)
against the current docs at:
https://developers.tiktok.com/doc/content-posting-api-reference-direct-post
"""

import os
import time
import requests

ACCESS_TOKEN = os.environ["TIKTOK_ACCESS_TOKEN"]
VIDEO_PATH = "output/final.mp4"

INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"

# TODO: rotate/randomize per post
CAPTION = "Auto-generated ambient loop 🎧 #ambient #lofi"


def init_upload(video_size: int) -> dict:
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    body = {
        "post_info": {
            "title": CAPTION,
            "privacy_level": "SELF_ONLY",  # switch to PUBLIC_TO_EVERYONE once you've tested end to end
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
            # NOTE: verify the current field name TikTok expects for AI-generated
            # content disclosure — this is required by their platform policy.
            "is_aigc": True,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": video_size,   # single chunk; fine for short vertical clips
            "total_chunk_count": 1,
        },
    }
    resp = requests.post(INIT_URL, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()["data"]


def upload_video(upload_url: str, video_size: int):
    with open(VIDEO_PATH, "rb") as f:
        video_bytes = f.read()

    headers = {
        "Content-Range": f"bytes 0-{video_size - 1}/{video_size}",
        "Content-Type": "video/mp4",
    }
    resp = requests.put(upload_url, headers=headers, data=video_bytes, timeout=120)
    resp.raise_for_status()


def poll_status(publish_id: str, attempts: int = 10, delay_seconds: int = 15):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    for _ in range(attempts):
        resp = requests.post(STATUS_URL, headers=headers, json={"publish_id": publish_id}, timeout=30)
        resp.raise_for_status()
        status = resp.json()["data"]["status"]
        print(f"Publish status: {status}")
        if status in ("PUBLISH_COMPLETE", "FAILED"):
            return status
        time.sleep(delay_seconds)
    return "TIMED_OUT"


def main():
    video_size = os.path.getsize(VIDEO_PATH)

    data = init_upload(video_size)
    publish_id = data["publish_id"]
    upload_url = data["upload_url"]

    upload_video(upload_url, video_size)
    final_status = poll_status(publish_id)

    print(f"Done. publish_id={publish_id} final_status={final_status}")


if __name__ == "__main__":
    main()
