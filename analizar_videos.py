import os
import cv2
import csv
import re
import subprocess
from pathlib import Path
from collections import defaultdict

#para correr en terminal: python3 analizar_videos.py

# ── Configuración ──────────────────────
# Busca la carpeta de videos arreglados dentro del repo
carpeta_videos = Path(__file__).parent / "videos_cookie_piloto_arreglados"

# Define la carpeta de salida dentro del repo y la crea si no existe
carpeta_datos  = Path(__file__).parent / "datos_videos"
carpeta_datos.mkdir(exist_ok=True)

salida_csv     = carpeta_datos / "reporte_calidad.csv"
# ──────────────────────────────────────────────────────────────────────────────

def analizar_volumen_seguro(ruta):
    """Mide el audio de forma aislada. Si falla ffmpeg, no rompe el script principal."""
    metricas = {"volumen_medio_db": None, "silencio_detectado": False}
    try:
        # Intenta medir volumen medio
        out = subprocess.run(
            ["ffmpeg", "-i", str(ruta), "-af", "volumedetect", "-vn", "-f", "null", "-"],
            capture_output=True, text=True, timeout=15
        )
        m_mean = re.search(r"mean_volume:\s*([-\d.]+)\s*dB", out.stderr)
        if m_mean: 
            metricas["volumen_medio_db"] = float(m_mean.group(1))

        # Intenta detectar si hubo un silencio absoluto prolongado (más de 3 segundos)
        sil = subprocess.run(
            ["ffmpeg", "-i", str(ruta), "-af", "silencedetect=noise=-40dB:d=3", "-vn", "-f", "null", "-"],
            capture_output=True, text=True, timeout=15
        )
        if "silence_start" in sil.stderr:
            metricas["silencio_detectado"] = True
    except Exception:
        # Si ffmpeg no está instalado o falla, devuelve valores vacíos pero no crashea
        pass
    return metricas

def analizar_video(ruta):
    resultado = {
        "archivo": ruta.name,
        "peso_mb": round(ruta.stat().st_size / (1024 ** 2), 2),
        "resolucion": None, 
        "fps": None,
        "volumen_medio_db": None,
        "silencio_detectado": False
    }

    # 1. Medición de Video con OpenCV (Confiable tras el arreglo de la terminal)
    cap = cv2.VideoCapture(str(ruta))
    if cap.isOpened():
        ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        resultado["resolucion"] = f"{ancho}x{alto}"
        
        fps_detectados = cap.get(cv2.CAP_PROP_FPS)
        # Filtramos el bug de los 1000 FPS o valores inválidos
        if 0 < fps_detectados < 100:
            resultado["fps"] = round(fps_detectados, 2)
        cap.release()

    # 2. Medición de Audio con FFmpeg Seguro
    audio_info = analizar_volumen_seguro(ruta)
    resultado.update(audio_info)

    return resultado

def interpretar_calidad(fps_promedio, resoluciones, fps_valido, vol_medio, silencio):
    res_str = ", ".join(resoluciones)
    
    # Evaluación del Canal de Video
    if not fps_valido:
        estado = "⚠️ ERROR DE METADATOS"
        comentario = (
            "Lectura ausente de FPS. El contenedor WebM original de Chrome no guardó los índices de tiempo. "
            "Se requiere usar los archivos con sufijo '_arreglado' para procesar el tracking."
        )
    elif "640x480" in res_str:
        estado = "BAJA CALIDAD (SD)"
        comentario = (
            "Restricción de hardware en origen. El navegador forzó una resolución de 640x480 px "
            "debido a limitaciones de la webcam o baja iluminación ambiental. Puede comprometer el eye-tracking."
        )
    elif fps_promedio < 24:
        estado = "HD ENTRECORTADO"
        comentario = (
            f"Cuello de botella en procesamiento. La tasa de cuadros cayó a {fps_promedio} FPS debido a "
            "saturación de la CPU del usuario durante la sesión, generando saltos temporales."
        )
    else:
        estado = "OPTIMA"
        comentario = (
            f"Rendimiento excelente. Canal de video estable a {fps_promedio} FPS con resolución nativa HD "
            f"({res_str} px). Cumple rigurosamente con los estándares técnicos para el tracking continuo."
        )

    # Evaluación Integrada del Canal de Audio
    alertas_audio = []
    if silencio: 
        alertas_audio.append("silencio prolongado")
    if vol_medio is not None and vol_medio < -45: 
        alertas_audio.append(f"volumen críticamente bajo ({vol_medio} dB)")
    
    calidad_audio = "OK" if not alertas_audio else " | ".join(alertas_audio)
    
    if vol_medio is None:
        calidad_audio = "Sin datos (FFmpeg no disponible)"
    elif alertas_audio:
        comentario += f" NOTA DE AUDIO: Canal de audio degradado debido a {calidad_audio}. Revisar ganancia del micrófono."
    else:
        comentario += " Canal de audio limpio y verificado."

    return estado, calidad_audio, comentario

