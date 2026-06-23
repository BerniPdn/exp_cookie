import spacy
from spacy.cli import download
from src.utils import logger

def get_transcript(sample):
    with open(sample.text_path, "r") as f:
        return f.read()


def flatten_dict(d: dict):
    # Flatten a dictionary recursively until it only contains scalars
    res = {}
    for k, v in d.items():
        if isinstance(v, dict):
            for k2, v2 in flatten_dict(v).items():
                res[f'{k}__{k2}'] = v2
        else:
            res[k] = v
    return res

def ensure_model_installed(model_name):
    try:
        # Try loading the model
        spacy.load(model_name)
        logger.info(f"Model '{model_name}' is already installed.")
    except OSError:
        # Download the model if it's not found
        logger.info(f"Model '{model_name}' not found. Downloading now...")
        download(model_name)