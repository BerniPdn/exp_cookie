"""
Video quality control utilities.

This module inspects processed videos and extracts technical
information useful for quality assurance before downstream analysis.

The generated report includes:

- File size
- Resolution
- Frame count
- FPS
- Duration
- Mean audio volume
- Quality status
"""

from pathlib import Path
import subprocess
import re
import cv2
import pandas as pd

from configs.paths import (
    PROCESSED_VIDEO_DIR,
    VIDEO_QUALITY_REPORT,
)

# ==========================================================
# Audio Quality
# ==========================================================

def analyze_volume(video_path: Path):
    """
    Compute the mean audio volume using FFmpeg.

    Parameters
    ----------

    Returns
    -------
    float | None
        Mean volume in dB or None if unavailable.
    """

    try:

        result = subprocess.run(

            [
                "ffmpeg",
                "-i",
                str(video_path),
                "-af",
                "volumedetect",
                "-vn",
                "-f",
                "null",
                "-",
            ],

            capture_output=True,
            text=True,
            timeout=20,

        )

        match = re.search(
            r"mean_volume:\s*([-\d.]+)\s*dB",
            result.stderr,
        )

        if match:

            return float(match.group(1))

    except Exception:

        pass

    return None


# ==========================================================
# FPS Recovery
# ==========================================================

def count_real_fps(video_path: Path):
    """
    Estimate FPS by counting the number of decoded frames.

    This function is used when the FPS metadata stored in the
    container is corrupted.

    Parameters
    ----------
    video_path : Path

    Returns
    -------
    float | None
    """

    try:

        duration = subprocess.run(

            [
                "ffprobe",
                "-v",
                "quiet",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],

            capture_output=True,
            text=True,

            timeout=20,

        )

        duration = float(duration.stdout.strip())

        frames = subprocess.run(

            [
                "ffprobe",
                "-v",
                "quiet",
                "-count_frames",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=nb_read_frames",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],

            capture_output=True,
            text=True,

            timeout=120,

        )

        frames = int(frames.stdout.strip())

        if duration > 0:

            return round(frames / duration, 2)

    except Exception:

        return None


# ==========================================================
# Video Inspection
# ==========================================================
def extract_run_id(filename: str) -> str:
    """
    Extract the experiment run ID from a processed video filename.

    Expected format
    ---------------
    grabacion_<uuid>_<trial>_<run_id>_arreglado.webm
    """

    parts = Path(filename).stem.split("_")

    if len(parts) < 2:
        return "unknown"

    # El run_id es el penúltimo elemento
    return parts[-2]

def extract_trial(filename: str) -> str:
    """
    Extract the trial name from a processed video filename.

    Expected filename
    -----------------
    grabacion_<uuid>_<trial>_<run_id>_arreglado.webm

    Returns
    -------
    str
        Example:
            lamina_original
            lamina_nueva
    """

    parts = Path(filename).stem.split("_")

    if len(parts) < 6:
        return "unknown"

    # Todo lo que está entre el UUID y el run_id
    return "_".join(parts[2:-2])

def inspect_video(video_path: Path):
    """
    Inspect a single processed video.

    Parameters
    ----------
    video_path : Path

    Returns
    -------
    dict
        Dictionary containing video properties.
    """

    cap = cv2.VideoCapture(str(video_path))

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fps = cap.get(cv2.CAP_PROP_FPS)

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    cap.release()

    if fps <= 0 or fps > 100:

        fps = count_real_fps(video_path)

    duration = None

    if fps is not None and fps > 0:

        duration = round(frame_count / fps, 2)

    volume = analyze_volume(video_path)

    filesize = round(
        video_path.stat().st_size / (1024 ** 2),
        2,
    )

    return {

        "filename": video_path.name,
        
        "run_id": extract_run_id(video_path.name),

        "trial": extract_trial(video_path.name),

        "filesize_mb": filesize,

        "width": width,

        "height": height,

        "fps": fps,

        "frame_count": frame_count,

        "duration_seconds": duration,

        "volume_db": volume,

    }

# ==========================================================
# Quality Assessment
# ==========================================================

def interpret_quality(video_info: dict):
    """
    Evaluate the technical quality of a processed video.

    Parameters
    ----------
    video_info : dict
        Output from inspect_video().

    Returns
    -------
    tuple[str, str]
        (status, comments)
    """

    status = "OK"

    comments = []

    # ------------------------------------------------------
    # Resolution
    # ------------------------------------------------------

    if video_info["width"] < 640:

        status = "WARNING"

        comments.append("Low horizontal resolution.")

    if video_info["height"] < 480:

        status = "WARNING"

        comments.append("Low vertical resolution.")

    # ------------------------------------------------------
    # FPS
    # ------------------------------------------------------

    if video_info["fps"] is None:

        status = "FAILED"

        comments.append("FPS could not be recovered.")

    elif video_info["fps"] < 24:

        status = "WARNING"

        comments.append("Low frame rate.")

    # ------------------------------------------------------
    # Duration
    # ------------------------------------------------------

    duration = video_info["duration_seconds"]

    if duration is None:

        status = "FAILED"

        comments.append("Invalid duration.")

    elif duration < 45:

        status = "WARNING"

        comments.append("Recording shorter than expected.")

    elif duration > 90:

        status = "WARNING"

        comments.append("Recording longer than expected.")

    # ------------------------------------------------------
    # File size
    # ------------------------------------------------------

    if video_info["filesize_mb"] < 5:

        status = "WARNING"

        comments.append("Very small file size.")

    # ------------------------------------------------------
    # Audio
    # ------------------------------------------------------

    volume = video_info["volume_db"]

    if volume is None:

        comments.append("Audio unavailable.")

    elif volume < -45:

        status = "WARNING"

        comments.append("Very low audio volume.")

    if len(comments) == 0:

        comments.append("Video passed all quality checks.")

    return status, " ".join(comments)


# ==========================================================
# Dataset Inspection
# ==========================================================

def quality_control():
    """
    Inspect every processed video.

    Returns
    -------
    pandas.DataFrame
        Video quality report.
    """

    input_dir = PROCESSED_VIDEO_DIR

    videos = sorted(input_dir.rglob("*.webm"))

    report = []

    print(f"\nFound {len(videos)} processed videos.\n")

    for index, video in enumerate(videos, start=1):

        print(f"[{index}/{len(videos)}] {video.name}")

        info = inspect_video(video)

        status, comments = interpret_quality(info)

        info["status"] = status

        info["comments"] = comments

        report.append(info)

    return pd.DataFrame(report)


# ==========================================================
# Summary
# ==========================================================

def print_summary(df: pd.DataFrame):

    print("\n" + "=" * 55)

    print("VIDEO QUALITY REPORT")

    print("=" * 55)

    print(f"Videos analyzed : {len(df)}")

    print()

    print(f"OK       : {(df.status == 'OK').sum()}")

    print(f"WARNING  : {(df.status == 'WARNING').sum()}")

    print(f"FAILED   : {(df.status == 'FAILED').sum()}")

    print()

    print(f"Average FPS       : {df.fps.mean():.2f}")

    print(f"Average duration  : {df.duration_seconds.mean():.2f} s")

    print(f"Average file size : {df.filesize_mb.mean():.2f} MB")

    print("=" * 55)


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(

        description="Inspect processed videos."

    )


    args = parser.parse_args()

    VIDEO_QUALITY_REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = quality_control()

    report.to_csv(
        VIDEO_QUALITY_REPORT,
        index=False,
    )

    print_summary(report)

    print(f"\nReport saved to:\n{VIDEO_QUALITY_REPORT}\n")