"""
Generates a longer (~90s) track by running MusicGen for several separate
segments and crossfading them together — MusicGen-small can't generate one
continuous clip beyond ~40s because its position-embedding table is a fixed
size, so a single long generate() call errors out with an IndexError once
it runs past that limit.

Each segment is a genuinely fresh generation (not a copy), so the result
doesn't have the "obviously looping" quality a single short clip would.

IMPORTANT LICENSE NOTE:
facebook/musicgen-small ships under CC BY-NC 4.0 — non-commercial only.
If you plan to monetize the TikTok channel, swap MODEL_ID for a model with
a commercial-friendly license and adjust accordingly.
"""

import os
import random
import numpy as np
import scipy.io.wavfile
from transformers import pipeline

MODEL_ID = "facebook/musicgen-small"  # non-commercial license — see note above

# Rotate through a few styles so consecutive videos don't sound identical.
# All three segments use the SAME style prompt so they cohere as one track.
PROMPTS = [
    "lofi chill beat, warm piano, soft drums, relaxing background music",
    "ambient pad textures, slow evolving synths, dreamy and calm",
    "acoustic guitar fingerpicking, gentle and warm, cozy atmosphere",
    "soft rain sounds blended with mellow piano, peaceful and introspective",
    "warm analog synth pads, slow tempo, nostalgic and soothing",
]
PROMPT = random.choice(PROMPTS)

OUTPUT_PATH = "output/music.wav"

# ~1500 tokens ≈ 30s per segment, safely under the model's ~40s hard limit.
SEGMENT_MAX_NEW_TOKENS = 1500
NUM_SEGMENTS = 3          # 3 x 30s ≈ 90s total
CROSSFADE_SECONDS = 1.5   # overlap blended between consecutive segments


def crossfade_concat(clips: list, sample_rate: int, fade_seconds: float) -> np.ndarray:
    fade_samples = int(fade_seconds * sample_rate)
    result = clips[0]

    for next_clip in clips[1:]:
        fade_out = result[-fade_samples:] * np.linspace(1, 0, fade_samples)
        fade_in = next_clip[:fade_samples] * np.linspace(0, 1, fade_samples)
        blended = fade_out + fade_in
        result = np.concatenate([result[:-fade_samples], blended, next_clip[fade_samples:]])

    return result


def main():
    os.makedirs("output", exist_ok=True)

    synthesiser = pipeline("text-to-audio", model=MODEL_ID, device="cpu")

    segments = []
    sample_rate = None
    for i in range(NUM_SEGMENTS):
        print(f"Generating segment {i + 1}/{NUM_SEGMENTS}...")
        result = synthesiser(
            PROMPT,
            forward_params={"max_new_tokens": SEGMENT_MAX_NEW_TOKENS, "do_sample": True},
        )
        sample_rate = result["sampling_rate"]
        segments.append(np.asarray(result["audio"]).squeeze())

    full_track = crossfade_concat(segments, sample_rate, CROSSFADE_SECONDS)
    scipy.io.wavfile.write(OUTPUT_PATH, rate=sample_rate, data=full_track)

    duration = len(full_track) / sample_rate
    print(f"Saved music to {OUTPUT_PATH} (~{duration:.0f}s, prompt: {PROMPT})")


if __name__ == "__main__":
    main()
