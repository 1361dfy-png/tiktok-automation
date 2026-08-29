"""
Generates one still image using Hugging Face's free Inference API.
Free tier = rate-limited but no cost. Get a token at https://huggingface.co/settings/tokens
and store it as the HF_TOKEN secret in your repo (Settings > Secrets and variables > Actions).

Swap MODEL_ID for any other text-to-image model on the Hugging Face Hub that
supports the Inference API — check the model page for a "Deploy > Inference API"
button to confirm it's currently servable on the free tier before relying on it.
"""

import os
from huggingface_hub import InferenceClient

HF_TOKEN = os.environ["HF_TOKEN"]
MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"  # swap for a lighter model if this times out

# TODO: replace with your own prompt logic (random pick from a list, rotate a theme, etc.)
PROMPT = "a dreamy pastel-colored abstract landscape, soft light, cinematic, 9:16 vertical composition"

OUTPUT_PATH = "output/image.png"


def main():
    os.makedirs("output", exist_ok=True)
    client = InferenceClient(token=HF_TOKEN)

    image = client.text_to_image(
        PROMPT,
        model=MODEL_ID,
        width=1024,
        height=1792,  # vertical, TikTok-friendly aspect ratio
    )
    image.save(OUTPUT_PATH)
    print(f"Saved image to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
