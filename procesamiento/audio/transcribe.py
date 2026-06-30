"""
Transcribe a single audio recording using Faster-Whisper.

This module converts one WAV recording into two text files:

1. Clean transcript
   Plain text used for NLP and Speech Graph analysis.

2. Timestamp transcript
   Segment-level transcript preserving timing information and explicit silence markers.
"""

from pathlib import Path

from faster_whisper import WhisperModel


# ---------------------------------------------------------------------
# Whisper configuration
# ---------------------------------------------------------------------

MODEL_NAME = "large-v3"

DEVICE = "cpu"

COMPUTE_TYPE = "int8"

INITIAL_PROMPT = (
    "Literal transcription of spontaneous Rioplatense Spanish speech, "
    "including fillers such as eh, mm, este, o sea, bueno and dale."
)


# ---------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------

def load_model() -> WhisperModel:
    """
    Load the Faster-Whisper model.

    Returns
    -------
    WhisperModel
        Loaded Whisper model.
    """

    print("\nLoading Whisper model...")

    model = WhisperModel(
        MODEL_NAME,
        device=DEVICE,
        compute_type=COMPUTE_TYPE,
    )

    print("Model loaded.\n")

    return model


# ---------------------------------------------------------------------
# Transcription
# ---------------------------------------------------------------------

def transcribe_audio(
    input_audio: Path,
    clean_output: Path,
    timestamps_output: Path,
    model: WhisperModel,
):
    """
    Transcribe a single WAV recording.

    Parameters
    ----------
    input_audio : Path
        Input WAV file.

    clean_output : Path
        Destination of the clean transcript.

    timestamps_output : Path
        Destination of the timestamp transcript.

    model : WhisperModel
        Loaded Faster-Whisper model.
    """

    clean_output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamps_output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    segments, info = model.transcribe(

        str(input_audio),

        language="es",

        beam_size=5,

        condition_on_previous_text=False,

        no_speech_threshold=0.3,

        compression_ratio_threshold=2.4,

        word_timestamps=True,

        initial_prompt=INITIAL_PROMPT,

    )

    # Faster-Whisper returns a generator.
    segments = list(segments)

    # -------------------------------------------------------------
    # Clean transcript
    # -------------------------------------------------------------

    clean_text = " ".join(
        segment.text.strip()
        for segment in segments
    )

    with open(
        clean_output,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(clean_text)

    # -------------------------------------------------------------
    # Timestamp transcript
    # -------------------------------------------------------------

    previous_end = 0.0

    with open(
        timestamps_output,
        "w",
        encoding="utf-8",
    ) as file:

        for segment in segments:

            silence = segment.start - previous_end

            if silence >= 1.0:

                file.write(
                    f"[SILENCE {silence:.1f}s]\n"
                )

            file.write(
                f"[{segment.start:06.1f}s -> "
                f"{segment.end:06.1f}s] "
                f"{segment.text.strip()}\n"
            )

            previous_end = segment.end