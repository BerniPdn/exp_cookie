"""
Project paths.

This module centralizes every directory and file path used
throughout the processing and analysis pipeline.
"""

from pathlib import Path

# ==========================================================
# Project root
# ==========================================================

# exp_cookie/
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ==========================================================
# Data directories
# ==========================================================

DATA_DIR = PROJECT_ROOT / "data"

RAW_DIR = DATA_DIR / "raw"

PROCESSED_DIR = DATA_DIR / "processed"

RESULTS_DIR = DATA_DIR / "results"

METADATA_DIR = DATA_DIR / "metadata"

FEATURES_DIR = DATA_DIR / "features"


# ==========================================================
# Raw data
# ==========================================================

RAW_VIDEO_DIR = RAW_DIR / "videos"

RAW_EYE_TRACKING_DIR = RAW_DIR / "eye_tracking"

# ==========================================================
# Processed data
# ==========================================================

PROCESSED_VIDEO_DIR = (
    PROCESSED_DIR /
    "videos"
)

PROCESSED_AUDIO_DIR = (
    PROCESSED_DIR /
    "audio"
)

PROCESSED_TRANSCRIPT_DIR = (
    PROCESSED_DIR / "transcripts"
)

CLEAN_TRANSCRIPT_DIR = (
    PROCESSED_TRANSCRIPT_DIR / "clean"
)

TIMESTAMP_TRANSCRIPT_DIR = (
    PROCESSED_TRANSCRIPT_DIR / "timestamps"
)

PROCESSED_EYE_TRACKING_DIR = (
    PROCESSED_DIR /
    "eye_tracking"
)

# ==========================================================
# Analysis data
# ==========================================================


ANALYSIS_DIR = DATA_DIR / "analysis"

ANALYSIS_EYE_TRACKING_DIR = (
    ANALYSIS_DIR /
    "eye_tracking"
)

ANALYSIS_EYE_TRACKING_INTERMEDIATE_DIR = (
    ANALYSIS_EYE_TRACKING_DIR /
    "intermediate"
)

# ==========================================================
# Results
# ==========================================================

QUALITY_DIR = (
    RESULTS_DIR /
    "quality"
)

FEATURES_DIR = (
    RESULTS_DIR /
    "features"
)

FIGURES_DIR = (
    RESULTS_DIR /
    "figures"
)

TABLES_DIR = (
    RESULTS_DIR /
    "tables"
)


# ==========================================================
# Quality reports
# ==========================================================

VIDEO_QUALITY_REPORT = (
    QUALITY_DIR /
    "video_quality.csv"
)

EYE_TRACKING_QUALITY_REPORT = (
    QUALITY_DIR /
    "eye_tracking_quality.csv"
)

# ==========================================================
# Metadata
# ==========================================================
METADATA_DIR = DATA_DIR / "metadata"

SUBJECT_MAPPING = (
    METADATA_DIR /
    "subject_to_run.json"
)

# ==========================================================
# Helpers
# ==========================================================

def get_eye_tracking_json() -> Path:

    json_files = list(
        RAW_EYE_TRACKING_DIR.glob("*.json")
    )

    if len(json_files) == 0:

        raise FileNotFoundError(
            "No eye-tracking JSON found."
        )

    if len(json_files) > 1:

        raise RuntimeError(
            "More than one eye-tracking JSON found."
        )

    return json_files[0]