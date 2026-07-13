"""
Compute Speech Graph metrics.

Reads every clean transcript, computes Speech Graph metrics,
and saves a CSV for downstream analysis.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from nltk import tokenize


import pandas as pd

from configs.paths import (
    CLEAN_TRANSCRIPT_DIR,
    SUBJECT_MAPPING,
    TEXT_RESULTS_METRICS_DIR,
)

from .speech_graphs import SpeechGraph


# ==========================================================
# Paths
# ==========================================================

OUTPUT_FILE = (
    TEXT_RESULTS_METRICS_DIR /
    "speech_graph_metrics.csv"
)


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
    # grabacion_<run_id>_<trial>_<random>
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

    extractor = SpeechGraph(
        lang="es"
    )

    subject_mapping = load_subject_mapping()

    transcripts = sorted(
        CLEAN_TRANSCRIPT_DIR.glob("*.txt")
    )

    rows = []

    print()
    print("=" * 60)
    print("SPEECH GRAPH METRICS")
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

        metrics = extractor.get_speech_graph(
            text
        )

        row = {

            # Participant
            "subject_id":
                participant["subject_id"],
            "run_id":
                run_id,
            "gender":
                participant["gender"],
            "age":
                participant["age"],

            # Experiment
            "image":
                image,
            "condition":
                condition,

            # Text
            "word_count": len(
                tokenize.word_tokenize(
                    text,
                    language="spanish",
                )
            ),
        **metrics,
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
    print("SPEECH GRAPH METRICS FINISHED")
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
        description="Compute Speech Graph metrics."
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