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

# Experiment assets and local development output
EXPERIMENT_DIR = PROJECT_ROOT / "experimento"
LOCAL_RECORDINGS_DIR = EXPERIMENT_DIR / "local_recordings"

COOKIE_OLD_IMAGE = EXPERIMENT_DIR / "cookie_vieja_original.png"
COOKIE_NEW_IMAGE = EXPERIMENT_DIR / "cookie_nueva_original.png"


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

MANUAL_TRANSCRIPT_DIR = (
    PROCESSED_TRANSCRIPT_DIR / "corregidas_manualmente"
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

ANALYSIS_EYE_TRACKING_INTERMEDIATE_UNIMIRROR_DIR = (
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_DIR /
    "unmirror"
)

ANALYSIS_EYE_TRACKING_INTERMEDIATE_AOIS_DIR = (
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_DIR /
    "with_aois"
)

ANALYSIS_EYE_TRACKING_INTERMEDIATE_FILTERED_DIR = (
    ANALYSIS_EYE_TRACKING_INTERMEDIATE_DIR /
    "filtered"
)

# ==========================================================
# Results
# ==========================================================

EYE_TRACKING_RESULTS_DIR = (
    RESULTS_DIR /
    "eye_tracking"
)

QUALITY_DIR = (
    RESULTS_DIR /
    'quality'
)

TEXT_RESULTS_DIR = (
     RESULTS_DIR /
    "text"
)

TEXT_RESULTS_METRICS_DIR = (
    TEXT_RESULTS_DIR /
    "metrics"
)

TEXT_RESULTS_VIZ_DIR = (
    TEXT_RESULTS_DIR /
    "viz"
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

FILTER_QUALITY_REPORT = (
    QUALITY_DIR / 
    "eye_tracking_filter-csv"
)

# ==========================================================
# Metadata
# ==========================================================
METADATA_DIR = DATA_DIR / "metadata"

SUBJECT_MAPPING = (
    METADATA_DIR /
    "subject_mapping.json"
)

PARTICIPANT_INFORMATION_FILE = (
    RAW_EYE_TRACKING_DIR /
    "participant_information.csv"
)

OLD_AOIS_FILE = METADATA_DIR / "aois_lamina_vieja.csv"
NEW_AOIS_FILE = METADATA_DIR / "aois_lamina_nueva.csv"

# ==========================================================
# Analysis outputs
# ==========================================================

SPEECH_GRAPH_METRICS_FILE = TEXT_RESULTS_METRICS_DIR / "speech_graph_metrics.csv"
CHARACTER_MENTIONS_FILE = TEXT_RESULTS_METRICS_DIR / "character_mentions.csv"
SPEECH_GRAPH_FIGURES_DIR = TEXT_RESULTS_VIZ_DIR / "speech_graph"
CHARACTER_MENTIONS_FIGURES_DIR = TEXT_RESULTS_VIZ_DIR / "character_mentions"

EYE_TRACKING_METRICS_DIR = EYE_TRACKING_RESULTS_DIR / "metrics"
EYE_TRACKING_METRICS_FILE = EYE_TRACKING_METRICS_DIR / "eye_tracking_metrics.csv"
EYE_TRACKING_HEATMAPS_DIR = EYE_TRACKING_RESULTS_DIR / "heatmaps"
INDIVIDUAL_HEATMAPS_DIR = EYE_TRACKING_HEATMAPS_DIR / "individual"
AVERAGE_HEATMAPS_DIR = EYE_TRACKING_HEATMAPS_DIR / "average"
EYE_TRACKING_DESCRIPTIVE_PLOTS_DIR = EYE_TRACKING_RESULTS_DIR / "descriptive_plots"
EYE_TRACKING_AUDIT_DIR = EYE_TRACKING_RESULTS_DIR / "audit"
EYE_TRACKING_VISUALIZATIONS_DIR = ANALYSIS_EYE_TRACKING_DIR / "visualizations"

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
