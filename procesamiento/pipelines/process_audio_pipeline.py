"""
Complete audio processing pipeline.
"""

import argparse

from procesamiento.audio.process_audio import process_audio
from procesamiento.audio.process_transcripts import process_transcripts


def run_audio_pipeline(
    overwrite: bool = False,
):
    """
    Run the complete audio processing pipeline.

    Parameters
    ----------
    overwrite : bool, default=False
        Whether to overwrite existing processed files.
    """

    print("\n" + "=" * 60)
    print("AUDIO PIPELINE")
    print("=" * 60)

    process_audio(
        overwrite=overwrite,
    )

    process_transcripts(
        overwrite=overwrite,
    )

    print("\n✓ Audio pipeline completed.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Run the complete audio processing pipeline."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing processed files.",
    )

    args = parser.parse_args()

    run_audio_pipeline(
        overwrite=args.overwrite,
    )