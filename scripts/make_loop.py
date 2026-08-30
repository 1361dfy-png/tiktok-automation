"""
Turns output/image.png into a silent, slowly zooming vertical video using
ffmpeg's zoompan filter. Pure CPU, no AI model needed — this is the step
that makes the whole pipeline runnable on GitHub's free (GPU-less) runners.
"""

import subprocess

IMAGE_PATH = "output/image_with_text.png"
LOOP_PATH = "output/loop.mp4"

FPS = 25
LOOP_SECONDS = 15
WIDTH, HEIGHT = 1080, 1920  # TikTok vertical format


def main():
    total_frames = FPS * LOOP_SECONDS

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", IMAGE_PATH,
        "-vf",
        (
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT},"
            f"zoompan=z='min(zoom+0.0006,1.25)':d={total_frames}:"
            f"s={WIDTH}x{HEIGHT}:fps={FPS}"
        ),
        "-t", str(LOOP_SECONDS),
        "-pix_fmt", "yuv420p",
        LOOP_PATH,
    ]

    subprocess.run(cmd, check=True)
    print(f"Saved loop video to {LOOP_PATH}")


if __name__ == "__main__":
    main()
