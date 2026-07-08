"""
Eye-tracking quality control.

Computes quality metrics for every processed eye-tracking CSV.

Output
------
data/analysis/eye_tracking/quality/eye_tracking_quality.csv
"""

from __future__ import annotations

import argparse

import pandas as pd

from configs.paths import (
    PROCESSED_EYE_TRACKING_DIR,
    ANALYSIS_EYE_TRACKING_DIR,
)

# ==========================================================
# Paths
# ==========================================================

INPUT_DIR = PROCESSED_EYE_TRACKING_DIR

OUTPUT_DIR = (
    ANALYSIS_EYE_TRACKING_DIR /
    "quality"
)

OUTPUT_FILE = (
    OUTPUT_DIR /
    "eye_tracking_quality.csv"
)

MARGIN = 0.20


# ==========================================================
# Metrics
# ==========================================================

def inside_image(df):

    return (
        (df["x_relative"] >= 0)
        &
        (df["x_relative"] <= 1)
        &
        (df["y_relative"] >= 0)
        &
        (df["y_relative"] <= 1)
    )


def inside_margin(df):

    return (
        (df["x_relative"] >= -MARGIN)
        &
        (df["x_relative"] <= 1 + MARGIN)
        &
        (df["y_relative"] >= -MARGIN)
        &
        (df["y_relative"] <= 1 + MARGIN)
    )


# ==========================================================
# Process one file
# ==========================================================

def summarize(csv_file):

    df = pd.read_csv(csv_file)

    inside = inside_image(df)

    margin = inside_margin(df)

    participant = df["run_id"].iloc[0]

    image = df["image"].iloc[0]

    inside_pct = round(
        100 * inside.mean(),
        1,
    )

    margin_pct = round(
        100 * margin.mean(),
        1,
    )

    if inside_pct >= 90:
        quality = "Excellent"

    elif inside_pct >= 75:
        quality = "Good"

    elif inside_pct >= 50:
        quality = "Fair"

    else:
        quality = "Poor"

    return {

        "participant": participant,

        "file": csv_file.name,

        "image": image,

        "samples": len(df),

        "inside_image": int(inside.sum()),

        "inside_margin": int(margin.sum()),

        "pct_inside_image": inside_pct,

        "pct_inside_margin": margin_pct,

        "quality": quality,

        "x_min":
            round(
                df["x_relative"].min(),
                3,
            ),

        "x_max":
            round(
                df["x_relative"].max(),
                3,
            ),

        "y_min":
            round(
                df["y_relative"].min(),
                3,
            ),

        "y_max":
            round(
                df["y_relative"].max(),
                3,
            ),

    }

# ==========================================================
# Process dataset
# ==========================================================

def process_dataset(
    overwrite=False,
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if OUTPUT_FILE.exists() and not overwrite:

        print(f"{OUTPUT_FILE} already exists.")
        return

    rows = []

    csv_files = sorted(

        f

        for f in INPUT_DIR.glob("*.csv")

        if "oasis" not in f.name.lower()

    )

    for csv_file in csv_files:

        print(f"Processing {csv_file.name}")

        rows.append(
            summarize(csv_file)
        )

    quality = pd.DataFrame(rows)

    quality = quality.sort_values(
        [
            "participant",
            "image",
        ]
    )

    quality.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()

    print("=" * 60)
    print("QUALITY CONTROL COMPLETE")
    print("=" * 60)
    print()

    print(f"Files analyzed : {len(quality)}")

    print()

    print(
        quality[
            [   
                "participant",
                "image",
                "pct_inside_image",
                "pct_inside_margin",
                "quality",
            ]
        ]
    ) 
    print()

    print(f"Saved to:\n{OUTPUT_FILE}")

    print()


# ==========================================================
# Main
# ==========================================================

def main():

    parser = argparse.ArgumentParser(
        description="Eye-tracking quality control."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output.",
    )

    args = parser.parse_args()

    process_dataset(
        overwrite=args.overwrite,
    )


if __name__ == "__main__":

    main()