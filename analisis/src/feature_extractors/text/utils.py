import logging
import spacy
from spacy.cli import download

# Logger estándar de Python — reemplaza el src.utils.logger que no existe en este repo
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_transcript(sample):
    with open(sample.text_path, "r") as f:
        return f.read()

def flatten_dict(d: dict):
    # Aplana un dict anidado hasta que solo tenga escalares
    # Ej: {"a": {"b": 1}} → {"a__b": 1}
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
        spacy.load(model_name)
        logger.info(f"Modelo '{model_name}' ya instalado.")
    except OSError:
        logger.info(f"Modelo '{model_name}' no encontrado. Descargando...")
        download(model_name)