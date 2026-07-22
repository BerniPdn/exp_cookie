"""
Create paired participant figures for Speech Graph metrics.

Example
-------
python3 -m analysis.visualizations.text.create_figures \
    --metric word_count \
    --ylabel "Word Count" \
    --title "Word Count"
"""

import argparse

import matplotlib.pyplot as plt
import pandas as pd

from configs.paths import (
    SPEECH_GRAPH_METRICS_FILE,
    SPEECH_GRAPH_FIGURES_DIR,
)

INPUT_FILE = SPEECH_GRAPH_METRICS_FILE
OUTPUT_DIR = SPEECH_GRAPH_FIGURES_DIR


def plot_metric(df, metric, ylabel=None, title=None, save_path=None):
    if metric not in df.columns:
        raise ValueError(f"Unknown metric: {metric}")

    # Order participants by average word count
    order = (
        df.groupby("run_id")["word_count"]
        .mean()
        .sort_values()
        .index
        .tolist()
    )

    plot_df = df.copy()
    plot_df["run_id"] = pd.Categorical(
        plot_df["run_id"],
        categories=order,
        ordered=True,
    )

    colors = {
        "original": "#1f77b4",
        "new": "#ff7f0e",
    }

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, participant in enumerate(order):
        sub = plot_df[plot_df["run_id"] == participant]

        old = sub[sub["image"] == "original"]
        new = sub[sub["image"] == "new"]

        if len(old) == 0 or len(new) == 0:
            continue

        y_old = old.iloc[0][metric]
        y_new = new.iloc[0][metric]

        # Connect paired observations
        ax.plot(
            [i - 0.08, i + 0.08],
            [y_old, y_new],
            color="gray",
            linewidth=1.5,
            zorder=1,
        )

        # Original image
        ax.scatter(
            i - 0.08,
            y_old,
            s=80,
            color=colors["original"],
            edgecolor="black",
            label="Original" if i == 0 else "",
            zorder=3,
        )

        # New image
        ax.scatter(
            i + 0.08,
            y_new,
            s=80,
            color=colors["new"],
            edgecolor="black",
            label="New" if i == 0 else "",
            zorder=3,
        )

    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(
        [str(run_id)[:8] for run_id in order],
        rotation=45,
        ha="right",
    )

    ax.set_xlabel("Participant (Run ID)")
    ax.set_ylabel(ylabel or metric)
    ax.set_title(title or metric)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(frameon=False)

    plt.tight_layout()

    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved: {save_path}")

    plt.show()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--metric",
        required=True,
        help="Column name in speech_graph_metrics.csv",
    )

    parser.add_argument(
        "--ylabel",
        default=None,
        help="Y-axis label",
    )

    parser.add_argument(
        "--title",
        default=None,
        help="Figure title",
    )

    args = parser.parse_args()

    df = pd.read_csv(INPUT_FILE)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output = OUTPUT_DIR / f"{args.metric}.png"

    plot_metric(
        df=df,
        metric=args.metric,
        ylabel=args.ylabel,
        title=args.title,
        save_path=output,
    )


if __name__ == "__main__":
    main()
