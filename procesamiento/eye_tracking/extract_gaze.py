"""
Extract normalized gaze data from a single WebGazer trial.

This module converts one eye-tracking trial into a normalized
pandas DataFrame ready for downstream analysis.

It does NOT save CSV files.
That responsibility belongs to process_eye_tracking.py.
"""

from __future__ import annotations

import math

import pandas as pd


# ==========================================================
# Configuration
# ==========================================================

# Percentage of the image size accepted as a tolerance
# outside the image boundaries.
MARGIN_RATIO = 0.05


# ==========================================================
# Helper Functions
# ==========================================================

def normalize_coordinate(
    value: float,
    origin: float,
    size: float,
) -> float:
    """
    Normalize a screen coordinate.

    Parameters
    ----------
    value : float
        Screen coordinate.

    origin : float
        Image origin.

    size : float
        Image width or height.

    Returns
    -------
    float
        Coordinate normalized to the [0, 1] range.
    """

    return (value - origin) / size


def is_inside_image(
    x_relative: float,
    y_relative: float,
) -> bool:
    """
    Determine whether a normalized point lies
    inside the displayed image.
    """

    return (
        0.0 <= x_relative <= 1.0
        and
        0.0 <= y_relative <= 1.0
    )


def is_inside_margin(
    x_relative: float,
    y_relative: float,
    margin: float = MARGIN_RATIO,
) -> bool:
    """
    Determine whether a point lies inside the image
    after applying a tolerance margin.
    """

    return (
        -margin <= x_relative <= 1.0 + margin
        and
        -margin <= y_relative <= 1.0 + margin
    )


def distance_to_image(
    x_screen: float,
    y_screen: float,
    image_x: float,
    image_y: float,
    image_width: float,
    image_height: float,
) -> float:
    """
    Compute the minimum Euclidean distance (pixels)
    between one gaze sample and the image.

    Returns
    -------
    float
        Distance in pixels.

        Returns 0 when the point is already
        inside the image.
    """

    dx = max(
        image_x - x_screen,
        0,
        x_screen - (image_x + image_width),
    )

    dy = max(
        image_y - y_screen,
        0,
        y_screen - (image_y + image_height),
    )

    return round(math.sqrt(dx * dx + dy * dy), 2)


def parse_trial_name(
    trial_name: str,
) -> tuple[str, str]:
    """
    Split the trial name into image and condition.

    Parameters
    ----------
    trial_name : str

    Returns
    -------
    tuple[str, str]

        image
            original | new

        condition
            Original trial name.
    """

    trial = trial_name.lower()

    if "nueva" in trial:
        image = "new"
    else:
        image = "original"

    return image, trial


# ==========================================================
# Main Function
# ==========================================================

def extract_gaze(
    run_id: str,
    validation_score: float,
    calibration_passed: bool,
    calibration_attempts: int,
    trial_data: dict,
) -> pd.DataFrame:
    """
    Convert one WebGazer trial into a normalized DataFrame.

    Parameters
    ----------
    run_id : str
        Experiment run identifier.

    validation_score : float
        Average validation accuracy.

    calibration_passed : bool
        Calibration status.

    calibration_attempts : int
        Number of calibration attempts.

    trial_data : dict
        Trial dictionary from the raw JSON.

    Returns
    -------
    pandas.DataFrame
    """

    if "webgazer_data" not in trial_data:
        return pd.DataFrame()

    if "imagen_rect" not in trial_data:
        return pd.DataFrame()

    image_x = trial_data["imagen_rect"]["x"]
    image_y = trial_data["imagen_rect"]["y"]

    image_width = trial_data["imagen_rect"]["width"]
    image_height = trial_data["imagen_rect"]["height"]

    image, condition = parse_trial_name(
        trial_data["trial"]
    )

    rows = []

    for sample_index, sample in enumerate(
        trial_data["webgazer_data"]
    ):

        x_screen = sample["x"]
        y_screen = sample["y"]

        x_relative = normalize_coordinate(
            x_screen,
            image_x,
            image_width,
        )

        y_relative = normalize_coordinate(
            y_screen,
            image_y,
            image_height,
        )

                # Skip incomplete samples.
        if (
            "t" not in sample
            or "x" not in sample
            or "y" not in sample
        ):
            continue

        rows.append(
            {
                # ==================================================
                # Metadata
                # ==================================================

                "run_id": run_id,

                "image": image,

                "condition": condition,

                "sample_index": sample_index,

                "time_ms": sample["t"],

                # ==================================================
                # Original screen coordinates
                # ==================================================

                "x_screen": x_screen,

                "y_screen": y_screen,

                # ==================================================
                # Image geometry
                # ==================================================

                "image_x": image_x,

                "image_y": image_y,

                "image_width": image_width,

                "image_height": image_height,

                # ==================================================
                # Normalized coordinates
                # ==================================================

                "x_relative": round(x_relative, 6),

                "y_relative": round(y_relative, 6),

                # ==================================================
                # Calibration
                # ==================================================

                "validation_score": validation_score,

                "calibration_passed": calibration_passed,

                "calibration_attempts": calibration_attempts,
            }
        )

    if len(rows) == 0:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # Keep a consistent column order across every dataset.
    column_order = [

        # Metadata
        "run_id",
        "image",
        "condition",
        "sample_index",
        "time_ms",

        # Raw coordinates
        "x_screen",
        "y_screen",

        # Image geometry
        "image_x",
        "image_y",
        "image_width",
        "image_height",

        # Normalized coordinates
        "x_relative",
        "y_relative",

        # Calibration
        "validation_score",
        "calibration_passed",
        "calibration_attempts",
    ]

    df = df[column_order]

    return df