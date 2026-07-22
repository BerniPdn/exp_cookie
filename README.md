# exp_cookie

`exp_cookie` is a multimodal research project that studies potential gender
bias in the Cookie Theft picture. The jsPsych and WebGazer experiment collects
video and audio recordings, eye-tracking data, and experimental metadata. This
repository includes the experiment, data preprocessing, and text and
eye-tracking analyses.

## Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Project layout and input data](#project-layout-and-input-data)
- [Recommended execution](#recommended-execution)
- [Running individual stages](#running-individual-stages)
- [Generated outputs](#generated-outputs)
- [Local experiment server](#local-experiment-server)
- [Troubleshooting](#troubleshooting)

## Requirements

- Python 3.10 or later.
- [FFmpeg](https://ffmpeg.org/) and `ffprobe` available from the command line.
- An internet connection the first time Faster-Whisper and the spaCy language
  model are downloaded.

Confirm that FFmpeg is available before proceeding:

```bash
ffmpeg -version
ffprobe -version
```

## Installation

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

Download the language resources used by the text-analysis scripts:

```bash
python3 -m spacy download es_core_news_lg
python3 -m nltk.downloader punkt punkt_tab
```

> Run every command in this README from the repository root (`exp_cookie/`).
> This ensures Python can resolve imports and the centralized paths defined in
> `configs/paths.py`.

## Project layout and input data

```text
exp_cookie/
├── experimento/                  # jsPsych experiment and image stimuli
├── procesamiento/                # Video, audio, and raw gaze preprocessing
│   └── pipelines/
├── analysis/
│   ├── feature_extractors/       # Feature extraction modules
│   ├── visualizations/           # Figures and heatmaps
│   └── pipelines/                # Analysis and project-wide pipelines
├── configs/paths.py              # Single source of project paths
└── data/
    ├── raw/                      # Input data
    ├── processed/                # Preprocessed data
    ├── metadata/                 # Subject mapping and AOIs
    └── results/                  # Metrics, reports, and figures
```

Before running the complete workflow, make sure these files are available:

```text
data/raw/videos/*.webm
data/raw/eye_tracking/eye_tracking.json
data/raw/eye_tracking/participant_information.csv
data/metadata/subject_mapping.json
data/metadata/aois_lamina_vieja.csv
data/metadata/aois_lamina_nueva.csv
```

Create `subject_mapping.json` from the participant information file with:

```bash
python3 -m procesamiento.eye_tracking.create_subject_mapping
```

Both AOI files must exist before running eye-tracking analysis. They can be
created with the AOI annotation tool or reused from `data/metadata/`.

## Recommended execution

Run the complete workflow—preprocessing, text analysis, and eye-tracking
analysis—with:

```bash
python3 -m analysis.pipelines.pipeline_all
```

Its internal order is:

```text
video → audio extraction and transcription → raw eye-tracking processing
      → text analysis
      → eye-tracking analysis
```

To recompute existing outputs, add `--overwrite`:

```bash
python3 -m analysis.pipelines.pipeline_all --overwrite
```

To also generate individual heatmaps, group heatmaps, and descriptive
eye-tracking plots:

```bash
python3 -m analysis.pipelines.pipeline_all --with-visualizations
```

Eye-tracking visualizations are optional because they can take longer than
feature extraction.

## Running individual stages

### Preprocessing

Run all preprocessing modalities:

```bash
python3 -m procesamiento.pipelines.process_all_pipeline
```

Or run each modality independently:

```bash
python3 -m procesamiento.pipelines.process_video_pipeline
python3 -m procesamiento.pipelines.process_audio_pipeline
python3 -m procesamiento.pipelines.process_eye_tracking_pipeline
```

Preprocessing performs the following steps:

1. Normalizes WEBM videos and creates a video quality report.
2. Extracts WAV audio and transcribes it with Faster-Whisper.
3. Converts WebGazer data into one CSV file per participant and trial.

### Text analysis

The text pipeline computes speech-graph and character-mention features, then
creates their visualizations:

```bash
python3 -m analysis.pipelines.pipeline_fe_text
```

Use `--overwrite` to recalculate the feature tables before regenerating the
figures:

```bash
python3 -m analysis.pipelines.pipeline_fe_text --overwrite
```

The pipeline uses clean transcripts in
`data/processed/transcripts/clean/`. Word clouds are independent and use
manually corrected transcripts in
`data/processed/transcripts/corregidas_manualmente/`:

```bash
python3 -m analysis.visualizations.text.word_clouds
```

### Eye-tracking analysis

The eye-tracking pipeline performs quality control, invalid-sample filtering,
coordinate unmirroring, AOI assignment, and metric calculation:

```bash
python3 -m analysis.pipelines.pipeline_fe_eye_tracking
```

To regenerate its outputs:

```bash
python3 -m analysis.pipelines.pipeline_fe_eye_tracking --overwrite
```

Run visualizations independently after metrics have been produced:

```bash
python3 -m analysis.visualizations.eye_tracking.heatmaps.generate_all_heatmaps
python3 -m analysis.visualizations.eye_tracking.heatmaps.generate_group_heatmaps
python3 -m analysis.visualizations.eye_tracking.descriptive_plots
```

## Generated outputs

| Stage | Main location |
| --- | --- |
| Normalized videos | `data/processed/videos/` |
| WAV audio and transcripts | `data/processed/audio/`, `data/processed/transcripts/` |
| Processed eye-tracking data | `data/processed/eye_tracking/` |
| Quality reports | `data/results/quality/` |
| Text metrics | `data/results/text/metrics/` |
| Text figures | `data/results/text/viz/` |
| Eye-tracking metrics | `data/results/eye_tracking/metrics/` |
| Eye-tracking heatmaps and plots | `data/results/eye_tracking/` |

## Local experiment server

The local server is optional and lets you test the experiment without
DataPruebas:

```bash
python3 -m experimento.servidor_local
```

To use it, enable the commented local configuration in
`experimento/runtime.js`. Local recordings are saved in
`experimento/local_recordings/`.

## Troubleshooting

**`ModuleNotFoundError: No module named 'configs'`**

Run the command from the repository root and use the documented `python3 -m`
syntax.

**Faster-Whisper tries to download a model or fails without internet access**

The first transcription downloads the `medium` model. Connect to the internet
and repeat the command; subsequent runs use the local copy.

**spaCy cannot find `es_core_news_lg`**

Install the language model:

```bash
python3 -m spacy download es_core_news_lg
```

**NLTK fails while tokenizing**

Install its required resources:

```bash
python3 -m nltk.downloader punkt punkt_tab
```

**Videos, gaze data, or AOIs cannot be found**

Check the names and locations in [Project layout and input data](#project-layout-and-input-data).
All project paths are defined in `configs/paths.py`.

## License

This repository was developed as part of a research project at the Laboratorio
de Inteligencia Aplicada (LIAA).
