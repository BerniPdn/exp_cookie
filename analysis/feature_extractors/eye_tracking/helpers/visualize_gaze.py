"""
Visualize gaze samples over Cookie Theft images.

Overlays:

- stimulus image
- AOIs
- gaze samples

Gray = outside AOIs
Colors = inside AOIs
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

from configs.paths import (
    METADATA_DIR,
    ANALYSIS_EYE_TRACKING_DIR,
    EYE_TRACKING_VISUALIZATIONS_DIR,
    NEW_AOIS_FILE,
    OLD_AOIS_FILE,
    COOKIE_NEW_IMAGE,
    COOKIE_OLD_IMAGE,
)

# ==========================================================
# Paths
# ==========================================================

OUTPUT_DIR = EYE_TRACKING_VISUALIZATIONS_DIR

AOI_FILES = {

    "new": NEW_AOIS_FILE,
    "original": OLD_AOIS_FILE,

}

IMAGE_FILES = {

    "new": COOKIE_NEW_IMAGE,
    "original": COOKIE_OLD_IMAGE,

}

# ==========================================================
# Colors
# ==========================================================

AOI_COLORS = {

    "caregiver": "#d62728",

    "boy + cookies": "#ff7f0e",

    "girl": "#1f77b4",

    "mother": "#9467bd",

    "dog": "#2ca02c",

    "cat": "#8c564b",

}

# ==========================================================
# Helpers
# ==========================================================


def load_image(image_name: str):

    image_path = IMAGE_FILES[image_name]

    image = cv2.imread(str(image_path))

    if image is None:

        raise FileNotFoundError(image_path)

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB,
    )

    return image


def load_aois(image_name: str):

    return pd.read_csv(
        AOI_FILES[image_name]
    )


def color_for(aoi):

    return AOI_COLORS.get(
        aoi,
        "black",
    )

# ==========================================================
# Visualization
# ==========================================================

def visualize(

    csv_file: Path,

):

    df = pd.read_csv(csv_file)

    image_name = df["image"].iloc[0]

    aois = load_aois(image_name)

    image = load_image(image_name)

    h, w = image.shape[:2]

    fig, ax = plt.subplots(

        figsize=(10, 8)

    )

    ax.imshow(image)

    # ------------------------------------------------------
    # Outside AOIs
    # ------------------------------------------------------

    outside = df[df["aoi"].isna()]

    if len(outside):

        ax.scatter(

            outside["x_analysis"] * w,

            outside["y_analysis"] * h,

            s=4,

            color="lightgray",

            alpha=0.18,

            linewidths=0,

            label="Outside AOI",

        )

    # ------------------------------------------------------
    # Inside AOIs
    # ------------------------------------------------------

    inside = df[df["aoi"].notna()]

    for aoi in sorted(inside["aoi"].unique()):

        subset = inside[inside["aoi"] == aoi]

        ax.scatter(

            subset["x_analysis"] * w,

            subset["y_analysis"] * h,

            s=8,

            alpha=0.45,

            linewidths=0,

            color=color_for(aoi),

            label=aoi,

        )

    # ------------------------------------------------------
    # AOIs
    # ------------------------------------------------------

    for _, row in aois.iterrows():

        x = row["x_min"] * w

        y = row["y_min"] * h

        width = (

            row["x_max"]

            - row["x_min"]

        ) * w

        height = (

            row["y_max"]

            - row["y_min"]

        ) * h

        rect = patches.Rectangle(

            (x, y),

            width,

            height,

            linewidth=3,

            edgecolor=color_for(row["aoi"]),

            facecolor=color_for(row["aoi"]),

            alpha=0.12,

        )

        ax.add_patch(rect)

        ax.text(

            x,

            y - 5,

            row["aoi"],

            fontsize=9,

            fontweight="bold",

            color=color_for(row["aoi"]),

        )

            # ------------------------------------------------------
    # Axes
    # ------------------------------------------------------

    ax.set_title(

        csv_file.stem,

        fontsize=14,

        fontweight="bold",

    )

    ax.set_xlim(

        0,

        w,

    )

    ax.set_ylim(

        h,

        0,

    )

    ax.set_aspect(

        "equal",

    )

    ax.grid(

        alpha=0.15,

    )

    ax.legend(

        loc="upper right",

        fontsize=8,

        frameon=True,

    )

    plt.tight_layout()

    # ------------------------------------------------------
    # Save
    # ------------------------------------------------------

    OUTPUT_DIR.mkdir(

        parents=True,

        exist_ok=True,

    )

    output_file = (

        OUTPUT_DIR /

        f"{csv_file.stem}.png"

    )

    plt.savefig(

        output_file,

        dpi=300,

        bbox_inches="tight",

    )

    plt.close()

    print(

        f"Saved: {output_file}"

    )

    # ==========================================================
# Main
# ==========================================================

def main():

    parser = argparse.ArgumentParser(

        description="Visualize gaze samples and AOIs."

    )

    parser.add_argument(

        "csv",

        type=Path,

        help="CSV generated by 03_assign_aois.py",

    )

    args = parser.parse_args()

    if not args.csv.exists():

        raise FileNotFoundError(

            args.csv

        )

    visualize(

        args.csv,

    )

    print()

    print("=" * 60)

    print("VISUALIZATION COMPLETE")

    print("=" * 60)

    print()

    print(

        "Saved to:"

    )

    print(

        OUTPUT_DIR

    )

    print()


if __name__ == "__main__":

    main()
