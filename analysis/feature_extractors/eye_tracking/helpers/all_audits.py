"""
Generate audit plots for all eye-tracking CSV files.
"""

from pathlib import Path

from configs.paths import (
    PROCESSED_EYE_TRACKING_DIR,
)

from .audit import audit


def main():

    input_dir = (
       PROCESSED_EYE_TRACKING_DIR
    )

    csv_files = sorted(
        input_dir.glob("*.csv")
    )

    print(f"\nFound {len(csv_files)} files.\n")

    for i, csv_file in enumerate(csv_files, start=1):

        print(
            f"[{i}/{len(csv_files)}] "
            f"{csv_file.name}"
        )

        audit(csv_file)

    print()

    print("=" * 60)
    print("ALL AUDITS GENERATED")
    print("=" * 60)


if __name__ == "__main__":

    main()