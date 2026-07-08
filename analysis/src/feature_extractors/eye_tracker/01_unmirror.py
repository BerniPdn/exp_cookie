"""
Convert mirrored eye-tracking coordinates into a common analysis space.

This script creates analysis-ready gaze coordinates by correcting
horizontally mirrored stimuli. The original processed data are never
modified; instead, new columns are added for downstream analyses.

New columns:
- mirrored
- x_analysis
- y_analysis
"""

from pathlib import Path
import argparse

import pandas as pd

from configs.paths import (
    PROCESSED_EYE_TRACKING_DIR,
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_DIR,
)

# ==========================================================
# Helper Functions
# ==========================================================

def is_mirrored(
    condition: str,
):
    """
    Determine whether a stimulus was presented mirrored.

    Parameters
    ----------
    condition : str
        Experimental condition name.

    Returns
    -------
    bool
        True if the stimulus was mirrored.
    """

    return "invertida" in condition.lower()


# ==========================================================
# Coordinate Transformation
# ==========================================================

def unmirror_dataframe(
    df: pd.DataFrame,
):
    """
    Convert mirrored gaze coordinates into a common reference frame.

    Parameters
    ----------
    df : pandas.DataFrame
        Gaze samples produced during preprocessing.

    Returns
    -------
    pandas.DataFrame
        DataFrame including analysis coordinates.
    """

    df = df.copy()

    # ------------------------------------------------------
    # Detect mirrored stimulus
    # ------------------------------------------------------

    df["mirrored"] = (
        df["condition"].fillna("")
        .apply(is_mirrored)
    )

    # ------------------------------------------------------
    # Canonical X coordinate
    # ------------------------------------------------------

    df["x_analysis"] = df["x_relative"]

    mirrored_mask = df["mirrored"]

    df.loc[
        mirrored_mask,
        "x_analysis",
    ] = (
        1
        - df.loc[
            mirrored_mask,
            "x_relative",
        ]
    )

    # ------------------------------------------------------
    # Y coordinate never changes
    # ------------------------------------------------------

    df["y_analysis"] = df["y_relative"]

    return df

# ==========================================================
# Processing
# ==========================================================

def process_unmirror(
    overwrite=False,
):
    """
    Generate analysis-ready gaze coordinates.

    Parameters
    ----------
    overwrite : bool
        Overwrite existing output.

    Returns
    -------
    dict
        Processing summary.
    """

    output_dir = ANALYSIS_EYE_TRACKING_INTERMEDIATE_DIR

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_dir /
        "gaze_samples_unmirrored.csv"
    )

    if (
        output_file.exists()
        and not overwrite
    ):

        return {
            "samples": 0,
            "runs": 0,
            "mirrored": 0,
            "output": output_file,
            "skipped": True,
        }

    print("\nLoading gaze samples...\n")

    df = pd.read_csv(
        PROCESSED_EYE_TRACKING_DIR
    )

    print(
        f"Loaded {len(df)} gaze samples."
    )

    print(
        "\nApplying mirror correction...\n"
    )

    df = unmirror_dataframe(df)

    df.to_csv(
        output_file,
        index=False,
    )

    summary = {

        "samples": len(df),

        "runs": df["run_id"].nunique(),

        "mirrored": int(
            df["mirrored"].sum()
        ),

        "output": output_file,

        "skipped": False,

    }

    return summary

# ==========================================================
# Summary
# ==========================================================

def print_summary(summary):
    """
    Print processing summary.

    Parameters
    ----------
    summary : dict
        Processing summary.
    """

    if summary["skipped"]:

        print("\n" + "=" * 55)

        print("UNMIRROR")

        print("=" * 55)

        print("Output already exists.")

        print("Use --overwrite to regenerate it.")

        print("=" * 55)

        return

    print("\n" + "=" * 55)

    print("UNMIRROR COMPLETE")

    print("=" * 55)

    print(f"Runs processed   : {summary['runs']}")

    print(f"Samples          : {summary['samples']}")

    print(f"Mirrored samples : {summary['mirrored']}")

    print()

    print(f"Output:")

    print(summary["output"])

    print("=" * 55)


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(

        description=(
            "Convert mirrored eye-tracking coordinates "
            "into a common analysis space."
        )

    )

    parser.add_argument(

        "--overwrite",

        action="store_true",

        help="Overwrite existing output file.",

    )

    args = parser.parse_args()

    summary = process_unmirror(

        overwrite=args.overwrite,

    )

    print_summary(summary)