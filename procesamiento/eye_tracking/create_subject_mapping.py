"""
Create subject metadata mapping.

Reads participant_information.csv and creates a JSON mapping
between the subject UUID stored in the eye-tracking JSON and
participant metadata used throughout the project.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime

import pandas as pd

from configs.paths import (
    RAW_EYE_TRACKING_DIR,
    SUBJECT_MAPPING,
    PARTICIPANT_INFORMATION_FILE,
)

# ==========================================================
# Paths
# ==========================================================

INPUT_FILE = PARTICIPANT_INFORMATION_FILE

OUTPUT_FILE = SUBJECT_MAPPING 


# ==========================================================
# Helpers
# ==========================================================

def compute_age(
    birth_date: str,
) -> int:
    """
    Compute age from birth date.
    """

    birth = pd.to_datetime(birth_date)

    today = datetime.today()

    return (
        today.year
        - birth.year
        - (
            (today.month, today.day)
            <
            (birth.month, birth.day)
        )
    )


# ==========================================================
# Main
# ==========================================================

def create_mapping():

    df = pd.read_csv(INPUT_FILE)

    df = df.rename(
        columns={
            "Id sujeto": "subject_id",
            "Id ejecucion": "run_id",
            "Estado": "status",
            "Fecha de nacimiento": "birth_date",
            "Género": "gender",
            "Nivel educativo": "education",
            "Nacionalidad": "nationality",
            "Pais de residencia": "country",
            "Región de residencia": "city",
        }
    )

    mapping = {}

    for _, row in df.iterrows():

        mapping[row["subject_id"]] = {

            "run_id": row["run_id"],

            "gender": row["gender"],

            "birth_date": row["birth_date"],

            "age": compute_age(
                row["birth_date"]
            ),

        }

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
        description="Create subject metadata mapping."
    )

    parser.parse_args()

    create_mapping()


if __name__ == "__main__":

    main()
