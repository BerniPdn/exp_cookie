import os
import csv
import re
from pathlib import Path
import sys

# ─── Importar los módulos del repo ────────────────────────────────
# Asegurate de correr este script desde la raíz del repo (donde está /analisis)
# Agregar tanto analisis/ como analisis/src/ al path
sys.path.insert(0, str(Path(__file__).parent.parent / "analisis"))
sys.path.insert(0, str(Path(__file__).parent.parent / "analisis" / "src"))

from feature_extractors.text.SpeechGraph import SpeechGraph
from feature_extractors.text.Fluence import Fluence
from feature_extractors.text.utils import flatten_dict

# ─── 🛠️ CONFIGURACIÓN DE LA NUEVA CARPETA DE SALIDA ────────────────
_SCRIPT_DIR = Path(__file__).parent  # carpeta donde vive este archivo .py
CARPETA_TRANSCRIPCIONES = _SCRIPT_DIR / "transcripciones" / "limpias"

# Definimos la carpeta que querés y la creamos de forma segura si no existe
CARPETA_RESULTADOS = _SCRIPT_DIR / "resultados_transcripciones"
CARPETA_RESULTADOS.mkdir(exist_ok=True)

# Redireccionamos el archivo principal y la carpeta de resúmenes hacia la nueva ruta
ARCHIVO_SALIDA = str(CARPETA_RESULTADOS / "resultados_analisis.csv")
CARPETA_RESUMENES = CARPETA_RESULTADOS

LANG = "es"
LAMINAS_RELEVANTES = {"lamina_nueva", "lamina_vieja"}

# ─── Inicializar los extractores una sola vez ─────────────────────
print("Cargando modelos de análisis...")
speech_graph = SpeechGraph(LANG)
fluence      = Fluence(LANG)
print("Modelos cargados.\n")


def parsear_nombre(nombre_archivo):
    """
    Extrae uuid, lamina y run_id del nombre del archivo.
    """
    sin_ext = os.path.splitext(nombre_archivo)[0]

    patron = r"^grabacion_([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})_(.+)_([^_]+)_arreglado$"
    match = re.match(patron, sin_ext)

    if not match:
        return None, None, None

    uuid   = match.group(1)
    lamina = match.group(2)
    run_id = match.group(3)

    return uuid, lamina, run_id


def analizar_texto(texto):
    """
    Corre los extractores sobre un texto y devuelve un dict con todos los resultados.
    """
    resultados = {}

    # ── SpeechGraph ───────────────────────────────────────────────
    try:
        sg = speech_graph.get_peech_graph(texto)
        sg_flat = flatten_dict(sg)
        resultados.update(sg_flat)
    except Exception as e:
        print(f"    ⚠️  SpeechGraph falló: {e}")

    # ── Fluence ───────────────────────────────────────────────────
    try:
        pos  = fluence.get_postag(texto)
        pos_flat = flatten_dict({f"pos_{k}": v for k, v in pos.items()})
        resultados.update(pos_flat)

        n_words = fluence.get_total_words(texto)
        resultados["total_words"] = n_words
    except Exception as e:
        print(f"    ⚠️  Fluence falló: {e}")

    return resultados


# ─── Recorrer todas las transcripciones ───────────────────────────
filas = []

carpeta_base = Path(CARPETA_TRANSCRIPCIONES)

for carpeta_uuid in sorted(carpeta_base.iterdir()):
    if not carpeta_uuid.is_dir():
        continue

    uuid_participante = carpeta_uuid.name
    print(f"Procesando participante: {uuid_participante}")

    for archivo in sorted(carpeta_uuid.iterdir()):
        if not archivo.suffix == ".txt":
            continue

        uuid, lamina, run_id = parsear_nombre(archivo.name)

        if uuid is None:
            print(f"  ⚠️  No se pudo parsear: {archivo.name}")
            continue

        if lamina not in LAMINAS_RELEVANTES:
            print(f"  → Saltando {lamina} (no es lámina de análisis)")
            continue

        print(f"  Analizando: {lamina} [{run_id}]")

        texto = archivo.read_text(encoding="utf-8").strip()

        if not texto:
            print(f"  ⚠️  Archivo vacío: {archivo.name}")
            continue

        metricas = analizar_texto(texto)

        fila = {
            "uuid":   uuid,
            "run_id": run_id,
            "lamina": lamina,
            **metricas,
        }
        filas.append(fila)

# ─── Escribir el CSV Principal ────────────────────────────────────
if not filas:
    print("\n⚠️  No se encontraron archivos para analizar.")
else:
    todas_las_columnas = ["uuid", "run_id", "lamina"]
    for fila in filas:
        for k in fila:
            if k not in todas_las_columnas:
                todas_las_columnas.append(k)

    with open(ARCHIVO_SALIDA, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=todas_las_columnas, extrasaction="ignore")
        writer.writeheader()
        for fila in filas:
            fila_completa = {col: fila.get(col, None) for col in todas_las_columnas}
            writer.writerow(fila_completa)

    print(f"\n✓ CSV principal guardado en: {ARCHIVO_SALIDA}")
    print(f"  {len(filas)} filas | {len(todas_las_columnas)} columnas")

# ─── RESUMEN Y ANÁLISIS AUTOMÁTICO INDENTADO ──────────────────────
import statistics
from collections import defaultdict

def es_numerico(val):
    if val is None:
        return False
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False

cols_numericas = []
if filas:
    candidatas = [k for k in todas_las_columnas if k not in {"uuid", "run_id", "lamina"}]
    for col in candidatas:
        valores = [f[col] for f in filas if col in f and es_numerico(f.get(col))]
        if valores:
            cols_numericas.append(col)

