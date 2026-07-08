from pathlib import Path
import pandas as pd

from configs.paths import TEXT_RESULTS_DIR

# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = TEXT_RESULTS_DIR / "character_mentions.csv"
OUTPUT_FILE = TEXT_RESULTS_DIR / "character_summary.csv"

# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(INPUT_FILE)

# ============================================================
# SUMMARY
# ============================================================

rows = []

for (participant, image), group in df.groupby(["participant", "image"]):

    counts = group["character_group"].value_counts()

    first_character = group.iloc[0]["character_group"]

    rows.append({

        "participant": participant,

        "image": image,

        "first_character": first_character,

        "female_mentions":
            counts.get("caregiver_female", 0),

        "male_mentions":
            counts.get("caregiver_male", 0),

        "children_mentions":
            counts.get("children", 0),

        "dog_mentions":
            counts.get("dog", 0),

        "cat_mentions":
            counts.get("cat", 0),

        "total_mentions":
            len(group),

        "mentions_caregiver":
            counts.get("caregiver_female", 0)
            +
            counts.get("caregiver_male", 0),
    })

summary = pd.DataFrame(rows)

summary = summary.sort_values(
    ["participant", "image"]
)

summary.to_csv(
    OUTPUT_FILE,
    index=False,
)

print(summary)

print(f"\nSaved to {OUTPUT_FILE}")