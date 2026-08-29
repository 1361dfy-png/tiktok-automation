"""
Generates a short instrumental track using Hugging Face's free Inference API.

IMPORTANT LICENSE NOTE:
facebook/musicgen-small ships under CC BY-NC 4.0 — non-commercial only.
If you plan to monetize the TikTok channel, swap MODEL_ID for a model with a
commercial-friendly license (e.g. an Apache-2.0 model such as ACE-Step or
Stable Audio Open) and confirm on the model's Hugging Face page that it's
currently servable through the free Inference API before depending on it —
model availability on the free tier changes over time.
"""

import os
from huggingface_hub import InferenceClient

HF_TOKEN = os.environ["HF_TOKEN"]
MODEL_ID = "facebook/musicgen-small"  # non-commercial license — see note above

# TODO: rotate/randomize this prompt so tracks vary day to day
PROMPT = "lofi chill beat, warm piano, soft drums, relaxing background music"

OUTPUT_PATH = "output/music.mp3"


def main():
    os.makedirs("output", exist_ok=True)
    client = InferenceClient(token=HF_TOKEN)

    audio_bytes = client.text_to_audio(PROMPT, model=MODEL_ID)

    with open(OUTPUT_PATH, "wb") as f:
        f.write(audio_bytes)
    print(f"Saved music to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
