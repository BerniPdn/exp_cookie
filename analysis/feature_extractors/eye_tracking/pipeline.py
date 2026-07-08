"""
Run the complete eye-tracking processing pipeline.
"""

from __future__ import annotations

import argparse

from analysis.src.feature_extractors.eye_tracking.quality_control import (
    process_dataset as process_quality_control,
)

from analysis.src.feature_extractors.eye_tracking.filter_invalid_samples import (
    process_dataset as process_filter_invalid_samples,
)

from analysis.src.feature_extractors.eye_tracking.unmirror import (
    process_unmirror,
)

from analysis.src.feature_extractors.eye_tracking.assign_aois import (
    process_dataset as process_assign_aois,
)

from analysis.src.feature_extractors.eye_tracking.metrics import (
    process_metrics,
)


# ==========================================================
# Pipeline
# ==========================================================

def run_pipeline(
    overwrite: bool = False,
):

    print()
    print("=" * 60)
    print("EYE-TRACKING PIPELINE")
    print("=" * 60)

    print("\n[1/5] Quality control")
    process_quality_control(
        overwrite=overwrite,
    )

    print("\n[2/5] Filter invalid samples")
    process_filter_invalid_samples(
        overwrite=overwrite,
    )

    print("\n[3/5] Correct mirrored coordinates")
    process_unmirror(
        overwrite=overwrite,
    )

    print("\n[4/5] Assign AOIs")
    process_assign_aois(
        overwrite=overwrite,
    )

    print("\n[5/5] Compute metrics")
    process_metrics(
        overwrite=overwrite,
    )

    print()
    print("=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print()


# ==========================================================
# Main
# ==========================================================

def main():

    parser = argparse.ArgumentParser(
        description="Run the eye-tracking pipeline.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing outputs.",
    )

    args = parser.parse_args()

    run_pipeline(
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()