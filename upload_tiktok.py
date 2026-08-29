"""
Uploads output/final.mp4 to TikTok as a DRAFT using the Content Posting API's
"upload to inbox" flow — this is the flow that matches the video.upload
scope (the scope actually available in Sandbox without a separate TikTok
audit). The video lands in the TikTok app's inbox/drafts on the target
account; a human still has to open the TikTok app and tap "Post" to
publish it.

If you later apply for and get approved for the video.publish scope
(Direct Post), swap INIT_URL below for the direct-post endpoint and add
back the "post_info" block with privacy_level, captions, etc. — see
https://developers.tiktok.com/doc/content-posting-api-reference-direct-post

BEFORE THIS WORKS YOU NEED:
1. A TikTok developer app with the "Content Posting API" product added,
   with the video.upload scope enabled.
2. A user access token with that scope, stored as the TIKTOK_ACCESS_TOKEN
   secret in your repo (see get_tiktok_token.py for how to obtain one).

TikTok's API fields and endpoints do change over time — cross-check
against the current docs before relying on this:
https://developers.tiktok.com/doc/content-posting-api-reference-upload-video
"""

import os
import time
import requests

ACCESS_TOKEN = os.environ["TIKTOK_ACCESS_TOKEN"]
VIDEO_PATH = "output/final.mp4"

# "Upload to inbox" (draft) endpoints — different from the Direct Post ones.
INIT_URL = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"


def init_upload(video_size: int) -> dict:
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    body = {
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

    print(f"Done. Video sent to TikTok inbox as a draft. publish_id={publish_id} final_status={final_status}")
    print("Open the TikTok app on the target account to review and tap Post.")


if __name__ == "__main__":
    main()
