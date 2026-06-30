"""
Process all raw videos in a dataset.

This script iterates through every WEBM recording in the input directory,
repairs it if necessary, and stores the repaired version in the processed
dataset.

Unlike repair_video.py, this script operates on entire folders rather
than individual files.
"""

from pathlib import Path
import argparse
import time

from procesamiento.video.normalize_video import  normalize_video
from configs.paths import (
    RAW_VIDEO_DIR,
    PROCESSED_VIDEO_DIR,
)

def process_videos(
    overwrite: bool = False,
):
    """
    Repair every WEBM video contained in a directory.

    Parameters
    ----------
      overwrite : bool, default=False
        Whether to overwrite existing output files.

    Returns
    -------
    dict
        Processing summary.
    """

    # Search recursively to allow future nested folder structures.
    input_dir = RAW_VIDEO_DIR
    output_dir = PROCESSED_VIDEO_DIR
    videos = sorted(input_dir.rglob("*.webm"))

    summary = {
        "total": len(videos),
        "processed": 0,
        "skipped": 0,
        "failed": 0,
    }

    start = time.time()

    print(f"\nFound {len(videos)} videos.\n")

    for idx, video in enumerate(videos, start=1):

        # Preserve relative folder structure.
        relative_path = video.relative_to(input_dir)

        output_video = output_dir / relative_path

        output_video.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        print(f"[{idx}/{len(videos)}] {relative_path}")

        # Skip already processed videos.
        if output_video.exists() and not overwrite:

            summary["skipped"] += 1

            print("   ⏭ Already processed.")

            continue

        try:

            normalize_video(
                video,
                output_video,
            )

            summary["processed"] += 1

            print("   ✅ Success")

        except Exception as e:

            summary["failed"] += 1

            print(f"   ❌ Failed: {e}")

    summary["elapsed"] = time.time() - start

    return summary


def print_summary(summary):
    """
    Print a processing summary.
    """

    print("\n" + "=" * 45)
    print("VIDEO PROCESSING FINISHED")
    print("=" * 45)

    print(f"Videos found      : {summary['total']}")
    print(f"Processed         : {summary['processed']}")
    print(f"Skipped           : {summary['skipped']}")
    print(f"Failed            : {summary['failed']}")
    print(f"Elapsed time (s)  : {summary['elapsed']:.1f}")

    print("=" * 45)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Repair all WEBM recordings in a dataset."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files."
    )

    args = parser.parse_args()

    summary = process_videos(
        args.overwrite
    )

    print_summary(summary)