print(f"\n  Columnas numéricas detectadas: {len(cols_numericas)}")

# ── 1. Estadísticas descriptivas generales ────────────────────────
print("\nGenerando resumen descriptivo general...")
filas_descriptivas = []
for col in cols_numericas:
    vals = [float(f[col]) for f in filas if es_numerico(f.get(col))]
    if not vals:
        continue
    filas_descriptivas.append({
        "metrica":  col,
        "n":        len(vals),
        "media":    round(statistics.mean(vals), 4),
        "sd":       round(statistics.stdev(vals), 4) if len(vals) > 1 else 0,
        "mediana":  round(statistics.median(vals), 4),
        "min":      round(min(vals), 4),
        "max":      round(max(vals), 4),
    })

ruta_desc = CARPETA_RESUMENES / "resumen_descriptivo.csv"
with open(ruta_desc, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["metrica", "n", "media", "sd", "mediana", "min", "max"])
    writer.writeheader()
    writer.writerows(filas_descriptivas)
print(f"  ✓ {ruta_desc}")

# ── 2. Promedios por lámina ───────────────────────────────────────
print("Generando promedios por lámina...")
por_lamina = defaultdict(list)
for f in filas:
    por_lamina[f["lamina"]].append(f)

laminas = sorted(por_lamina.keys())
filas_por_lamina = []

for col in cols_numericas:
    fila_col = {"metrica": col}
    for lam in laminas:
        vals = [float(f[col]) for f in por_lamina[lam] if es_numerico(f.get(col))]
        fila_col[f"media_{lam}"]  = round(statistics.mean(vals), 4) if vals else None
        fila_col[f"sd_{lam}"]     = round(statistics.stdev(vals), 4) if len(vals) > 1 else None
        fila_col[f"n_{lam}"]      = len(vals)
    filas_por_lamina.append(fila_col)

if "lamina_nueva" in laminas and "lamina_vieja" in laminas:
    for fila_col in filas_por_lamina:
        nueva = fila_col.get("media_lamina_nueva")
        vieja = fila_col.get("media_lamina_vieja")
        if nueva is not None and vieja is not None:
            fila_col["diferencia_nueva_menos_vieja"] = round(nueva - vieja, 4)
        else:
            fila_col["diferencia_nueva_menos_vieja"] = None

cols_lamina = ["metrica"]
for lam in laminas:
    cols_lamina += [f"media_{lam}", f"sd_{lam}", f"n_{lam}"]
if "lamina_nueva" in laminas and "lamina_vieja" in laminas:
    cols_lamina.append("diferencia_nueva_menos_vieja")

ruta_lamina = CARPETA_RESUMENES / "resumen_por_lamina.csv"
with open(ruta_lamina, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=cols_lamina, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(filas_por_lamina)
print(f"  ✓ {ruta_lamina}")

# ── 3. Comparación por participante (nueva − vieja) ───────────────
print("Generando comparación por participante...")
por_participante = defaultdict(dict)
for f in filas:
    por_participante[f["uuid"]][f["lamina"]] = f

filas_participante = []
for uuid, lams in sorted(por_participante.items()):
    nueva = lams.get("lamina_nueva")
    vieja = lams.get("lamina_vieja")
    fila_p = {"uuid": uuid}

    for col in cols_numericas:
        val_nueva = float(nueva[col]) if nueva and es_numerico(nueva.get(col)) else None
        val_vieja = float(vieja[col]) if vieja and es_numerico(vieja.get(col)) else None
        fila_p[f"{col}__nueva"] = val_nueva
        fila_p[f"{col}__vieja"] = val_vieja
        if val_nueva is not None and val_vieja is not None:
            fila_p[f"{col}__diff"] = round(val_nueva - val_vieja, 4)
        else:
            fila_p[f"{col}__diff"] = None

    filas_participante.append(fila_p)

cols_participante = ["uuid"]
for col in cols_numericas:
    cols_participante += [f"{col}__nueva", f"{col}__vieja", f"{col}__diff"]

ruta_participante = CARPETA_RESUMENES / "resumen_por_participante.csv"
with open(ruta_participante, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=cols_participante, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(filas_participante)
print(f"  ✓ {ruta_participante}")

# ── 4. Outliers (> 2 SD de la media) ─────────────────────────────
print("Detectando outliers...")
stats_col = {}
for col in cols_numericas:
    vals = [float(f[col]) for f in filas if es_numerico(f.get(col))]
    if len(vals) > 1:
        stats_col[col] = {"media": statistics.mean(vals), "sd": statistics.stdev(vals)}

UMBRAL_SD = 2.0
filas_outliers = []

for f in filas:
    for col in cols_numericas:
        if col not in stats_col or not es_numerico(f.get(col)):
            continue
        val = float(f[col])
        media = stats_col[col]["media"]
        sd    = stats_col[col]["sd"]
        if sd == 0:
            continue
        z = (val - media) / sd
        if abs(z) > UMBRAL_SD:
            filas_outliers.append({
                "uuid":    f["uuid"],
                "lamina":  f["lamina"],
                "metrica": col,
                "valor":   round(val, 4),
                "media":   round(media, 4),
                "sd":      round(sd, 4),
                "z_score": round(z, 4),
            })

ruta_outliers = CARPETA_RESUMENES / "outliers.csv"
with open(ruta_outliers, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["uuid", "lamina", "metrica", "valor", "media", "sd", "z_score"])
    writer.writeheader()
    writer.writerows(filas_outliers)
print(f"  ✓ {ruta_outliers}  ({len(filas_outliers)} outliers detectados)")

print(f"\n✓ ¡Todo limpio y organizado adentro de: {CARPETA_RESULTADOS}/")