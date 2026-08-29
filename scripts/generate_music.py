"""
Generates a short instrumental track by calling Hugging Face's Inference API
directly over HTTP (rather than through huggingface_hub's InferenceClient
task methods, which have been renamed/changed across library versions —
this direct approach is more stable against future SDK changes).

IMPORTANT LICENSE NOTE:
facebook/musicgen-small ships under CC BY-NC 4.0 — non-commercial only.
If you plan to monetize the TikTok channel, swap MODEL_ID for a model with a
commercial-friendly license (e.g. an Apache-2.0 model) and confirm it's
currently servable through the free Inference API before depending on it.
"""

import os
import time
import requests

HF_TOKEN = os.environ["HF_TOKEN"]
MODEL_ID = "facebook/musicgen-small"  # non-commercial license — see note above
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"

# TODO: rotate/randomize this prompt so tracks vary day to day
PROMPT = "lofi chill beat, warm piano, soft drums, relaxing background music"

OUTPUT_PATH = "output/music.mp3"


def main():
    os.makedirs("output", exist_ok=True)
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    # The model sometimes needs to "warm up" on the free tier; retry a few
    # times if it reports it's still loading.
    for attempt in range(5):
        resp = requests.post(API_URL, headers=headers, json={"inputs": PROMPT}, timeout=120)

        if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("audio"):
            with open(OUTPUT_PATH, "wb") as f:
                f.write(resp.content)
            print(f"Saved music to {OUTPUT_PATH}")
            return

        # Model still loading — the API returns JSON with an estimated wait time.
        if resp.status_code == 503:
            wait = resp.json().get("estimated_time", 20)
            print(f"Model loading, waiting {wait:.0f}s (attempt {attempt + 1}/5)...")
            time.sleep(wait)
            continue

        if resp.status_code != 200:
            print(f"Response status: {resp.status_code}")
            print(f"Response body: {resp.text}")

        resp.raise_for_status()

    raise RuntimeError("Music generation failed after retries — see logs above.")


if __name__ == "__main__":
    main()
