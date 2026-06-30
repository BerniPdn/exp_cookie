"""
Extract audio from a single video recording.

This module converts one processed WEBM recording into a mono WAV file
compatible with Whisper.

The output audio has:
    - 16 kHz sample rate
    - mono channel
    - PCM 16-bit encoding
"""

from pathlib import Path
import subprocess


def extract_audio(
    input_video: Path,
    output_audio: Path,
):
    """
    Extract audio from a single video.

    Parameters
    ----------
    input_video : Path
        Input WEBM video.

    output_audio : Path
        Output WAV file.
    """

    output_audio.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        "ffmpeg",

        "-y",

        "-fflags",
        "+genpts",

        "-i",
        str(input_video),

        "-vn",

        "-ar",
        "16000",

        "-ac",
        "1",

        "-c:a",
        "pcm_s16le",

        str(output_audio),
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)