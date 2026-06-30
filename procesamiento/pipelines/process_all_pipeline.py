"""
Complete experiment processing pipeline.
"""

import argparse

from procesamiento.pipelines.process_video_pipeline import (
    run_video_pipeline,
)

from procesamiento.pipelines.process_audio_pipeline import (
    run_audio_pipeline,
)

from procesamiento.pipelines.process_eye_tracking_pipeline import (
    run_eye_tracking_pipeline,
)


def run_experiment_pipeline(
    overwrite: bool = False,
):
    """
    Run the complete experiment processing pipeline.

    Parameters
    ----------
    overwrite : bool, default=False
        Whether to overwrite existing processed files.
    """

    print("\n" + "=" * 70)
    print("EXPERIMENT PROCESSING")
    print("=" * 70)

    results = {}

    # ======================================================
    # Video
    # ======================================================

    try:

        run_video_pipeline(
            overwrite=overwrite,
        )

        results["Video"] = "SUCCESS"

    except Exception as e:

        results["Video"] = f"FAILED ({e})"

        print("\n" + "-" * 60)
        print("VIDEO PIPELINE FAILED")
        print("-" * 60)
        print(e)

    # ======================================================
    # Audio
    # ======================================================

    try:

        run_audio_pipeline(
            overwrite=overwrite,
        )

        results["Audio"] = "SUCCESS"

    except Exception as e:

        results["Audio"] = f"FAILED ({e})"

        print("\n" + "-" * 60)
        print("AUDIO PIPELINE FAILED")
        print("-" * 60)
        print(e)

    # ======================================================
    # Eye Tracking
    # ======================================================

    try:

        run_eye_tracking_pipeline(
            overwrite=overwrite,
        )

        results["Eye Tracking"] = "SUCCESS"

    except Exception as e:

        results["Eye Tracking"] = f"FAILED ({e})"

        print("\n" + "-" * 60)
        print("EYE TRACKING PIPELINE FAILED")
        print("-" * 60)
        print(e)

    # ======================================================
    # Final summary
    # ======================================================

    print("\n" + "=" * 70)
    print("PROCESSING SUMMARY")
    print("=" * 70)

    for module, status in results.items():

        if status == "SUCCESS":

            print(f"✓ {module:<15} {status}")

        else:

            print(f"✗ {module:<15} {status}")

    print("=" * 70)

    if all(status == "SUCCESS" for status in results.values()):

        print("\n🎉 Experiment processed successfully!")

    else:

        print(
            "\n⚠️  Experiment finished with errors. "
            "Check the messages above."
        )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Run the complete experiment processing pipeline."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing processed files.",
    )

    args = parser.parse_args()

    run_experiment_pipeline(
        overwrite=args.overwrite,
    )