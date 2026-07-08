from pathlib import Path
import re

import matplotlib.pyplot as plt
import spacy
from wordcloud import WordCloud
from configs.paths import (
    MANUAL_TRANSCRIPT_DIR,
    TEXT_RESULTS_DIR,
)

# ============================================================
# CONFIG
# ============================================================

TRANSCRIPT_DIR = MANUAL_TRANSCRIPT_DIR
OUTPUT_DIR = TEXT_RESULTS_DIR

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# LOAD SPACY
# ============================================================

nlp = spacy.load("es_core_news_lg")

# ============================================================
# EXTRA STOPWORDS
# ============================================================

STOPWORDS = {
    "eh", "emm", "mmm", "este", "bueno",
    "acá", "aca", "ahí", "ahi",
    "entonces", "capaz", "creo",
    "persona", "personas",
    "cosa", "cosas",
    "lado", "imagen",
    "haber", "ser", "estar",
    "hacer", "tener", "decir",
    "ver", "ir", "dar",
    "poner", "salir", "venir",
    "poder", "parecer"
}

# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text: str) -> str:

    text = text.lower()

    text = re.sub(r"[^\w\sáéíóúüñ]", " ", text)
    text = re.sub(r"\d+", " ", text)

    doc = nlp(text)

    words = []

    for token in doc:

        if (
            token.is_space
            or token.is_punct
            or token.is_stop
            or token.like_num
        ):
            continue

        # Mantener solo palabras informativas
        if token.pos_ not in {"NOUN", "VERB", "ADJ"}:
            continue

        lemma = token.lemma_.strip().lower()

        if len(lemma) < 3:
            continue

        if lemma in STOPWORDS:
            continue

        words.append(lemma)

    return " ".join(words)

# ============================================================
# READ TRANSCRIPTS
# ============================================================

texts = {
    "lamina_vieja": [],
    "lamina_nueva": [],
}

for file in TRANSCRIPT_DIR.glob("*.txt"):

    text = file.read_text(encoding="utf-8")

    if "lamina_vieja" in file.name:
        texts["lamina_vieja"].append(text)

    elif "lamina_nueva" in file.name:
        texts["lamina_nueva"].append(text)

# ============================================================
# CREATE WORD CLOUDS
# ============================================================

for condition, corpus in texts.items():

    corpus = "\n".join(corpus)
    corpus = clean_text(corpus)

    wc = WordCloud(
        width=1800,
        height=1000,
        background_color="white",
        collocations=False,
        max_words=120,
        prefer_horizontal=0.95
    ).generate(corpus)

    plt.figure(figsize=(14, 8))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()

    output_file = OUTPUT_DIR / f"{condition}_wordcloud.png"

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Saved: {output_file}")

print("Done!")
