"""
Loops output/loop.mp4 (the zooming image) indefinitely and lays the FULL,
un-looped output/music.wav track on top, cutting the video to match the
music's natural length (generate_music.py now produces a full ~90s track,
so there's no audio loop seam to worry about).

A short fade-in/fade-out is still applied to the music for a clean start
and ending.
"""

import subprocess

LOOP_PATH = "output/loop.mp4"
MUSIC_PATH = "output/music.wav"
SMOOTHED_MUSIC_PATH = "output/music_smoothed.wav"
FINAL_PATH = "output/final.mp4"

FADE_SECONDS = 1.0  # gentle fade in/out at the very start/end of the track


def get_duration(path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def add_fade_in_out():
    duration = get_duration(MUSIC_PATH)
    fade_out_start = max(duration - FADE_SECONDS, 0)

    cmd = [
        "ffmpeg", "-y",
        "-i", MUSIC_PATH,
        "-af", f"afade=t=in:st=0:d={FADE_SECONDS},afade=t=out:st={fade_out_start}:d={FADE_SECONDS}",
        SMOOTHED_MUSIC_PATH,
    ]
    subprocess.run(cmd, check=True)


def main():
    add_fade_in_out()

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", LOOP_PATH,
        "-i", SMOOTHED_MUSIC_PATH,
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",   # cut the (infinitely looped) video to the music's length
        FINAL_PATH,
    ]

    subprocess.run(cmd, check=True)
    print(f"Saved final video to {FINAL_PATH}")


if __name__ == "__main__":
    main()
