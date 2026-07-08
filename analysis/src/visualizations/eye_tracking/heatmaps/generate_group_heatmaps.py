"""
Generate average gaze heatmaps.

Creates one average heatmap per stimulus by combining
all participant gaze samples.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from configs.paths import (
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_DIR,
    ANALYSIS_EYE_TRACKING_DIR,
)

from .generate_heatmap import plot_heatmap


# ==========================================================
# Paths
# ==========================================================

INPUT_DIR = (
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_DIR /
    "with_aois"
)

OUTPUT_DIR = (
    ANALYSIS_EYE_TRACKING_DIR /
    "heatmaps" /
    "average"
)


# ==========================================================
# Helpers
# ==========================================================

def load_group(image: str) -> pd.DataFrame:
    """
    Load all CSVs corresponding to one image.
    """

    dfs = []

    for csv_file in sorted(INPUT_DIR.glob("*.csv")):

        df = pd.read_csv(csv_file)

        if df.empty:
            continue

        if df["image"].iloc[0] != image:
            continue

        dfs.append(df)

    if len(dfs) == 0:
        raise ValueError(f"No CSVs found for image '{image}'.")

    return pd.concat(
        dfs,
        ignore_index=True,
    )

# ==========================================================
# Main
# ==========================================================

# ==========================================================
# Main
# ==========================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for image in ["original", "new"]:

        print()
        print("=" * 60)
        print(f"Generating average heatmap: {image}")
        print("=" * 60)

        try:

            df = load_group(image)

        except ValueError as e:

            print(e)

            continue

        print(
            f"Samples: {len(df):,}"
        )

        print(
            f"Participants: {df['run_id'].nunique()}"
        )

        plot_heatmap(
            df=df,
            output_file=(
                OUTPUT_DIR /
                f"{image}_average_heatmap.png"
            ),
            title=f"{image.capitalize()} Average Heatmap",
            only_aoi=False,
        )

    print()
    print("=" * 60)
    print("AVERAGE HEATMAPS COMPLETE")
    print("=" * 60)
    print()
    print("Saved to:")
    print(OUTPUT_DIR)
    print()


if __name__ == "__main__":
    main()