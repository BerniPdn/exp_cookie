# exp_cookie

**exp_cookie** is a multimodal experimental platform developed to investigate potential gender bias in the Cookie Theft picture.

The experiment was implemented in **jsPsych** and designed to run on **DataPruebas**, allowing participants to complete a picture description task while multiple behavioral data modalities are recorded simultaneously.

The repository contains the complete experimental implementation, data preprocessing pipelines, and the infrastructure for future multimodal analyses.

---

# Experiment

The experimental protocol consists of the following stages:

- Informed consent
- Camera and microphone setup
- Eye-tracking calibration and validation
- Description of two Cookie Theft pictures
- Presentation of emotional images from the OASIS dataset
- Post-task questionnaires

During the experiment, the following data are collected:

- Video recordings
- Audio recordings
- Eye-tracking data (WebGazer)
- Experimental metadata

## Cookie Theft Pictures

The experiment compares two versions of the Cookie Theft picture:

- **Original Cookie Theft Picture**
- **Modified color version** with reversed parental roles

The objective is to investigate whether changing the gender roles represented in the scene influences participants' visual attention and spontaneous language production.

## Local Development

For development and debugging purposes, the experiment can also be executed locally using the provided Flask server.

Start the local server:

```bash
python experimento/servidor_local.py
```

The server emulates the main DataPruebas API endpoints used during the experiment, allowing local testing of:

- Video uploads
- Experimental metadata
- Experiment completion

By default, the server runs at:

```
http://localhost:8002 (to make it work you would need to comment in the two lines commented out in runtime.js)
```

When running locally, recorded videos are saved to the directory configured in `servidor_local.py`.

---

# Repository Structure

```text
exp_cookie/

├── analysis/          Feature extraction and statistical analyses
├── configs/           Project configuration files
├── data/              Raw, processed, and result data
├── experimento/       jsPsych experiment
└── procesamiento/     Data preprocessing pipelines
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/BerniPdn/exp_cookie.git
cd exp_cookie
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

**FFmpeg** must also be installed and available from the command line.

---

# Data Organization

Raw experimental data should be placed inside:

```text
data/raw/videos/
data/raw/eye_tracking/
```

Processed files are automatically generated in:

```text
data/processed/
```

Quality reports and future analysis outputs are stored in:

```text
data/results/
```

---

# Processing Pipeline

Run the complete preprocessing pipeline with:

```bash
python3 -m procesamiento.pipelines.process_experiment
```

Or process each modality independently:

```bash
python3 -m procesamiento.pipelines.process_video_pipeline

python3 -m procesamiento.pipelines.process_audio_pipeline

python3 -m procesamiento.pipelines.process_eye_tracking_pipeline
```

---

# Current Processing Modules

The repository currently includes:

- Video preprocessing
- Audio extraction
- Automatic transcription using Faster Whisper
- Eye-tracking preprocessing
- Video quality assessment
- Modular processing pipelines

The `analysis/` module contains the feature extraction and statistical analyses built on top of the processed data.

---

# License

This repository was developed as part of a research project at the Laboratorio de Inteligencia Aplicada (LIAA)
