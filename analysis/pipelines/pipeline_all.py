"""Run preprocessing and all analysis pipelines for the project."""

from __future__ import annotations

import argparse

from analysis.pipelines.pipeline_fe_eye_tracking import (
    run_pipeline as run_eye_tracking_analysis,
)
from analysis.pipelines.pipeline_fe_text import (
    run_pipeline as run_text_analysis,
)
from procesamiento.pipelines.process_all_pipeline import run_experiment_pipeline


def run_visualizations() -> None:
    """Generate optional eye-tracking visualizations after metrics exist."""

    from analysis.visualizations.eye_tracking.descriptive_plots import (
        main as create_descriptive_plots,
    )
    from analysis.visualizations.eye_tracking.heatmaps.generate_all_heatmaps import (
        main as create_individual_heatmaps,
    )
    from analysis.visualizations.eye_tracking.heatmaps.generate_group_heatmaps import (
        main as create_group_heatmaps,
    )

    print("\n[4/4] Generate eye-tracking visualizations")
    create_individual_heatmaps()
    create_group_heatmaps()
    create_descriptive_plots()


def run_pipeline(
    overwrite: bool = False,
    with_visualizations: bool = False,
) -> None:
    """Run the project workflow in its dependency order."""

    total_steps = 4 if with_visualizations else 3

    print()
    print("=" * 70)
    print("COMPLETE PROJECT PIPELINE")
    print("=" * 70)

    print(f"\n[1/{total_steps}] Preprocess experiment data")
    run_experiment_pipeline(overwrite=overwrite)

    print(f"\n[2/{total_steps}] Run text analysis")
    run_text_analysis(overwrite=overwrite)

    print(f"\n[3/{total_steps}] Run eye-tracking analysis")
    run_eye_tracking_analysis(overwrite=overwrite)

    if with_visualizations:
        run_visualizations()

    print()
    print("=" * 70)
    print("COMPLETE PROJECT PIPELINE FINISHED")
    print("=" * 70)
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run preprocessing and all analysis pipelines.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing preprocessing and feature outputs.",
    )
    parser.add_argument(
        "--with-visualizations",
        action="store_true",
        help="Also generate eye-tracking heatmaps and descriptive plots.",
    )
    args = parser.parse_args()

    run_pipeline(
        overwrite=args.overwrite,
        with_visualizations=args.with_visualizations,
    )


if __name__ == "__main__":
    main()
