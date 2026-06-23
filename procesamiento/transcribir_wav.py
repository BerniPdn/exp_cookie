import os
from faster_whisper import WhisperModel

# ─── Configuración ────────────────────────────────────────────────
DEVICE       = "cpu"
COMPUTE_TYPE = "int8"

carpeta_wavs       = "./wavs_convertidos"
carpeta_limpias    = "./transcripciones/limpias"
carpeta_timestamps = "./transcripciones/timestamps"

os.makedirs(carpeta_limpias, exist_ok=True)
os.makedirs(carpeta_timestamps, exist_ok=True)

# ─── Cargar modelo ────────────────────────────────────────────────
print("Cargando modelo Whisper large-v3...")
model = WhisperModel("large-v3", device=DEVICE, compute_type=COMPUTE_TYPE)
print("Modelo cargado.\n")

def extraer_uuid(nombre_archivo):
    """
    Extrae el UUID del nombre del archivo WAV.
    Formato: grabacion_{uuid}_{lamina}_{runID}_arreglado.wav
    El UUID es siempre el segundo campo al separar por '_',
    pero como el UUID tiene guiones internos, está entre el primer
    y segundo underscore contando desde 'grabacion_'.
    Ejemplo: grabacion_7cc7d9af-37f5-4d65-915d-fc79f9d045b9_lamina_nueva_5R0S1mr_arreglado.wav
             → UUID: 7cc7d9af-37f5-4d65-915d-fc79f9d045b9
    """
    sin_extension = os.path.splitext(nombre_archivo)[0]  # saca .wav
    # El UUID está entre el primer y segundo underscore
    # "grabacion" es el campo 0, UUID es el campo 1
    partes = sin_extension.split("_")
    # El UUID tiene formato xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    # son 5 grupos separados por guiones, así que ocupa un solo campo
    return partes[1]

errores = []

# ─── Procesar cada WAV ────────────────────────────────────────────
for archivo in sorted(os.listdir(carpeta_wavs)):
    if not archivo.endswith(".wav"):
        continue

    ruta_wav    = os.path.join(carpeta_wavs, archivo)
    nombre_base = os.path.splitext(archivo)[0]

    # Extraer UUID para agrupar carpetas
    try:
        uuid = extraer_uuid(archivo)
    except IndexError:
        print(f"  ⚠️  No se pudo extraer UUID de: {archivo}")
        errores.append(archivo)
        continue

    # Crear subcarpetas por UUID
    # Resultado: transcripciones/limpias/7cc7d9af-.../grabacion_...txt
    carpeta_uuid_limpia     = os.path.join(carpeta_limpias, uuid)
    carpeta_uuid_timestamps = os.path.join(carpeta_timestamps, uuid)
    os.makedirs(carpeta_uuid_limpia, exist_ok=True)
    os.makedirs(carpeta_uuid_timestamps, exist_ok=True)

    ruta_txt        = os.path.join(carpeta_uuid_limpia, f"{nombre_base}.txt")
    ruta_timestamps = os.path.join(carpeta_uuid_timestamps, f"{nombre_base}_timestamps.txt")

    print(f"Transcribiendo: {archivo}  [UUID: {uuid}]")

    try:
        # Sin vad_filter para preservar muletillas y todo el audio
        segments, info = model.transcribe(
            ruta_wav,
            language="es",
            beam_size=5,
            condition_on_previous_text=False, 
            no_speech_threshold=0.3,           
            compression_ratio_threshold=2.4,  
            word_timestamps=True,  # fuerza análisis palabra por palabra
            initial_prompt="Transcripción literal de habla espontánea en español rioplatense, incluyendo muletillas como eh, mm, este, o sea, bueno, dale."
        )

        # Colectar en lista porque el generador se consume una sola vez
        segmentos = list(segments)

        # ── Archivo 1: texto limpio para SpeechGraph ──────────────
        # Texto corrido sin marcas, listo para SpeechGraph y análisis léxico
        texto_limpio = " ".join(seg.text.strip() for seg in segmentos)

        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write(texto_limpio)

        # ── Archivo 2: timestamps + silencios marcados ─────────────
        # Cada segmento con su tiempo de inicio y fin
        # Los silencios >= 1s quedan marcados explícitamente
        with open(ruta_timestamps, "w", encoding="utf-8") as f:
            tiempo_anterior = 0.0

            for seg in segmentos:
                inicio = seg.start
                fin    = seg.end
                texto  = seg.text.strip()

                # Silencio desde el fin del segmento anterior hasta este
                silencio = inicio - tiempo_anterior
                if silencio >= 1.0:
                    f.write(f"[SILENCIO {silencio:.1f}s]\n")

                f.write(f"[{inicio:06.1f}s -> {fin:06.1f}s] {texto}\n")

                tiempo_anterior = fin

        print(f"  ✓ Limpio     -> {ruta_txt}")
        print(f"  ✓ Timestamps -> {ruta_timestamps}")

    except Exception as e:
        print(f"  ⚠️  Error con {archivo}: {e}")
        errores.append(archivo)

# ─── Resumen final ────────────────────────────────────────────────
print(f"\n--- Procesamiento terminado. Errores: {len(errores)} ---")
for e in errores:
    print(f"  - {e}")