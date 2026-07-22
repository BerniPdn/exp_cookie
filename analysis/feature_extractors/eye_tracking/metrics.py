"""
Compute eye-tracking metrics for every trial.

Input
-----
CSV files produced by 03_assign_aois.py

Output
------
eye_tracking_metrics.csv
"""

from pathlib import Path
import argparse

import pandas as pd

from configs.paths import (
    EYE_TRACKING_RESULTS_DIR,
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_DIR,
    EYE_TRACKING_METRICS_DIR,
    EYE_TRACKING_METRICS_FILE,
)

# ==========================================================
# Paths
# ==========================================================

INPUT_DIR = (
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_DIR /
    "with_aois"
)

OUTPUT_DIR = EYE_TRACKING_METRICS_DIR
OUTPUT_FILE = EYE_TRACKING_METRICS_FILE

# ==========================================================
# AOIs
# ==========================================================

OLD_AOIS = [
    "mother",
    "children",
]

NEW_AOIS = [
    "father",
    "mother",
    "children",
    "dog",
]

ALL_AOIS = [
    "father",
    "mother",
    "children",
    "dog",
]

# ==========================================================
# Helper Functions
# ==========================================================

def collapse_sequence(sequence):
    """
    Remove consecutive repeated AOIs.

    Example
    -------
    father father children children dog

    becomes

    father -> children -> dog
    """

    collapsed = []
    previous = None

    for value in sequence:
        if value != previous:
            collapsed.append(value)
            previous = value
    return collapsed


def first_time(df, aoi):
    """
    Return first timestamp at which an AOI is visited.
    """

    subset = df[df["aoi"] == aoi]
    if len(subset):
        return subset["time_ms"].iloc[0]
    return None

# ==========================================================
# Metrics
# ==========================================================

def compute_metrics(csv_file: Path):
    df = pd.read_csv(csv_file)
    valid = df[df["inside_aoi"]].copy()
    run_id = df["run_id"].iloc[0]
    image = df["image"].iloc[0]
    condition = df["condition"].iloc[0]

    if image == "original":
        aois = OLD_AOIS

    else:
        aois = NEW_AOIS

    metrics = {
        "run_id": run_id,
        "image": image,
        "condition": condition,
        "n_samples": len(df),
        "pct_inside_image": (
            (
                df["x_relative"].between(0, 1)
            )
            &
            (
                df["y_relative"].between(0, 1)
            )
        ).mean(),

        "pct_inside_aoi": (
            df["inside_aoi"].mean()
        ),
    }

    counts = (
        valid["aoi"]
        .value_counts()
    )

    proportions = (
        valid["aoi"]
        .value_counts(normalize=True)
    )

    #
    # Percentages over ALL samples
    #

    total_counts = (
        df["aoi"]
        .value_counts()
    )

    total_proportions = (
        df["aoi"]
        .value_counts(
            normalize=True
        )
    )

    #
    # Always create the same columns
    #

    for aoi in ALL_AOIS:

        if aoi in aois:

            #
            # Samples inside AOIs only
            #

            metrics[f"n_{aoi}"] = (
                counts.get(aoi, 0)
            )

            metrics[f"pct_{aoi}"] = (
                proportions.get(aoi, 0.0)
            )

            #
            # Samples over the whole trial
            #

            metrics[f"pct_total_{aoi}"] = (
                total_proportions.get(aoi, 0.0)
            )

        else:
            metrics[f"n_{aoi}"] = 0
            metrics[f"pct_{aoi}"] = 0.0
            metrics[f"pct_total_{aoi}"] = 0.0
        
        #
        # First AOI
        #

        if len(valid):

            metrics["first_aoi"] = (
                valid["aoi"].iloc[0]
            )

        else:

            metrics["first_aoi"] = None

        #
        # First person seen
        #

        people = valid[
            valid["aoi"].isin(
                [
                    "father",
                    "mother",
                    "children",
                ]
            )
        ]

        if len(people):

            metrics["first_person_seen"] = (
                people["aoi"].iloc[0]
            )

        else:

            metrics["first_person_seen"] = None

    #
    # Time to first AOI
    #

    for aoi in ALL_AOIS:

        metrics[
            f"time_to_first_{aoi}"
        ] = first_time(
            valid,
            aoi,
        )

    #
    # AOIs visited
    #

    metrics["n_aois_visited"] = (
        valid["aoi"].nunique()
    )

    #
    # AOI transitions
    #

    if len(valid):

        sequence = (
            valid["aoi"]
            .tolist()
        )

        collapsed = collapse_sequence(
            sequence
        )

        metrics["n_transitions"] = max(
            len(collapsed) - 1,
            0,
        )

        metrics["aoi_sequence"] = (
            " -> ".join(collapsed)
        )

    else:

        metrics["n_transitions"] = 0

        metrics["aoi_sequence"] = ""

    return metrics

# ==========================================================
# Processing
# ==========================================================

def process_metrics(
    overwrite=False,
):
    """
    Compute eye-tracking metrics for all trials.

    Parameters
    ----------
    overwrite : bool
        Overwrite existing output file.

    Returns
    -------
    dict
        Processing summary.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if (
        OUTPUT_FILE.exists()
        and
        not overwrite
    ):

        return {
            "processed": 0,
            "skipped": True,
            "files": 0,
            "output": OUTPUT_FILE,
        }

    csv_files = sorted(
        INPUT_DIR.glob("*.csv")
    )

    rows = []

    print(
        f"\nFound {len(csv_files)} eye-tracking files.\n"
    )

    for index, csv_file in enumerate(
        csv_files,
        start=1,
    ):

        print(
            f"[{index}/{len(csv_files)}] "
            f"{csv_file.name}"
        )

        rows.append(
            compute_metrics(
                csv_file
            )
        )

    metrics = pd.DataFrame(
        rows
    )

    metrics = metrics.sort_values(
        [
            "run_id",
            "image",
        ]
    )

    metrics.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    return {

        "processed": len(metrics),
        "skipped": False,
        "files": len(csv_files),
        "output": OUTPUT_FILE,
    }


# ==========================================================
# Summary
# ==========================================================

def print_summary(
    summary,
):
    """
    Print processing summary.
    """

    print("\n" + "=" * 60)
    print(
        "EYE TRACKING METRICS"
    )
    print("=" * 60)

    if summary["skipped"]:
        print()
        print(
            "Output already exists."
        )
        print(
            "Use --overwrite to regenerate it."
        )

    else:
        print()
        print(
            f"Files processed : {summary['files']}"
        )
        print(
            f"Rows written    : {summary['processed']}"
        )

    print()
    print("Saved to:")
    print(summary["output"])
    print()
    print("=" * 60)


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "Compute eye-tracking metrics."
        )
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "Overwrite existing output."
        ),
    )

    args = parser.parse_args()
    summary = process_metrics(
        overwrite=args.overwrite,
    )

    print_summary(
        summary,
    )
