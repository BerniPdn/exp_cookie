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

def is_cookie_trial(
    csv_file: Path,
):
    """
    Determine whether a CSV corresponds to a Cookie Theft trial.

    Parameters
    ----------
    csv_file : Path
        Eye-tracking CSV file.

    Returns
    -------
    bool
        True if the file belongs to a Cookie Theft trial.
    """

    return "lamina" in csv_file.stem.lower()


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

    input_dir = (
        ANALYSIS_EYE_TRACKING_INTERMEDIATE_DIR /
        "filtered"
    )

    input_files = sorted(
        input_dir.glob("*.csv")
    )

    trial_files = [

        file

        for file in input_files

        if is_cookie_trial(file)

    ]

    summary = {

        "total": len(trial_files),

        "processed": 0,

        "skipped": 0,

        "samples": 0,

        "runs": set(),

        "mirrored": 0,

    }

    print(f"\nFound {len(input_files)} eye-tracking files.")

    print(
        f"Ignoring {len(input_files) - len(trial_files)} non-Cookie Theft files."
    )

    print(
        f"Processing {len(trial_files)} Cookie Theft files.\n"
    )

    for index, csv_file in enumerate(
        trial_files,
        start=1,
    ):

        output_file = (
            output_dir /
            csv_file.name
        )

        print(
            f"[{index}/{len(trial_files)}] "
            f"{csv_file.name}"
        )

        if (
            output_file.exists()
            and not overwrite
        ):

            summary["skipped"] += 1

            print("   ⏭ Already processed.")

            continue

        df = pd.read_csv(csv_file)

        df = unmirror_dataframe(df)

        df.to_csv(
            output_file,
            index=False,
        )

        summary["processed"] += 1

        summary["samples"] += len(df)

        summary["mirrored"] += int(
            df["mirrored"].sum()
        )

        summary["runs"].add(
            df["run_id"].iloc[0]
        )

        print("   ✅ Success")

    summary["runs"] = len(summary["runs"])

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

    print(f"Files found      : {summary['total']}")

    print(f"Processed        : {summary['processed']}")

    print(f"Skipped          : {summary['skipped']}")

    print()

    print(f"Runs             : {summary['runs']}")

    print(f"Samples          : {summary['samples']}")

    print(f"Mirrored samples : {summary['mirrored']}")

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