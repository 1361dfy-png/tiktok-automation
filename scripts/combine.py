"""
Builds the final video:
  - output/loop.mp4 (the zooming background) is looped to cover the full
    music length.
  - output/music.wav plays once, in full, with a short fade in/out.
  - Each output/slide_N.png (rendered by draw_text.py) is overlaid on top
    for its own equal time slice, so the TEXT STAYS FIXED on screen while
    only the background moves underneath it — the slide images themselves
    contain no motion.
"""

import glob
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


def build_overlay_filter(num_slides: int, slice_seconds: float) -> str:
    """
    Chains one overlay per slide onto the background, each gated to its own
    time window with enable='between(t,start,end)'. Slide inputs are indices
    2..num_slides+1 (0 = looped background video, 1 = music).
    """
    filters = []
    current_label = "0:v"

    for i in range(num_slides):
        input_index = i + 2
        start = i * slice_seconds
        end = (i + 1) * slice_seconds
        out_label = f"v{i}"
        filters.append(
            f"[{current_label}][{input_index}:v]overlay=enable='between(t,{start},{end})'[{out_label}]"
        )
        current_label = out_label

    return ";".join(filters), current_label


def main():
    add_fade_in_out()
    total_seconds = get_duration(SMOOTHED_MUSIC_PATH)

    slide_paths = sorted(glob.glob("output/slide_*.png"))
    num_slides = len(slide_paths)
    slice_seconds = total_seconds / num_slides

    filter_complex, final_video_label = build_overlay_filter(num_slides, slice_seconds)

    cmd = ["ffmpeg", "-y", "-stream_loop", "-1", "-i", LOOP_PATH, "-i", SMOOTHED_MUSIC_PATH]
    for slide_path in slide_paths:
        cmd += ["-loop", "1", "-i", slide_path]

    cmd += [
        "-filter_complex", filter_complex,
        "-map", f"[{final_video_label}]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-t", str(total_seconds),
        FINAL_PATH,
    ]

    subprocess.run(cmd, check=True)
    print(f"Saved final video to {FINAL_PATH} ({total_seconds:.0f}s, {num_slides} slides)")


if __name__ == "__main__":
    main()
