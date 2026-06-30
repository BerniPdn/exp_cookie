"""
Extract audio from every processed video.

This script converts all WEBM recordings inside a directory into WAV
files suitable for speech transcription.
"""

from pathlib import Path
import argparse
import time

from .extract_audio import extract_audio

from configs.paths import (
    PROCESSED_VIDEO_DIR,
    PROCESSED_AUDIO_DIR,
)

def process_audio(
    overwrite=False,
):
    """
    Convert every WEBM video into a WAV file.

    Parameters
    ----------
    overwrite : bool, default=False
        Whether to overwrite existing output files.

    Returns
    -------
    dict
        Processing summary.
    """
    input_dir = PROCESSED_VIDEO_DIR
    output_dir = PROCESSED_AUDIO_DIR    
    videos = sorted(input_dir.rglob("*.webm"))

    summary = {
        "total": len(videos),
        "processed": 0,
        "skipped": 0,
        "failed": 0,
    }

    start = time.time()

    print(f"\nFound {len(videos)} videos.\n")

    for index, video in enumerate(videos, start=1):

        relative = video.relative_to(input_dir)

        output_audio = (
            output_dir /
            relative.with_suffix(".wav")
        )

        output_audio.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        print(
            f"[{index}/{len(videos)}] "
            f"{relative}"
        )

        if output_audio.exists() and not overwrite:

            summary["skipped"] += 1

            print("   ⏭ Already processed.")

            continue

        try:

            extract_audio(
                video,
                output_audio,
            )

            summary["processed"] += 1

            print("   ✅ Success")

        except Exception as e:

            summary["failed"] += 1

            print(f"   ❌ Failed: {e}")

    summary["elapsed"] = time.time() - start

    return summary


def print_summary(summary):

    print("\n" + "=" * 45)
    print("AUDIO EXTRACTION FINISHED")
    print("=" * 45)

    print(f"Videos found : {summary['total']}")
    print(f"Processed    : {summary['processed']}")
    print(f"Skipped      : {summary['skipped']}")
    print(f"Failed       : {summary['failed']}")
    print(f"Elapsed (s)  : {summary['elapsed']:.1f}")

    print("=" * 45)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Extract audio from processed videos."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files."
    )

    args = parser.parse_args()

    summary = process_audio(
        args.overwrite
    )

    print_summary(summary)