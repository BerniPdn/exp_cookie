"""
Process raw eye-tracking data.

This script reads the raw experiment JSON and converts every
WebGazer trial into an independent CSV file.

Each CSV contains normalized gaze coordinates ready for
downstream analysis.
"""

from pathlib import Path
import argparse
import json
import time

from .extract_gaze import extract_gaze


from configs.paths import (
    PROCESSED_EYE_TRACKING_DIR,
    SUBJECT_MAPPING,
    get_eye_tracking_json,
)

def process_eye_tracking(
    overwrite=False,
):
    """
    Process one raw eye-tracking JSON file.

    Parameters
    ----------
    overwrite : bool, default=False
        Overwrite existing CSV files.

    Returns
    -------
    dict
        Processing summary.
    """

    input_file = get_eye_tracking_json()

    output_dir = PROCESSED_EYE_TRACKING_DIR

    with open(
        input_file,
        "r",
        encoding="utf-8",
    ) as file:

        experiment = json.load(file)

    runs = experiment.get("experiment_runs", [])

    with open(
        SUBJECT_MAPPING,
        "r",
        encoding="utf-8",
    ) as file:

        subject_mapping = json.load(file)

    summary = {
        "runs": len(runs),
        "processed": 0,
        "skipped": 0,
        "failed": 0,
        "trials": 0,
    }

    start = time.time()

    print(f"\nFound {len(runs)} experiment runs.\n")

    for run_index, run in enumerate(runs, start=1):

        subject_id = run["subject"]

        if subject_id not in subject_mapping:
            raise KeyError(
                f"Subject {subject_id} not found in subject mapping."
            )

        participant = subject_mapping[subject_id]
        run_id = participant["run_id"]

        print(
            f"[{run_index}/{len(runs)}] "
            f"{run_id}"
        )

        validation_score = None
        calibration_passed = None
        calibration_attempts = None

        records = run.get("records", [])

        #
        # Recover calibration information
        #

        for record in records:

            data = record.get("data", {})

            if data.get("trial") == "webgazer_validation":

                validation_score = data.get(
                    "validacion_promedio"
                )

                calibration_passed = data.get(
                    "calibracion_aprobada"
                )

                calibration_attempts = data.get(
                    "intentos_calibracion"
                )

                break

        #
        # Process every eye-tracking trial
        #

        for record in records:

            data = record.get("data", {})

            if "webgazer_data" not in data:
                continue

            summary["trials"] += 1

            trial_name = data["trial"]

            output_file = (
                output_dir /
                f"{run_id}_{trial_name}.csv"
            )

            if (
                output_file.exists()
                and
                not overwrite
            ):

                summary["skipped"] += 1

                print(
                    f"   ⏭ {trial_name}"
                )

                continue

            try:

                df = extract_gaze(

                    run_id=run_id,

                    validation_score=validation_score,

                    calibration_passed=calibration_passed,

                    calibration_attempts=calibration_attempts,

                    trial_data=data,

                )

                df.to_csv(
                    output_file,
                    index=False,
                )

                summary["processed"] += 1

                print(
                    f"   ✓ {trial_name}"
                )

            except Exception as e:

                summary["failed"] += 1

                print(
                    f"   ✗ {trial_name}: {e}"
                )

    summary["elapsed"] = time.time() - start

    return summary


def print_summary(summary):

    print("\n" + "=" * 50)

    print("EYE TRACKING PROCESSING FINISHED")

    print("=" * 50)

    print(f"Runs found      : {summary['runs']}")
    print(f"Trials found    : {summary['trials']}")
    print(f"Processed       : {summary['processed']}")
    print(f"Skipped         : {summary['skipped']}")
    print(f"Failed          : {summary['failed']}")
    print(f"Elapsed (s)     : {summary['elapsed']:.1f}")

    print("=" * 50)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Process raw eye-tracking data."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing CSV files.",
    )

    args = parser.parse_args()

    summary = process_eye_tracking(

        overwrite=args.overwrite,

    )

    print_summary(summary)