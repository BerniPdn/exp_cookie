"""
Repair a single video recorded during the experiment.

Browser-generated WEBM files sometimes contain inconsistent timestamps,
which can cause problems when processing them with OpenCV or MediaPipe.

This script regenerates presentation timestamps (PTS) using FFmpeg
without re-encoding the video.
"""

from pathlib import Path

from .utils import ensure_directory, run_ffmpeg


def normalize_video(
    input_video: Path,
    output_video: Path,
):
    """
    Repair a single WEBM recording.

    Parameters
    ----------
    input_video : Path
        Original WEBM recording.

    output_video : Path
        Destination of the repaired recording.
    """

    # Create output directory if needed.
    ensure_directory(output_video.parent)

    command = [
        "ffmpeg",

        # Overwrite output if it already exists.
        "-y",

        # Regenerate timestamps.
        "-fflags",
        "+genpts",

        # Input file.
        "-i",
        str(input_video),

        # Copy video and audio streams without re-encoding.
        "-c",
        "copy",

        # Output file.
        str(output_video),
    ]

    run_ffmpeg(command)