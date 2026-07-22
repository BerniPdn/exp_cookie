"""
Audit eye-tracking quality.

Visualizes gaze samples relative to the stimulus position.
"""

from pathlib import Path
import argparse

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

from configs.paths import (
    EYE_TRACKING_AUDIT_DIR,
)

OUTPUT_DIR = EYE_TRACKING_AUDIT_DIR


def audit(csv_file: Path):

    df = pd.read_csv(csv_file)

    inside = (

        (df["x_screen"] >= df["image_x"])

        &

        (df["x_screen"] <= df["image_x"] + df["image_width"])

        &

        (df["y_screen"] >= df["image_y"])

        &

        (df["y_screen"] <= df["image_y"] + df["image_height"])

    )

    fig, ax = plt.subplots(
        figsize=(10, 8)
    )

    #
    # Outside image
    #

    ax.scatter(

        df.loc[~inside, "x_screen"],

        df.loc[~inside, "y_screen"],

        s=8,

        c="red",

        alpha=0.35,

        label="Outside image",

    )

    #
    # Inside image
    #

    ax.scatter(

        df.loc[inside, "x_screen"],

        df.loc[inside, "y_screen"],

        s=8,

        c="lime",

        alpha=0.55,

        label="Inside image",

    )

    #
    # Stimulus rectangle
    #

    rect = patches.Rectangle(

        (

            df["image_x"].iloc[0],

            df["image_y"].iloc[0],

        ),

        df["image_width"].iloc[0],

        df["image_height"].iloc[0],

        linewidth=3,

        edgecolor="cyan",

        facecolor="none",

    )

    ax.add_patch(rect)

    ax.set_title(csv_file.stem)

    ax.invert_yaxis()

    ax.set_aspect("equal")

    ax.legend()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        OUTPUT_DIR /
        f"{csv_file.stem}_audit.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    print(csv_file.name)

    print(df["x_screen"].min(), df["x_screen"].max())
    print(df["y_screen"].min(), df["y_screen"].max())

    print(ax.get_xlim())
    print(ax.get_ylim())

    plt.close()

    print(f"Saved: {output_file}")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "csv",
        type=Path,
    )

    args = parser.parse_args()

    audit(args.csv)


if __name__ == "__main__":

    main()
