"""
Transcribe every WAV recording in a directory.

This script iterates through all processed audio files and generates:

1. Clean transcripts
2. Timestamp transcripts

using Faster-Whisper.
"""

import argparse
import time

from .transcribe import (
    load_model,
    transcribe_audio,
)

from configs.paths import (
    PROCESSED_AUDIO_DIR,
    CLEAN_TRANSCRIPT_DIR,
    TIMESTAMP_TRANSCRIPT_DIR,
)

def process_transcripts(
    overwrite=False,
):
    """
    Transcribe every WAV file in a directory.

    Parameters
    ----------
    overwrite : bool, default=False
        Whether to overwrite existing output files.
    
    Returns
    -------
    dict
        Processing summary.
    """
    audio_dir = PROCESSED_AUDIO_DIR
    wav_files = sorted(audio_dir.rglob("*.wav"))

    clean_dir = CLEAN_TRANSCRIPT_DIR
    timestamp_dir = TIMESTAMP_TRANSCRIPT_DIR

    summary = {
        "total": len(wav_files),
        "processed": 0,
        "skipped": 0,
        "failed": 0,
    }

    model = load_model()

    start = time.time()

    print(f"Found {len(wav_files)} audio files.\n")

    for index, wav in enumerate(wav_files, start=1):

        relative = wav.relative_to(audio_dir)

        clean_output = (
            clean_dir /
            relative.with_suffix(".txt")
        )

        timestamps_output = (
            timestamp_dir /
            relative.with_suffix(".txt")
        )

        clean_output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamps_output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        print(
            f"[{index}/{len(wav_files)}] "
            f"{relative.name}"
        )

        # Skip already processed recordings.

        if (
            clean_output.exists()
            and timestamps_output.exists()
            and not overwrite
        ):

            summary["skipped"] += 1

            print("   ⏭ Already processed.")

            continue

        try:

            transcribe_audio(
                input_audio=wav,
                clean_output=clean_output,
                timestamps_output=timestamps_output,
                model=model,
            )

            summary["processed"] += 1

            print("   ✅ Success")

        except Exception as e:

            summary["failed"] += 1

            print(f"   ❌ Failed: {e}")

    summary["elapsed"] = time.time() - start

    return summary


def print_summary(summary):

    print("\n" + "=" * 50)
    print("TRANSCRIPTION FINISHED")
    print("=" * 50)

    print(f"Audio files found : {summary['total']}")
    print(f"Processed         : {summary['processed']}")
    print(f"Skipped           : {summary['skipped']}")
    print(f"Failed            : {summary['failed']}")
    print(f"Elapsed (s)       : {summary['elapsed']:.1f}")

    print("=" * 50)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Transcribe processed audio recordings."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files."
    )

    args = parser.parse_args()

    summary = process_transcripts(
        args.overwrite
    )

    print_summary(summary)