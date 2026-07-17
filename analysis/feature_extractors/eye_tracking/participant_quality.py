"""
Create participant quality report for eye tracking.

Reads the experiment JSON and extracts the WebGazer
validation results for each Cookie Theft image.

The output is one row per participant × image and
is used to decide which eye-tracking data should
be included in downstream analyses.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from configs.paths import (
    SUBJECT_MAPPING,
    get_eye_tracking_json,
    QUALITY_DIR,
)

# ==========================================================
# Paths
# ==========================================================

INPUT_FILE = get_eye_tracking_json()

OUTPUT_FILE = (
    QUALITY_DIR /
    "participant_quality.csv"
)

# ==========================================================
# Helpers
# ==========================================================

def load_subject_mapping() -> dict:
    """
    Load subject -> participant mapping.
    """

    with open(
        SUBJECT_MAPPING,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


def trial_to_image(
    trial: str,
) -> str | None:
    """
    Convert trial name into image label.
    """

    if "lamina_nueva" in trial:

        return "new"

    if "lamina_vieja" in trial:

        return "original"

    return None


# ==========================================================
# Process one participant
# ==========================================================

def process_run(
    run: dict,
    subject_mapping: dict,
) -> list[dict]:
    """
    Extract validation information for one participant.
    """

    subject_id = run["subject"]

    if subject_id not in subject_mapping:

        print(
            f"Warning: subject not found -> {subject_id}"
        )

        return []

    participant = subject_mapping[
        subject_id
    ]

    run_id = participant["run_id"]

    pending_validation = None

    rows = []

    validation_count = 0

    for record in run["records"]:

        if record["type"] != "data":

            continue

        data = record["data"]

        trial = data.get(
            "trial",
            "",
        )

        #
        # Validation
        #

        if trial == "webgazer_validation":

            pending_validation = {

                "validation_accuracy":
                    data.get(
                        "validacion_promedio",
                        None,
                    ),

                "calibration_passed":
                    data.get(
                        "calibracion_aprobada",
                        False,
                    ),

                "calibration_attempts":
                    data.get(
                        "intentos_calibracion",
                        None,
                    ),

            }

            continue

        #
        # Cookie Theft image
        #

        image = trial_to_image(
            trial
        )

        if image is None:

            continue

        #
        # No validation before image
        #

        if pending_validation is None:

            print(
                f"Warning: {run_id} "
                f"{image} has no validation."
            )

            continue

        validation_count += 1

        rows.append(

            {

                "run_id":
                    run_id,

                "subject_id":
                    subject_id,

                "gender":
                    participant["gender"],

                "age":
                    participant["age"],

                "image":
                    image,

                "validation_accuracy":
                    pending_validation[
                        "validation_accuracy"
                    ],

                "validation_threshold":
                    75.0,

                "calibration_passed":
                    pending_validation[
                        "calibration_passed"
                    ],

                "calibration_attempts":
                    pending_validation[
                        "calibration_attempts"
                    ],

                "include_eye_tracking":
                    pending_validation[
                        "calibration_passed"
                    ],

                "exclusion_reason":
                    (
                        "passed"
                        if pending_validation[
                            "calibration_passed"
                        ]
                        else
                        "validation_failed"
                    ),

            }

        )

        #
        # Reset
        #

        pending_validation = None

    if validation_count != 2:

        print(

            f"Warning: {run_id} "

            f"has {validation_count} "

            "validation records."

        )

    return rows

# ==========================================================
# Process dataset
# ==========================================================

def process_dataset(
    overwrite: bool = False,
):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if (
        OUTPUT_FILE.exists()
        and
        not overwrite
    ):

        print()
        print(
            f"{OUTPUT_FILE} already exists."
        )
        print(
            "Use --overwrite to regenerate."
        )
        print()

        return None

    subject_mapping = load_subject_mapping()

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        experiment = json.load(f)

    experiment_runs = experiment[
        "experiment_runs"
    ]

    rows = []

    print()
    print("=" * 60)
    print("PARTICIPANT QUALITY")
    print("=" * 60)
    print()

    print(
        f"Found {len(experiment_runs)} participants."
    )
    print()

    for run in experiment_runs:

        rows.extend(

            process_run(
                run,
                subject_mapping,
            )

        )

    if len(rows) == 0:

        raise RuntimeError(
            "No participant quality information extracted."
        )

    df = pd.DataFrame(rows)

    #
    # Check duplicates
    #

    duplicates = df.duplicated(
        subset=[
            "run_id",
            "image",
        ]
    )

    if duplicates.any():

        raise RuntimeError(
            "Duplicate run_id + image combinations found."
        )

    #
    # Sort
    #

    df = df.sort_values(
        by=[
            "run_id",
            "image",
        ]
    ).reset_index(
        drop=True
    )

    expected_rows = (
        len(experiment_runs) * 2
    )

    if len(df) != expected_rows:

        print()

        print(
            f"Warning: expected {expected_rows} "
            f"rows but found {len(df)}."
        )

        print()

    #
    # Save
    #

    df.to_csv(

        OUTPUT_FILE,

        index=False,

    )

    return df


# ==========================================================
# Summary
# ==========================================================

def print_summary(
    df: pd.DataFrame | None,
):

    if df is None:

        return

    included = df[
        "include_eye_tracking"
    ].sum()

    excluded = len(df) - included

    print()

    print("=" * 60)
    print("PARTICIPANT QUALITY FINISHED")
    print("=" * 60)
    print()

    print(
        f"Participants : {df['run_id'].nunique()}"
    )

    print(
        f"Images       : {len(df)}"
    )

    print()

    print(
        f"Included     : {included}"
    )

    print(
        f"Excluded     : {excluded}"
    )

    print()

    if excluded:

        print("Excluded images:")

        print()

        excluded_df = df[
            ~df["include_eye_tracking"]
        ]

        for row in excluded_df.itertuples():

            print(
                f"  {row.run_id}"
                f" | {row.image}"
                f" | {row.validation_accuracy:.2f}%"
            )

        print()

    print(
        f"Saved to:\n{OUTPUT_FILE}"
    )

    print()

    print("=" * 60)


# ==========================================================
# CLI
# ==========================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Create participant quality report."
        )
    )

    parser.add_argument(

        "--overwrite",

        action="store_true",

        help="Overwrite existing output.",

    )

    args = parser.parse_args()

    df = process_dataset(

        overwrite=args.overwrite,

    )

    print_summary(df)


if __name__ == "__main__":

    main()