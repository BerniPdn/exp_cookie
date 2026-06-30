"""
Complete eye-tracking processing pipeline.
"""

import argparse

from procesamiento.eye_tracking.process_eye_tracking import (
    process_eye_tracking,
)


def run_eye_tracking_pipeline(
    overwrite: bool = False,
):
    """
    Run the complete eye-tracking processing pipeline.

    Parameters
    ----------
    overwrite : bool, default=False
        Whether to overwrite existing processed files.
    """

    print("\n" + "=" * 60)
    print("EYE TRACKING PIPELINE")
    print("=" * 60)

    process_eye_tracking(
        overwrite=overwrite,
    )

    print("\n✓ Eye-tracking pipeline completed.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Run the complete eye-tracking processing pipeline."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing processed files.",
    )

    args = parser.parse_args()

    run_eye_tracking_pipeline(
        overwrite=args.overwrite,
    )