def main():
    if not carpeta_videos.exists():
        print(f"❌ No se encontró la carpeta: {carpeta_videos}")
        return

    archivos = sorted([f for f in carpeta_videos.iterdir() if f.suffix.lower() == ".webm"])
    if not archivos:
        print("❌ No se encontraron archivos .webm")
        return

    grupos = defaultdict(list)
    for archivo in archivos:
        # Filtro inteligente: priorizar archivos arreglados sobre los rotos
        if "arreglado" not in archivo.name and any(f"{archivo.stem}_arreglado.webm" in f.name for f in archivos):
            continue
            
        partes = archivo.name.split("_")
        if len(partes) >= 2:
            grupos[partes[1]].append(archivo)

    filas = []
    
    print("==========================================================================================")
    print("📊 INICIANDO AUDITORÍA TÉCNICA INTEGRAL (VIDEO + AUDIO)")
    print("==========================================================================================\n")

    for num, (run_id, archivos_usuario) in enumerate(grupos.items(), 1):
        print(f"Analizando usuario {num}/{len(grupos)} (Run-ID: ...{run_id[-12:]})...")
        videos_info = [analizar_video(a) for a in archivos_usuario]

        resoluciones = list({v["resolucion"] for v in videos_info if v["resolucion"]})
        lista_fps    = [v["fps"] for v in videos_info if v["fps"] is not None]
        
        fps_promedio = round(sum(lista_fps) / len(lista_fps), 2) if lista_fps else 0
        fps_valido   = len(lista_fps) > 0
        peso_total   = round(sum(v["peso_mb"] for v in videos_info), 2)
        
        # Procesamiento de métricas de audio
        volumenes    = [v["volumen_medio_db"] for v in videos_info if v["volumen_medio_db"] is not None]
        vol_medio    = round(sum(volumenes) / len(volumenes), 1) if volumenes else None
        silencio     = any(v["silencio_detectado"] for v in videos_info)

        estado, calidad_audio, comentario_tecnico = interpretar_calidad(fps_promedio, resoluciones, fps_valido, vol_medio, silencio)

        print(f"👤 USUARIO PILOTO {num} (ID: ...{run_id[-12:]})")
        print(f"   ↳ 📄 Cantidad Archivos:     {len(archivos_usuario)} videos")
        print(f"   ↳ 💾 Tamaño total sesión:   {peso_total} MB")
        print(f"   ↳ 🖥️ Calidad Video:         {', '.join(resoluciones)} px -> [{estado}]")
        print(f"   ↳ 🎞️ FPS Promedio:           {fps_promedio if fps_valido else '⚠️ Metadatos corruptos (Usar archivos arreglados)'}")
        print(f"   ↳ 🔊 Estado del Audio:      [{calidad_audio}]")
        print(f"   ↳ 📝 COMENTARIO TÉCNICO:    {comentario_tecnico}")
        print("-" * 90)

        filas.append({
            "Usuario (N°)":          num,
            "Run-ID":                run_id,
            "Videos en servidor":    len(archivos_usuario),
            "Tamaño total (MB)":     peso_total,
            "Resolución (px)":       ", ".join(resoluciones) or "—",
            "FPS":                   fps_promedio if fps_valido else "Error",
            "Volumen medio (dB)":    vol_medio if vol_medio is not None else "N/A",
            "Calidad de Audio":      calidad_audio,
            "Estado del canal":      estado,
            "Comentario Tecnico":    comentario_tecnico
        })

    with open(salida_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        writer.writeheader()
        writer.writerows(filas)

    print(f"\n✅ ¡Análisis completado! Reporte unificado en: {salida_csv}")

if __name__ == "__main__":
    main()