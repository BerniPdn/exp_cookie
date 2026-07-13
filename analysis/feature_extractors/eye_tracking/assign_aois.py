"""
Assign AOIs to every processed eye-tracking file.

Input
-----
data/analysis/eye_tracking/intermediate/*.csv

Output
------
One CSV per run containing an additional AOI column.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from configs.paths import (
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_UNIMIRROR_DIR,
    METADATA_DIR,
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_AOIS_DIR,
)

# ==========================================================
# Paths
# ==========================================================

INPUT_DIR = (
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_UNIMIRROR_DIR
)

OUTPUT_DIR = (
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_AOIS_DIR
)

NEW_AOIS = (
    METADATA_DIR /
    "aois_lamina_nueva.csv"
)

OLD_AOIS = (
    METADATA_DIR /
    "aois_lamina_vieja.csv"
)

# ==========================================================
# Load AOIs
# ==========================================================

def load_aois():

    return {
        "new": pd.read_csv(
            NEW_AOIS
        ),

        "old": pd.read_csv(
            OLD_AOIS
        ),
    }


# ==========================================================
# Geometry
# ==========================================================

def point_inside_aoi(x, y, aoi,):
    return (
        aoi.x_min <= x <= aoi.x_max
        and
        aoi.y_min <= y <= aoi.y_max
    )


def assign_single_point(x, y, image, aois,):
    current_aois = aois[image]
    for _, aoi in current_aois.iterrows():
        if point_inside_aoi( x, y, aoi,):
            return aoi.aoi
    return None

# ==========================================================
# File processing
# ==========================================================

def process_file(
    csv_file: Path,
    aois,

):

    df = pd.read_csv(
        csv_file
    )

    image = df["image"].iloc[0].strip().lower()

    if image == "new":
        image = "new"

    elif image == "original":
        image = "old"

    else:
        raise ValueError(
            f"Unknown image '{image}' in {csv_file.name}"
        )

    assigned = []
    inside = []

    for row in df.itertuples():
        aoi = assign_single_point(
            x=row.x_analysis,
            y=row.y_analysis,
            image=image,
            aois=aois,
        )

        assigned.append(
            aoi
        )

        inside.append(
            aoi is not None
        )

    df["aoi"] = assigned
    df["inside_aoi"] = inside

    output = (
        OUTPUT_DIR /
        csv_file.name
    )

    df.to_csv(
        output,
        index=False,
    )

    return {
        "samples": len(df),
        "inside": int(
            df["inside_aoi"].sum()
        ),

        "outside": int(
            (~df["inside_aoi"]).sum()
        ),

        "output": output,
    }


# ==========================================================
# Dataset processing
# ==========================================================

def process_dataset(
    overwrite=False,
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    aois = load_aois()
    csv_files = sorted(
        INPUT_DIR.glob("*.csv")
    )

    processed = []
    skipped = 0

    for csv_file in csv_files:
        output = (
            OUTPUT_DIR /
            csv_file.name
        )

        if (
            output.exists()
            and not overwrite
        ):

            skipped += 1
            continue

        print(
            f"Processing {csv_file.name}"
        )

        summary = process_file(
            csv_file,
            aois,
        )

        processed.append(
            summary
        )

    return processed, skipped

# ==========================================================
# Summary
# ==========================================================

def print_summary(
    processed,
    skipped,
):

    total_samples = sum(
        p["samples"]
        for p in processed
    )

    total_inside = sum(
        p["inside"]
        for p in processed
    )

    total_outside = sum(
        p["outside"]
        for p in processed
    )

    print()
    print("=" * 60)
    print("AOI ASSIGNMENT COMPLETE")
    print("=" * 60)
    print()
    print(f"Files processed : {len(processed)}")
    print(f"Files skipped   : {skipped}")
    print(f"Samples         : {total_samples}")
    print(f"Inside AOIs     : {total_inside}")
    print(f"Outside AOIs    : {total_outside}")
    print()
    print("Output:")
    print(OUTPUT_DIR)
    print()
    print("=" * 60)


# ==========================================================
# Main
# ==========================================================

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Assign AOIs to processed eye-tracking files."
        )
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output.",
    )

    args = parser.parse_args()
    processed, skipped = process_dataset(
        overwrite=args.overwrite,
    )

    print_summary(
        processed,
        skipped,
    )


if __name__ == "__main__":
    main()