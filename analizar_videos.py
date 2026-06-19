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
    metricas = {"volumen_medio_db": None, "silencio_detectado": False}
    try:
        out = subprocess.run(
            ["ffmpeg", "-i", str(ruta), "-af", "volumedetect", "-vn", "-f", "null", "-"],
            capture_output=True, text=True, timeout=15
        )
        m_mean = re.search(r"mean_volume:\s*([-\d.]+)\s*dB", out.stderr)
        if m_mean:
            metricas["volumen_medio_db"] = float(m_mean.group(1))

        sil = subprocess.run(
            ["ffmpeg", "-i", str(ruta), "-af", "silencedetect=noise=-40dB:d=3", "-vn", "-f", "null", "-"],
            capture_output=True, text=True, timeout=15
        )
        if "silence_start" in sil.stderr:
            metricas["silencio_detectado"] = True
    except Exception:
        pass
    return metricas


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
        "volumen_medio_db": None,
        "silencio_detectado": False
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

    resultado.update(analizar_volumen_seguro(ruta))
    return resultado


def interpretar_calidad(fps_promedio, resoluciones, fps_valido, vol_medio, silencio):
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
    if silencio:
        alertas_audio.append("silencio prolongado")
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
        videos_info = [analizar_video(a) for a in archivos_usuario]

        resoluciones = list({v["resolucion"] for v in videos_info if v["resolucion"]})
        lista_fps    = [v["fps"] for v in videos_info if v["fps"] is not None]
        fps_promedio = round(sum(lista_fps) / len(lista_fps), 2) if lista_fps else 0
        fps_valido   = len(lista_fps) > 0
        peso_total   = round(sum(v["peso_mb"] for v in videos_info), 2)
        volumenes    = [v["volumen_medio_db"] for v in videos_info if v["volumen_medio_db"] is not None]
        vol_medio    = round(sum(volumenes) / len(volumenes), 1) if volumenes else None
        silencio     = any(v["silencio_detectado"] for v in videos_info)

        estado, calidad_audio, comentario = interpretar_calidad(
            fps_promedio, resoluciones, fps_valido, vol_medio, silencio
        )

        print(f"  Archivos:    {len(archivos_usuario)} videos")
        print(f"  Tamano:      {peso_total} MB")
        print(f"  Resolucion:  {', '.join(resoluciones) or '-'} px -> [{estado}]")
        print(f"  FPS:         {fps_promedio if fps_valido else 'No recuperable'}")
        print(f"  Audio:       [{calidad_audio}]")
        print(f"  Comentario:  {comentario}")
        print("-" * 90)

        filas.append({
            "Usuario (N)":        num,
            "Run-ID":             run_id,
            "Videos en servidor": len(archivos_usuario),
            "Tamano total (MB)":  peso_total,
            "Resolucion (px)":    ", ".join(resoluciones) or "-",
            "FPS":                fps_promedio if fps_valido else "Error",
            "Volumen medio (dB)": vol_medio if vol_medio is not None else "N/A",
            "Calidad de Audio":   calidad_audio,
            "Estado del canal":   estado,
            "Comentario":         comentario,
        })

    with open(salida_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        writer.writeheader()
        writer.writerows(filas)

    print(f"\nReporte guardado en: {salida_csv}")


if __name__ == "__main__":
    main()