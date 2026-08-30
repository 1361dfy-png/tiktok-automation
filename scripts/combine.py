"""
Loops BOTH output/loop.mp4 and output/music.mp3 independently until each
reaches TARGET_SECONDS, then muxes them together. This guarantees a fixed
final duration regardless of how short the raw generated music clip is —
free text-to-audio APIs often return only 8-15 seconds by default, which is
why we don't just rely on "-shortest" against the raw music length.
"""

import subprocess

LOOP_PATH = "output/loop.mp4"
MUSIC_PATH = "output/music.wav"
FINAL_PATH = "output/final.mp4"

TARGET_SECONDS = 65  # comfortably over TikTok's 60s mark; adjust as you like


def main():
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", LOOP_PATH,
        "-stream_loop", "-1",
        "-i", MUSIC_PATH,
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-t", str(TARGET_SECONDS),
        FINAL_PATH,
    ]

    subprocess.run(cmd, check=True)
    print(f"Saved final video to {FINAL_PATH} ({TARGET_SECONDS}s)")


if __name__ == "__main__":
    main()
