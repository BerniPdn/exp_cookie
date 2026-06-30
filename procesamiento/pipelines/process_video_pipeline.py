"""
Complete video processing pipeline.
"""

import argparse

from procesamiento.video.process_videos import process_videos
from procesamiento.video.quality_control import quality_control


def run_video_pipeline(
    overwrite: bool = False,
):
    """
    Run the complete video processing pipeline.

    Parameters
    ----------
    overwrite : bool, default=False
        Whether to overwrite existing processed files.
    """

    print("\n" + "=" * 60)
    print("VIDEO PIPELINE")
    print("=" * 60)

    process_videos(
        overwrite=overwrite,
    )

    quality_control()

    print("\n✓ Video pipeline completed.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Run the complete video processing pipeline."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing processed files.",
    )

    args = parser.parse_args()

    run_video_pipeline(
        overwrite=args.overwrite,
    )