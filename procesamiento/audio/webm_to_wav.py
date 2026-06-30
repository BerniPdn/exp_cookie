import os
import subprocess

carpeta_webm = "./videos_cookie_piloto_arreglados"
carpeta_wav  = "./wavs_convertidos"
os.makedirs(carpeta_wav, exist_ok=True)

errores = []

for archivo in os.listdir(carpeta_webm):
    if not archivo.endswith(".webm"):
        continue

    ruta_entrada = os.path.join(carpeta_webm, archivo)
    nombre_base  = os.path.splitext(archivo)[0]
    ruta_salida  = os.path.join(carpeta_wav, f"{nombre_base}.wav")

    print(f"Convirtiendo: {archivo}...")

    resultado = subprocess.run([
        "ffmpeg",
        "-y",                        # sobreescribir si ya existe
        "-fflags", "+genpts",        # regenera timestamps corruptos (clave para Chrome WebM)
        "-i", ruta_entrada,
        "-vn",                       # ignorar video, solo audio
        "-ar", "16000",              # 16kHz — formato nativo de Whisper
        "-ac", "1",                  # mono
        "-c:a", "pcm_s16le",         # WAV sin compresión
        ruta_salida
    ], capture_output=True, text=True)

    if resultado.returncode != 0:
        print(f"  ⚠️  Error con {archivo}:")
        print(resultado.stderr[-300:])  # últimas líneas del error de ffmpeg
        errores.append(archivo)
    else:
        print(f"  ✓ Guardado en {ruta_salida}")

print(f"\n--- Conversión terminada. Errores: {len(errores)} ---")
for e in errores:
    print(f"  - {e}")