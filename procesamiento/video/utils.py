"""
Utility functions used across the video processing module.
"""

from pathlib import Path
import subprocess


def ensure_directory(directory: Path):
    """
    Create a directory if it does not already exist.

    Parameters
    ----------
    directory : Path
        Directory to create.
    """

    directory.mkdir(parents=True, exist_ok=True)


def run_ffmpeg(command: list[str]):
    """
    Execute an FFmpeg command.

    Parameters
    ----------
    command : list[str]
        Complete FFmpeg command.

    Raises
    ------
    RuntimeError
        If FFmpeg returns an error.
    """

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result