"""
Run the complete text feature-extraction and visualization pipeline.
"""

from __future__ import annotations

import argparse

import pandas as pd

from analysis.feature_extractors.text.character_mentions import (
    process_dataset as process_character_mentions,
)
from analysis.feature_extractors.text.speech_graph_metrics import (
    process_dataset as process_speech_graph_metrics,
)
from analysis.visualizations.text.create_character_figures import (
    main as create_character_figures,
)
from analysis.visualizations.text.create_speech_graph_figures import (
    OUTPUT_DIR as SPEECH_GRAPH_FIGURES_DIR,
    INPUT_FILE as SPEECH_GRAPH_METRICS_FILE,
    plot_metric,
)


METADATA_COLUMNS = {
    "subject_id",
    "run_id",
    "gender",
    "age",
    "image",
    "condition",
}


def create_speech_graph_figures() -> None:
    """Generate one paired figure for every numeric speech-graph metric."""

    dataframe = pd.read_csv(SPEECH_GRAPH_METRICS_FILE)
    SPEECH_GRAPH_FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    metrics = [
        column
        for column in dataframe.select_dtypes(include="number").columns
        if column not in METADATA_COLUMNS
    ]

    print(f"Generating {len(metrics)} speech-graph figures.")

    for metric in metrics:
        plot_metric(
            df=dataframe,
            metric=metric,
            title=metric.replace("_", " ").title(),
            save_path=SPEECH_GRAPH_FIGURES_DIR / f"{metric}.png",
            show=False,
        )


def run_pipeline(
    overwrite: bool = False,
) -> None:
    """Run every text analysis module in dependency order."""

    print()
    print("=" * 60)
    print("TEXT ANALYSIS PIPELINE")
    print("=" * 60)

    print("\n[1/4] Compute speech-graph metrics")
    process_speech_graph_metrics(overwrite=overwrite)

    print("\n[2/4] Extract character-mention features")
    process_character_mentions(overwrite=overwrite)

    print("\n[3/4] Create speech-graph figures")
    create_speech_graph_figures()

    print("\n[4/4] Create character-mention figures")
    create_character_figures()

    print()
    print("=" * 60)
    print("TEXT PIPELINE COMPLETE")
    print("=" * 60)
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the complete text analysis pipeline.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing feature tables before creating figures.",
    )
    args = parser.parse_args()

    run_pipeline(overwrite=args.overwrite)


if __name__ == "__main__":
    main()
