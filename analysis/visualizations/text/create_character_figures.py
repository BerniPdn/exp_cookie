"""
Create figures for Character Mentions metrics.

Generates paired figures for:
    - father_mentions
    - mother_mentions

Generates categorical figures for:
    - first_adult
    - adult_order
    - description_start
    - father_label
    - mother_label
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from configs.paths import (
    TEXT_RESULTS_METRICS_DIR,
    TEXT_RESULTS_VIZ_DIR,
)

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

INPUT_FILE = TEXT_RESULTS_METRICS_DIR / "character_mentions.csv"

OUTPUT_DIR = (
    TEXT_RESULTS_VIZ_DIR
    / "character_mentions"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# ---------------------------------------------------------------------
# Plot settings
# ---------------------------------------------------------------------

COLORS = {
    "original": "#1f77b4",
    "new": "#ff7f0e",
}

PAIR_OFFSET = 0.08
POINT_SIZE = 80
LINE_WIDTH = 1.5

BAR_WIDTH = 0.35

# ---------------------------------------------------------------------
# Category order
# ---------------------------------------------------------------------

CATEGORY_ORDER = {

    "first_adult": [
        "father",
        "mother",
        "none",
    ],

    "adult_order": [
        "father_first",
        "mother_first",
        "simultaneous",
        "none",
    ],

    "description_start": [
        "adult",
        "children",
        "environment",
        "unknown",
    ],

    "father_label": [
        "padre",
        "papá",
        "hombre",
        "señor",
        "none",
    ],

    "mother_label": [
        "madre",
        "mamá",
        "mujer",
        "señora",
        "none",
    ],
}

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def load_data():
    """
    Load Character Mentions CSV.
    """

    return pd.read_csv(INPUT_FILE)


def participant_order(
    df,
    metric,
):
    """
    Order participants by the average value
    of the selected metric.
    """

    return (
        df.groupby("run_id")[metric]
        .mean()
        .sort_values()
        .index
        .tolist()
    )


def save_figure(
    fig,
    path,
):
    """
    Save and close figure.
    """

    plt.tight_layout()

    fig.savefig(
        path,
        dpi=300,
        bbox_inches="tight",
    )

    print(f"Saved: {path.name}")

    plt.close(fig)


def style_axes(ax):
    """
    Apply consistent style.
    """

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(
        frameon=False,
    )


def percentage_table(
    df,
    column,
):
    """
    Returns a table with percentages
    for Original and New images.
    """

    counts = (
        df.groupby(
            [
                "image",
                column,
            ]
        )
        .size()
        .reset_index(name="count")
    )

    totals = (
        counts
        .groupby("image")["count"]
        .transform("sum")
    )

    counts["percentage"] = (
        counts["count"]
        / totals
        * 100
    )

    pivot = (
        counts
        .pivot(
            index=column,
            columns="image",
            values="percentage",
        )
        .fillna(0)
    )

    if column in CATEGORY_ORDER:

        pivot = pivot.reindex(
            CATEGORY_ORDER[column],
            fill_value=0,
        )

    return pivot

# ---------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------


def plot_paired_metric(
    df,
    metric,
    ylabel,
    title,
):
    """
    Create paired participant plot for a numeric metric.
    """

    order = participant_order(df, metric)

    plot_df = df.copy()

    plot_df["run_id"] = pd.Categorical(
        plot_df["run_id"],
        categories=order,
        ordered=True,
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, participant in enumerate(order):

        participant_df = plot_df[
            plot_df["run_id"] == participant
        ]

        original = participant_df[
            participant_df["image"] == "original"
        ]

        new = participant_df[
            participant_df["image"] == "new"
        ]

        if original.empty or new.empty:
            continue

        y_original = original.iloc[0][metric]
        y_new = new.iloc[0][metric]

        # paired line
        ax.plot(
            [i - PAIR_OFFSET, i + PAIR_OFFSET],
            [y_original, y_new],
            color="gray",
            linewidth=LINE_WIDTH,
            zorder=1,
        )

        # original point
        ax.scatter(
            i - PAIR_OFFSET,
            y_original,
            s=POINT_SIZE,
            color=COLORS["original"],
            edgecolor="black",
            zorder=3,
            label="Original" if i == 0 else "",
        )

        # new point
        ax.scatter(
            i + PAIR_OFFSET,
            y_new,
            s=POINT_SIZE,
            color=COLORS["new"],
            edgecolor="black",
            zorder=3,
            label="New" if i == 0 else "",
        )

    ax.set_xticks(range(len(order)))

    ax.set_xticklabels(
        [run_id[:8] for run_id in order],
        rotation=45,
        ha="right",
    )

    ax.set_xlabel("Participant (Run ID)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    style_axes(ax)

    save_figure(
        fig,
        OUTPUT_DIR / f"{metric}.png",
    )


def plot_categorical_metric(
    df,
    column,
    title,
):
    """
    Create grouped percentage bar chart.
    """

    pivot = percentage_table(
        df,
        column,
    )

    categories = pivot.index.tolist()

    x = list(range(len(categories)))

    original = pivot.get(
        "original",
        pd.Series(
            0,
            index=categories,
        ),
    )

    new = pivot.get(
        "new",
        pd.Series(
            0,
            index=categories,
        ),
    )

    fig, ax = plt.subplots(figsize=(8, 6))

    bars_original = ax.bar(
        [i - BAR_WIDTH / 2 for i in x],
        original.values,
        BAR_WIDTH,
        color=COLORS["original"],
        label="Original",
    )

    bars_new = ax.bar(
        [i + BAR_WIDTH / 2 for i in x],
        new.values,
        BAR_WIDTH,
        color=COLORS["new"],
        label="New",
    )

    for bars in [bars_original, bars_new]:

        for bar in bars:

            height = bar.get_height()

            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 1,
                f"{height:.0f}%",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax.set_xticks(x)

    ax.set_xticklabels(
        categories,
        rotation=20,
        ha="right",
    )

    ax.set_ylim(
        0,
        max(
            original.max(),
            new.max(),
            5,
        ) + 15,
    )

    ax.set_ylabel("Participants (%)")
    ax.set_title(title)

    style_axes(ax)

    save_figure(
        fig,
        OUTPUT_DIR / f"{column}.png",
    )

    # ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------


def main():

    print("Loading Character Mentions data...")

    df = load_data()

    print(f"Loaded {len(df)} rows.")

    # -------------------------------------------------------------
    # Numeric metrics
    # -------------------------------------------------------------

    print("Creating paired figures...")

    plot_paired_metric(
        df=df,
        metric="father_mentions",
        ylabel="Father Mentions",
        title="Father Mentions",
    )

    plot_paired_metric(
        df=df,
        metric="mother_mentions",
        ylabel="Mother Mentions",
        title="Mother Mentions",
    )

    # -------------------------------------------------------------
    # Categorical metrics
    # -------------------------------------------------------------

    print("Creating categorical figures...")

    plot_categorical_metric(
        df=df,
        column="first_adult",
        title="First Adult Mentioned",
    )

    plot_categorical_metric(
        df=df,
        column="adult_order",
        title="Order of Adult Mentions",
    )

    plot_categorical_metric(
        df=df,
        column="description_start",
        title="Description Start",
    )

    plot_categorical_metric(
        df=df,
        column="father_label",
        title="First Label Used for Father",
    )

    plot_categorical_metric(
        df=df,
        column="mother_label",
        title="First Label Used for Mother",
    )

    print()
    print("-" * 60)
    print("Character Mention figures created successfully.")
    print(f"Output directory: {OUTPUT_DIR}")
    print("-" * 60)


if __name__ == "__main__":
    main()

