"""
Generate heatmaps for every processed eye-tracking CSV.
"""

from pathlib import Path

from configs.paths import (
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_DIR,
    EYE_TRACKING_RESULTS_DIR,
)

from .generate_heatmap import plot_heatmap
import pandas as pd


# ==========================================================
# Paths
# ==========================================================

INPUT_DIR = (
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_DIR /
    "with_aois"
)

OUTPUT_DIR = (
    EYE_TRACKING_RESULTS_DIR/
    "heatmaps" /
    "individual"
)


# ==========================================================
# Main
# ==========================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_files = sorted(INPUT_DIR.glob("*.csv"))

    print(f"\nFound {len(csv_files)} files.\n")

    for i, csv_file in enumerate(csv_files, start=1):

        print(
            f"[{i}/{len(csv_files)}] "
            f"{csv_file.name}"
        )

        df = pd.read_csv(csv_file)

        plot_heatmap(
            df=df,
            output_file=(
                OUTPUT_DIR /
                f"{csv_file.stem}_heatmap.png"
            ),
            title=csv_file.stem,
            only_aoi=False,
        )

    print()
    print("=" * 60)
    print("ALL HEATMAPS GENERATED")
    print("=" * 60)
    print()
    print("Saved to:")
    print(OUTPUT_DIR)
    print()


if __name__ == "__main__":
    main()