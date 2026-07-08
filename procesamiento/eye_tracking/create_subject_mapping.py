"""
Create subject -> run mapping.

Reads participant_information.csv and creates a JSON mapping
between the subject UUID stored in the eye-tracking JSON and
the experiment run_id used throughout the rest of the project.
"""

from __future__ import annotations

import argparse
import json

import pandas as pd

from configs.paths import (
    RAW_EYE_TRACKING_DIR,
    SUBJECT_MAPPING,
)

# ==========================================================
# Paths
# ==========================================================

INPUT_FILE = (
    RAW_EYE_TRACKING_DIR /
    "participant_information.csv"
)

OUTPUT_FILE = (
    SUBJECT_MAPPING
)


# ==========================================================
# Main
# ==========================================================

def create_mapping():

    df = pd.read_csv(
        INPUT_FILE,
        header=None,
    )

    df.columns = [

        "subject_id",

        "run_id",

        "status",

        "birth_date",

        "gender",

        "education",

        "nationality",

        "country",

        "city",

    ]

    mapping = dict(

        zip(

            df["subject_id"],

            df["run_id"],

        )

    )

    OUTPUT_FILE.parent.mkdir(

        parents=True,

        exist_ok=True,

    )

    with open(

        OUTPUT_FILE,

        "w",

        encoding="utf-8",

    ) as f:

        json.dump(

            mapping,

            f,

            indent=4,

            ensure_ascii=False,

        )

    print()

    print("=" * 60)

    print("SUBJECT MAPPING CREATED")

    print("=" * 60)

    print()

    print(f"Participants : {len(mapping)}")

    print()

    print(f"Saved to:\n{OUTPUT_FILE}")

    print()

# ==========================================================
# CLI
# ==========================================================

def main():

    parser = argparse.ArgumentParser(
        description="Create subject -> run mapping."
    )

    parser.parse_args()

    create_mapping()


if __name__ == "__main__":

    main()