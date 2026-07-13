from pathlib import Path
import pandas as pd
import spacy

from configs.paths import (
    MANUAL_TRANSCRIPT_DIR,
    TEXT_RESULTS_METRICS_DIR,
)

# ============================================================
# CONFIG
# ============================================================

TRANSCRIPT_DIR = MANUAL_TRANSCRIPT_DIR

OUTPUT_FILE = TEXT_RESULTS_METRICS_DIR / "character_mentions.csv"

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

nlp = spacy.load("es_core_news_lg")

# ============================================================
# CHARACTER GROUPS
# ============================================================

CHARACTER_GROUPS = {

    "caregiver_female": {
        "madre",
        "mamá",
        "mama",
        "mujer",
        "señora",
    },

    "caregiver_male": {
        "padre",
        "papá",
        "papa",
        "hombre",
        "señor",
        "varon",
    },

    "children": {
        "niño",
        "niña",
        "nena",
        "nene",
        "chico",
        "chica",
        "hijo",
        "hija",
    },

    "dog": {
        "perro",
    },

    "cat": {
        "gato",
    },
}

# ============================================================
# HELPERS
# ============================================================

def get_character_group(lemma):

    lemma = lemma.lower()

    for group, words in CHARACTER_GROUPS.items():

        if lemma in words:
            return group

    return None

# ============================================================
# MAIN
# ============================================================

rows = []

for file in sorted(TRANSCRIPT_DIR.glob("*.txt")):

    text = file.read_text(encoding="utf-8")

    doc = nlp(text)

    image = (
        "vieja"
        if "lamina_vieja" in file.name
        else "nueva"
    )

    for sent in doc.sents:

        for token in sent:

            group = get_character_group(token.lemma_)

            if group is None:
                continue

            rows.append({

                "file": file.name,

                "participant":
                    file.name.split("_")[1],

                "image":
                    image,

                "character_group":
                    group,

                "word":
                    token.text,

                "lemma":
                    token.lemma_,

                "sentence":
                    sent.text.strip(),
            })

# ============================================================
# SAVE
# ============================================================

df = pd.DataFrame(rows)

df.to_csv(
    OUTPUT_FILE,
    index=False,
)

print(df.head())

print(f"\nSaved to {OUTPUT_FILE}")
