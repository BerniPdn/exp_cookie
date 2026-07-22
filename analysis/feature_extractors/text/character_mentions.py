"""
Extract character mention features from clean transcripts.

Computes simple discourse-level features describing how
participants refer to the adult characters in the Cookie Theft
images.

Outputs:
    character_mentions.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import spacy

from configs.paths import (
    CLEAN_TRANSCRIPT_DIR,
    SUBJECT_MAPPING,
    CHARACTER_MENTIONS_FILE,
)


# ==========================================================
# Paths
# ==========================================================

OUTPUT_FILE = CHARACTER_MENTIONS_FILE

# ==========================================================
# spaCy
# ==========================================================

nlp = spacy.load(
    "es_core_news_lg",
    disable=[
        "ner",
    ],
)

# ==========================================================
# Lexicons
# ==========================================================

FATHER_WORDS = {
    "padre",
    "papá",
    "papa",
    "papá",
    "hombre",
    "señor",
}

MOTHER_WORDS = {
    "madre",
    "mamá",
    "mama",
    "mujer",
    "señora",
}

CHILD_WORDS = {
    "niño",
    "niña",
    "nene",
    "nena",
    "chico",
    "chica",
    "hijo",
    "hija",
    "hermano",
    "hermana",
}

ENVIRONMENT_WORDS = {
    "cocina",
    "casa",
    "jardín",
    "jardin",
    "ventana",
    "patio",
    "árbol",
    "arbol",
    "pasto",
    "flores",
    "perro",
    "gato",
    "pájaros",
    "pajaros",
}

# ==========================================================
# Helpers
# ==========================================================

def load_subject_mapping():

    with open(
        SUBJECT_MAPPING,
        "r",
        encoding="utf-8",
    ) as f:

        subject_mapping = json.load(f)

    run_mapping = {}

    for subject_id, participant in subject_mapping.items():

        run_mapping[
            participant["run_id"]
        ] = {
            "subject_id": subject_id,
            "gender": participant["gender"],
            "age": participant["age"],
        }

    return run_mapping


def parse_filename(
    filename: str,
):

    stem = Path(filename).stem
    parts = stem.split("_")

    run_id = parts[1]

    if parts[2] == "oasis":

        image = "oasis"
        condition = "_".join(parts[2:-1])

    else:

        image = (
            "new"
            if parts[3] == "nueva"
            else "original"
        )

        condition = "_".join(parts[2:-1])

    return (
        run_id,
        image,
        condition,
    )


# ==========================================================
# Feature extraction
# ==========================================================

def normalize(
    token,
):

    return token.lower_.strip()


def count_mentions(
    doc,
    lexicon,
):

    count = 0

    for token in doc:

        if normalize(token) in lexicon:

            count += 1

    return count


def first_label(
    doc,
    lexicon,
):

    for token in doc:

        word = normalize(token)

        if word in lexicon:

            return word

    return None


def first_adult(
    doc,
):

    for token in doc:

        word = normalize(token)

        if word in FATHER_WORDS:

            return "father"

        if word in MOTHER_WORDS:

            return "mother"

    return "none"


def adult_order(
    doc,
):

    father_index = None
    mother_index = None

    for i, token in enumerate(doc):

        word = normalize(token)

        if (
            father_index is None
            and
            word in FATHER_WORDS
        ):

            father_index = i

        if (
            mother_index is None
            and
            word in MOTHER_WORDS
        ):

            mother_index = i

    if (
        father_index is None
        and
        mother_index is None
    ):

        return "none"

    if father_index is None:

        return "mother_first"

    if mother_index is None:

        return "father_first"

    if father_index < mother_index:

        return "father_first"

    if mother_index < father_index:

        return "mother_first"

    return "simultaneous"


def description_start(
    doc,
):

    first_tokens = list(doc)[:20]

    for token in first_tokens:

        word = normalize(token)

        if (
            word in FATHER_WORDS
            or
            word in MOTHER_WORDS
        ):

            return "adult"

        if word in CHILD_WORDS:

            return "children"

        if word in ENVIRONMENT_WORDS:

            return "environment"

    return "unknown"

# ==========================================================
# Main
# ==========================================================

def process_dataset(
    overwrite=False,
):

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
            "Use --overwrite to replace it."
        )
        print()
        return

    subject_mapping = load_subject_mapping()

    transcripts = sorted(
        CLEAN_TRANSCRIPT_DIR.glob("*.txt")
    )

    rows = []

    print()
    print("=" * 60)
    print("CHARACTER MENTION FEATURES")
    print("=" * 60)
    print()
    print(
        f"Found {len(transcripts)} transcripts."
    )
    print()

    for transcript in transcripts:

        text = transcript.read_text(
            encoding="utf-8"
        ).strip()

        if len(text) == 0:
            continue

        run_id, image, condition = parse_filename(
            transcript.name
        )

        # Skip Oasis trials
        if image == "oasis":
            continue

        if run_id not in subject_mapping:

            print(
                f"Skipping {run_id}: participant not found."
            )

            continue

        participant = subject_mapping[
            run_id
        ]

        doc = nlp(text)

        row = {

            # --------------------------------------
            # Participant
            # --------------------------------------

            "subject_id":
                participant["subject_id"],

            "run_id":
                run_id,

            "gender":
                participant["gender"],

            "age":
                participant["age"],

            # --------------------------------------
            # Experiment
            # --------------------------------------

            "image":
                image,

            "condition":
                condition,

            # --------------------------------------
            # Character features
            # --------------------------------------

            "father_mentions":
                count_mentions(
                    doc,
                    FATHER_WORDS,
                ),

            "mother_mentions":
                count_mentions(
                    doc,
                    MOTHER_WORDS,
                ),

            "father_label":
                first_label(
                    doc,
                    FATHER_WORDS,
                ),

            "mother_label":
                first_label(
                    doc,
                    MOTHER_WORDS,
                ),

            "first_adult":
                first_adult(
                    doc,
                ),

            "adult_order":
                adult_order(
                    doc,
                ),

            "description_start":
                description_start(
                    doc,
                ),
        }

        rows.append(row)

        print(
            f"✓ {transcript.name}"
        )

    df = pd.DataFrame(rows)

    df = df.sort_values(
        by=[
            "run_id",
            "condition",
        ]
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print("=" * 60)
    print("CHARACTER FEATURES FINISHED")
    print("=" * 60)
    print()
    print(
        f"Processed : {len(df)} transcripts"
    )
    print()
    print(
        f"Saved to:\n{OUTPUT_FILE}"
    )
    print()

    return df


# ==========================================================
# CLI
# ==========================================================

def main():

    parser = argparse.ArgumentParser(
        description="Extract character mention features."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output file.",
    )

    args = parser.parse_args()

    process_dataset(
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
