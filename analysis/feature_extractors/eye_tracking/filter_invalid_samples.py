"""
Remove invalid eye-tracking samples.

Input
-----
Processed eye-tracking CSVs.

Output
------
Filtered CSVs with an additional
'valid_sample' column.

Also generates a summary CSV.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from configs.paths import (
    PROCESSED_EYE_TRACKING_DIR,
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_FILTERED_DIR,
    FILTER_QUALITY_REPORT
)

# ==========================================================
# Paths
# ==========================================================

INPUT_DIR = PROCESSED_EYE_TRACKING_DIR

OUTPUT_DIR = (
   ANALYSIS_EYE_TRACKING_INTERMEDIATE_FILTERED_DIR
)

SUMMARY_FILE = FILTER_QUALITY_REPORT

# ==========================================================
# Filtering thresholds
# ==========================================================

MIN_RELATIVE = -0.5
MAX_RELATIVE = 1.5

# ==========================================================
# Helpers
# ==========================================================

def mark_valid_samples(
    df: pd.DataFrame,
):
    """
    Mark valid gaze samples.

    A sample is considered valid if its
    normalized coordinates fall within
    a reasonable margin around the image.
    """

    df = df.copy()

    #
    # Thresholds
    #

    MIN_X = -0.5
    MAX_X = 1.5

    MIN_Y = -0.5
    MAX_Y = 1.5

    #
    # Valid samples
    #

    valid = (

        df["x_relative"].between(
            MIN_X,
            MAX_X,
        )

        &

        df["y_relative"].between(
            MIN_Y,
            MAX_Y,
        )

    )

    df["valid_sample"] = valid

    #
    # Reason for removal
    #

    df["invalid_reason"] = "valid"

    df.loc[
        df["x_relative"] < MIN_X,
        "invalid_reason",
    ] = "x_too_small"

    df.loc[
        df["x_relative"] > MAX_X,
        "invalid_reason",
    ] = "x_too_large"

    df.loc[
        df["y_relative"] < MIN_Y,
        "invalid_reason",
    ] = "y_too_small"

    df.loc[
        df["y_relative"] > MAX_Y,
        "invalid_reason",
    ] = "y_too_large"

    return df

# ==========================================================
# Process one file
# ==========================================================

def process_file(csv_file: Path):

    df = pd.read_csv(csv_file)

    df = mark_valid_samples(df)

    filtered = df[
        df["valid_sample"]
    ].copy()

    total = len(df)

    kept = len(filtered)

    removed = total - kept

    pct_removed = (
        removed / total
        if total
        else 0
    )

    return filtered, {

        "run_id":
            df["run_id"].iloc[0],

        "image":
            df["image"].iloc[0],

        "condition":
            df["condition"].iloc[0],

        "total_samples":
            total,

        "valid_samples":
            kept,

        "removed_samples":
            removed,

        "pct_removed":
            pct_removed,

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

    if (
        SUMMARY_FILE.exists()
        and
        not overwrite
    ):

        return {

            "processed": 0,

            "skipped": True,

            "summary": SUMMARY_FILE,

        }

    csv_files = sorted(
        INPUT_DIR.glob("*.csv")
    )

    summary_rows = []

    print()

    print(
        f"Found {len(csv_files)} files."
    )

    print()

    for index, csv_file in enumerate(

        csv_files,

        start=1,

    ):

        print(

            f"[{index}/{len(csv_files)}] "

            f"{csv_file.name}"

        )

        filtered, summary = process_file(
            csv_file
        )

        filtered.to_csv(

            OUTPUT_DIR / csv_file.name,

            index=False,

        )

        summary_rows.append(
            summary
        )

    summary_df = pd.DataFrame(
        summary_rows
    )

    summary_df.to_csv(

        SUMMARY_FILE,

        index=False,

    )

    return {

        "processed": len(csv_files),

        "skipped": False,

        "summary": SUMMARY_FILE,

        "table": summary_df,

    }


# ==========================================================
# Summary
# ==========================================================

def print_summary(summary):

    print()

    print("=" * 60)

    print("INVALID SAMPLE FILTER")

    print("=" * 60)

    print()

    if summary["skipped"]:

        print(
            "Summary already exists."
        )

        print(
            "Use --overwrite to regenerate."
        )

        print()

        return

    table = summary["table"]

    print(
        f"Files processed : {summary['processed']}"
    )

    print(
        f"Total samples    : {table['total_samples'].sum()}"
    )

    print(
        f"Valid samples    : {table['valid_samples'].sum()}"
    )

    print(
        f"Removed samples  : {table['removed_samples'].sum()}"
    )

    print(
        f"Mean removed (%) : {100 * table['pct_removed'].mean():.2f}"
    )

    print(
        f"Max removed (%)  : {100 * table['pct_removed'].max():.2f}"
    )

    print()

    print(
        f"Filtered CSVs:\n{OUTPUT_DIR}"
    )

    print()

    print(
        f"Summary:\n{SUMMARY_FILE}"
    )

    print()

    print("=" * 60)


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(

        description=(
            "Filter invalid eye-tracking samples."
        )

    )

    parser.add_argument(

        "--overwrite",

        action="store_true",

        help=(
            "Overwrite existing files."
        ),

    )

    args = parser.parse_args()

    summary = process_dataset(

        overwrite=args.overwrite,

    )

    print_summary(summary)