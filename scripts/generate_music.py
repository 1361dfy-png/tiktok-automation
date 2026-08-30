"""
Generates a short instrumental track by running facebook/musicgen-small
LOCALLY (on CPU, right inside the GitHub Actions runner) via the
transformers library — no external Inference API dependency.

Why local instead of an API call: Hugging Face's free hf-inference API
no longer serves music-generation models (as of testing in 2026, only
speech-related tasks are available there). Running the model directly
sidesteps that entirely, at the cost of a slower (CPU) generation step.

IMPORTANT LICENSE NOTE:
facebook/musicgen-small ships under CC BY-NC 4.0 — non-commercial only.
If you plan to monetize the TikTok channel, swap MODEL_ID for a model with
a commercial-friendly license (e.g. an Apache-2.0 model like Stable Audio
Open) and adjust the pipeline call accordingly.
"""

import os
import scipy.io.wavfile
from transformers import pipeline

MODEL_ID = "facebook/musicgen-small"  # non-commercial license — see note above

# TODO: rotate/randomize this prompt so tracks vary day to day
PROMPT = "lofi chill beat, warm piano, soft drums, relaxing background music"

OUTPUT_PATH = "output/music.wav"

# Roughly controls output length. MusicGen generates at ~50 tokens/second
# of audio, so ~500 tokens ≈ 10 seconds. Keep this modest — CPU generation
# time scales with it, and combine.py loops whatever we produce anyway.
MAX_NEW_TOKENS = 512


def main():
    os.makedirs("output", exist_ok=True)

    synthesiser = pipeline("text-to-audio", model=MODEL_ID, device="cpu")
    result = synthesiser(PROMPT, forward_params={"max_new_tokens": MAX_NEW_TOKENS, "do_sample": True})

    scipy.io.wavfile.write(OUTPUT_PATH, rate=result["sampling_rate"], data=result["audio"][0])
    print(f"Saved music to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
