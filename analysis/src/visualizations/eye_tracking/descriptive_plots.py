"""
Hypothesis-driven eye tracking figures.

The figures in this script are organized around the
research question instead of individual AOIs.

Research question
-----------------
How does changing the caregiver's gender affect
visual attention?
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ==========================================================
# Paths
# ==========================================================

INPUT = Path(
    "data/analysis/eye_tracking/metrics/eye_tracking_metrics.csv"
)

OUTPUT = Path(
    "data/analysis/eye_tracking/figures"
)

OUTPUT.mkdir(
    parents=True,
    exist_ok=True,
)

# ==========================================================
# Load
# ==========================================================

df = pd.read_csv(INPUT)

# ==========================================================
# Derived variables
# ==========================================================

# The caregiver is the mother in the original image
# and the father in the modified image.

df["caregiver_attention"] = np.where(
    df["image"] == "original",
    df["pct_mother"],
    df["pct_father"],
)

df["caregiver_first"] = np.where(
    df["image"] == "original",
    df["first_person_seen"] == "mother",
    df["first_person_seen"] == "father",
)

df["caregiver_time_to_first"] = np.where(
    df["image"] == "original",
    df["time_to_first_mother"],
    df["time_to_first_father"],
)
# ==========================================================
# Style
# ==========================================================

plt.style.use("ggplot")

plt.rcParams["figure.figsize"] = (6,5)
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

# ==========================================================
# Helpers
# ==========================================================

def save(name):

    plt.tight_layout()

    plt.savefig(

        OUTPUT / name,

        bbox_inches="tight",

    )

    plt.close()


def paired(metric):

    return (

        df

        .pivot(

            index="run_id",

            columns="image",

            values=metric,

        )

    )

# ==========================================================
# FIGURE 1
#
# First fixation
#
# Question:
# Who attracts attention first?
# ==========================================================

def plot_first_fixation():

    counts = (

        df

        .groupby("image")["first_person_seen"]

        .value_counts(normalize=True)

        .mul(100)

        .unstack(fill_value=0)

    )

    ax = counts.plot(

        kind="bar",

        stacked=True,

        width=.7,

    )

    ax.set_ylabel("% participants")

    ax.set_xlabel("")

    ax.set_title(

        "First person observed"

    )

    save(

        "01_first_fixation.png"

    )

# ==========================================================
# FIGURE 2
#
# Caregiver attention
#
# Main hypothesis.
#
# Every participant is connected between
# original (mother)
# and
# modified (father)
# ==========================================================

def plot_caregiver_attention():

    wide = paired(

        "caregiver_attention"

    )

    plt.figure(

        figsize=(6,6)

    )

    for _, row in wide.iterrows():

        plt.plot(

            [0,1],

            [

                row["original"],

                row["new"],

            ],

            marker="o",

            linewidth=2,

            alpha=.65,

        )

    # group mean

    plt.scatter(

        0,

        wide["original"].mean(),

        marker="_",

        s=1400,

        linewidth=4,

    )

    plt.scatter(

        1,

        wide["new"].mean(),

        marker="_",

        s=1400,

        linewidth=4,

    )

    plt.xticks(

        [0,1],

        [

            "Mother\n(original)",

            "Father\n(modified)",

        ],

    )

    plt.ylabel(

        "% visual attention"

    )

    plt.title(

        "Attention to the caregiver"

    )

    save(

        "02_caregiver_attention.png"

    )

    # ==========================================================
# FIGURE 3
#
# Children attention
#
# Question:
# Are children still the main visual target?
# ==========================================================

def plot_children_attention():

    wide = paired(
        "pct_children"
    )

    plt.figure(
        figsize=(6,6)
    )

    for _, row in wide.iterrows():

        plt.plot(
            [0,1],
            [
                row["original"],
                row["new"],
            ],
            marker="o",
            linewidth=2,
            alpha=.65,
        )

    plt.scatter(
        0,
        wide["original"].mean(),
        marker="_",
        s=1400,
        linewidth=4,
    )

    plt.scatter(
        1,
        wide["new"].mean(),
        marker="_",
        s=1400,
        linewidth=4,
    )

    plt.xticks(
        [0,1],
        [
            "Original",
            "Modified",
        ],
    )

    plt.ylabel("% visual attention")

    plt.title(
        "Attention to the children"
    )

    save(
        "03_children_attention.png"
    )

# ==========================================================
# FIGURE 4
#
# Attention distribution in the modified image
#
# Question:
# Once the dog is introduced, how is attention
# distributed across the different characters?
# ==========================================================

def plot_modified_attention_distribution():

    modified = df[
        df["image"] == "new"
    ]

    attention = pd.Series({

        "Father": modified["pct_father"].mean(),

        "Children": modified["pct_children"].mean(),

        "Mother": modified["pct_mother"].mean(),

        "Dog": modified["pct_dog"].mean(),

    })

    attention = attention.sort_values()

    plt.figure(
        figsize=(7,5)
    )

    plt.barh(
        attention.index,
        attention.values,
    )

    plt.xlabel(
        "% visual attention"
    )

    plt.title(
        "Distribution of attention in the modified image"
    )

    for i, value in enumerate(attention.values):

        plt.text(

            value + 0.5,

            i,

            f"{value:.1f}%",

            va="center",

        )

    save(
        "04_modified_attention_distribution.png"
    )

    # ==========================================================
# FIGURE 5
#
# Visual exploration
#
# Question:
# Does the modified image encourage broader
# visual exploration?
# ==========================================================

def plot_visual_exploration():

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(10,5),
    )

    variables = [

        (
            "n_aois_visited",
            "AOIs visited",
        ),

        (
            "n_transitions",
            "AOI transitions",
        ),

    ]

    for ax, (metric, title) in zip(
        axes,
        variables,
    ):

        wide = paired(metric)

        for _, row in wide.iterrows():

            ax.plot(

                [0,1],

                [

                    row["original"],

                    row["new"],

                ],

                marker="o",

                alpha=.65,

            )

        ax.scatter(

            0,

            wide["original"].mean(),

            marker="_",

            s=1400,

            linewidth=4,

        )

        ax.scatter(

            1,

            wide["new"].mean(),

            marker="_",

            s=1400,

            linewidth=4,

        )

        ax.set_xticks(

            [0,1],

            [

                "Original",

                "Modified",

            ],

        )

        ax.set_title(title)

    plt.suptitle(

        "Visual exploration"

    )

    save(

        "05_visual_exploration.png"

    )

    # ==========================================================
# FIGURE 6
#
# Time to first fixation on the caregiver
# ==========================================================

def plot_caregiver_time():

    wide = paired(
        "caregiver_time_to_first"
    )

    plt.figure(figsize=(6,6))

    for _, row in wide.iterrows():

        plt.plot(
            [0,1],
            [
                row["original"],
                row["new"],
            ],
            marker="o",
            linewidth=2,
            alpha=.65,
        )

    plt.scatter(
        0,
        wide["original"].mean(),
        marker="_",
        s=1400,
        linewidth=4,
    )

    plt.scatter(
        1,
        wide["new"].mean(),
        marker="_",
        s=1400,
        linewidth=4,
    )

    plt.xticks(
        [0,1],
        [
            "Mother\n(original)",
            "Father\n(modified)",
        ],
    )

    plt.ylabel("Time to first fixation (ms)")

    plt.title(
        "Time to first fixation on the caregiver"
    )

    save(
        "06_caregiver_time.png"
    )

    # ==========================================================
# FIGURE 7
#
# First fixation on caregiver
# ==========================================================

def plot_caregiver_first_fixation():

    summary = (

        df

        .groupby("image")["caregiver_first"]

        .mean()

        *100

    )

    plt.figure(figsize=(5,5))

    plt.bar(

        ["Original","Modified"],

        summary,

    )

    plt.ylabel("% participants")

    plt.ylim(0,100)

    plt.title(
        "Caregiver observed first"
    )

    for i, value in enumerate(summary):

        plt.text(

            i,

            value+2,

            f"{value:.1f}%",

            ha="center",

        )

    save(
        "07_caregiver_first_fixation.png"
    )

    # ==========================================================
# FIGURE 8
#
# Visual hierarchy
# ==========================================================

def plot_attention_hierarchy():

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(12,5),
    )

    images = {

        "original":[

            ("Mother","pct_mother"),

            ("Children","pct_children"),

        ],

        "new":[

            ("Father","pct_father"),

            ("Children","pct_children"),

            ("Mother","pct_mother"),

            ("Dog","pct_dog"),

        ],

    }

    for ax, image in zip(

        axes,

        images,

    ):

        subset = df[
            df.image == image
        ]

        values = {

            label:

            subset[column].mean()

            for label, column

            in images[image]

        }

        values = pd.Series(

            values

        ).sort_values()

        ax.barh(

            values.index,

            values.values,

        )

        ax.set_title(

            image.capitalize()

        )

        ax.set_xlabel(

            "% visual attention"

        )

    plt.suptitle(

        "Visual hierarchy"

    )

    save(

        "08_visual_hierarchy.png"

    )

    # ==========================================================
# Main
# ==========================================================

def main():

    print("=" * 60)
    print("GENERATING DESCRIPTIVE EYE-TRACKING FIGURES")
    print("=" * 60)
    print()

    print("Figure 1: First fixation...")
    plot_first_fixation()

    print("Figure 2: Caregiver attention...")
    plot_caregiver_attention()

    print("Figure 3: Children attention...")
    plot_children_attention()

    print("Figure 4: Visual hierarchy (modified image)...")
    plot_modified_attention_distribution()

    print("Figure 5: Visual exploration...")
    plot_visual_exploration()

    print("Figure 6: Caregiver time to first fixation...")
    plot_caregiver_time()

    print("Figure 7: Caregiver observed first...")
    plot_caregiver_first_fixation()

    print("Figure 8: Visual hierarchy...")
    plot_attention_hierarchy()

    # Uncomment when implemented
    # print("Figure 9: Bubble plot...")
    # plot_attention_bubbles()

    print()
    print("=" * 60)
    print("ALL FIGURES GENERATED")
    print("=" * 60)
    print()
    print(f"Figures saved to:\n{OUTPUT}")
    print()


if __name__ == "__main__":
    main()