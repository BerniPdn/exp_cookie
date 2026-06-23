import cv2
import csv
import re
import subprocess
from pathlib import Path
from collections import defaultdict

# Para correr en terminal: python3 analizar_videos.py

# Configuracion
carpeta_origen   = Path(__file__).parent / "videos_cookie_piloto"
carpeta_destino  = Path(__file__).parent / "videos_cookie_piloto_arreglados"
carpeta_datos    = Path(__file__).parent / "datos_videos"
salida_csv       = carpeta_datos / "reporte_calidad.csv"


def arreglar_videos_en_lote():
    if not carpeta_origen.exists():
        print(f"Error: No se encontro la carpeta de origen: {carpeta_origen}")
        return False

    carpeta_destino.mkdir(exist_ok=True)
    carpeta_datos.mkdir(exist_ok=True)

    archivos = [f for f in carpeta_origen.iterdir() if f.suffix.lower() == ".webm"]
    if not archivos:
        print("Error: No se encontraron videos en 'videos_cookie_piloto'.")
        return False

    print("PASO 1: Arreglando contenedores WebM con FFmpeg...")
    print("-" * 60)

    hubo_cambios = False
    for archivo in archivos:
        nuevo_nombre = f"{archivo.stem}_arreglado.webm"
        ruta_salida  = carpeta_destino / nuevo_nombre

        if ruta_salida.exists():
            continue

        print(f"Arreglando: {archivo.name} -> {nuevo_nombre}")

        # Intento 1: regenerar timestamps e ignorar DTS invalidos
        resultado = subprocess.run(
            ["ffmpeg", "-y",
             "-fflags", "+genpts+igndts",
             "-i", str(archivo),
             "-c:v", "copy", "-c:a", "copy",
             "-vsync", "cfr",
             str(ruta_salida)],
            capture_output=True, text=True
        )

        # Intento 2 (fallback): remuxeo con muxdelay forzado a 0
        if resultado.returncode != 0 or not ruta_salida.exists():
            print("  Reintentando con metodo alternativo...")
            subprocess.run(
                ["ffmpeg", "-y",
                 "-i", str(archivo),
                 "-c:v", "copy", "-c:a", "copy",
                 "-muxdelay", "0", "-muxpreload", "0",
                 str(ruta_salida)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        hubo_cambios = True

    if not hubo_cambios:
        print("Todos los videos ya estaban arreglados previamente.")
    print("-" * 60 + "\n")
    return True


def analizar_volumen_seguro(ruta):
    """Mide el audio de forma aislada y devuelve solo el valor del volumen en dB (float o None)."""
    try:
        out = subprocess.run(
            ["ffmpeg", "-i", str(ruta), "-af", "volumedetect", "-vn", "-f", "null", "-"],
            capture_output=True, text=True, timeout=15
        )
        m_mean = re.search(r"mean_volume:\s*([-\d.]+)\s*dB", out.stderr)
        if m_mean:
            return float(m_mean.group(1))
    except Exception:
        pass
    return None 

def contar_fps_real(ruta):
    """Cuenta frames reales dividido duracion. Lento pero confiable para WebM corruptos."""
    try:
        print(f"    Metadatos corruptos, contando frames reales (puede tardar)...")
        out_dur = subprocess.run(
            ["ffprobe", "-v", "quiet",
             "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1",
             str(ruta)],
            capture_output=True, text=True, timeout=30
        )
        duracion = float(out_dur.stdout.strip())

        out_frames = subprocess.run(
            ["ffprobe", "-v", "quiet",
             "-count_frames",
             "-select_streams", "v:0",
             "-show_entries", "stream=nb_read_frames",
             "-of", "default=noprint_wrappers=1:nokey=1",
             str(ruta)],
            capture_output=True, text=True, timeout=120
        )
        n_frames = int(out_frames.stdout.strip())

        if duracion > 0 and n_frames > 0:
            fps_real = round(n_frames / duracion, 2)
            print(f"    FPS por conteo: {fps_real} ({n_frames} frames / {round(duracion, 1)}s)")
            return fps_real
    except Exception as e:
        print(f"    No se pudo calcular FPS por conteo: {e}")
    return None


def analizar_video(ruta):
    resultado = {
        "archivo": ruta.name,
        "peso_mb": round(ruta.stat().st_size / (1024 ** 2), 2),
        "resolucion": None,
        "fps": None,
        "volumen_medio_db": None
    }

    cap = cv2.VideoCapture(str(ruta))
    if cap.isOpened():
        ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        alto  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        resultado["resolucion"] = f"{ancho}x{alto}"
        fps_detectados = cap.get(cv2.CAP_PROP_FPS)
        if 0 < fps_detectados < 100:
            resultado["fps"] = round(fps_detectados, 2)
        cap.release()

    # Fallback: contar frames reales si los metadatos estan corruptos
    if resultado["fps"] is None:
        resultado["fps"] = contar_fps_real(ruta)

    resultado["volumen_medio_db"] = analizar_volumen_seguro(ruta)
    return resultado


def interpretar_calidad(fps_promedio, resoluciones, fps_valido, vol_medio):
    res_str = ", ".join(resoluciones)

    if not fps_valido:
        estado     = "ERROR DE METADATOS"
        comentario = "FPS no legible incluso por conteo de frames. Archivo severamente corrupto."
    elif "640x480" in res_str:
        estado     = "BAJA CALIDAD (SD)"
        comentario = "Resolucion 640x480 px. Puede comprometer el eye-tracking."
    elif fps_promedio < 24:
        estado     = "HD ENTRECORTADO"
        comentario = f"Caida a {fps_promedio} FPS. Posible saturacion de CPU."
    else:
        estado     = "OPTIMA"
        comentario = f"Canal estable a {fps_promedio} FPS ({res_str} px)."

    alertas_audio = []
    if vol_medio is not None and vol_medio < -45:
        alertas_audio.append(f"volumen bajo ({vol_medio} dB)")

    if vol_medio is None:
        calidad_audio = "Sin datos"
    elif alertas_audio:
        calidad_audio  = " | ".join(alertas_audio)
        comentario    += f" AUDIO: {calidad_audio}."
    else:
        calidad_audio  = "OK"
        comentario    += " Audio limpio."

    return estado, calidad_audio, comentario


def main():
    # PASO 1: Arreglar los videos
    if not arreglar_videos_en_lote():
        return

    # PASO 2: Analizar los videos corregidos
    archivos = sorted([f for f in carpeta_destino.iterdir() if f.suffix.lower() == ".webm"])

    grupos = defaultdict(list)
    for archivo in archivos:
        partes = archivo.name.split("_")
        if len(partes) >= 2:
            grupos[partes[1]].append(archivo)

    filas = []
    print("=" * 90)
    print("PASO 2: AUDITORIA TECNICA INTEGRAL (VIDEO + AUDIO)")
    print("=" * 90 + "\n")

    for num, (run_id, archivos_usuario) in enumerate(grupos.items(), 1):
        print(f"Analizando usuario {num}/{len(grupos)} (Run-ID: ...{run_id[-12:]})...")
        
        # Iteramos y procesamos cada archivo de video de forma individual
        for ruta_video in archivos_usuario:
            v = analizar_video(ruta_video)
            
            # Evaluamos la calidad técnica de este video específico
            resoluciones = [v["resolucion"]] if v["resolucion"] else []
            fps_valido = v["fps"] is not None
            
            estado, calidad_audio, comentario = interpretar_calidad(
                v["fps"] or 0, resoluciones, fps_valido, v["volumen_medio_db"]
            )

            print(f"  Archivo:     {v['archivo']}")
            print(f"  Resolucion:  {v['resolucion'] or '-'} px -> [{estado}]")
            print(f"  FPS:         {v['fps'] if fps_valido else 'No recuperable'}")
            print(f"  Volumen:     {f'{v['volumen_medio_db']} dB' if v['volumen_medio_db'] is not None else 'N/A'}")
            print("-" * 50)

            # Guardamos los datos desglosados por video en el CSV
            filas.append({
                "Usuario (N)":        num,
                "Run-ID":             run_id,
                "Video":              v["archivo"],
                "Tamano (MB)":        v["peso_mb"],
                "Resolucion (px)":    v["resolucion"] or "-",
                "FPS":                v["fps"] if fps_valido else "Error",
                "Volumen medio (dB)": v["volumen_medio_db"] if v["volumen_medio_db"] is not None else "N/A",
                "Calidad de Audio":   calidad_audio,
                "Estado del canal":   estado,
                "Comentario":         comentario,
            })

    # Guardamos el archivo CSV definitivo
    with open(salida_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        writer.writeheader()
        writer.writerows(filas)

    print(f"\nReporte guardado en: {salida_csv}")


if __name__ == "__main__":
    main()