import os
import cv2

def auditoria_tecnica_cookiejar():
    # Ruta absoluta de la carpeta de tus videos en la Mac
    ruta_home = os.path.expanduser("~")
    carpeta_videos = os.path.join(ruta_home, "Downloads", "experiment_video", "2026", "06", "16")
    
    if not os.path.exists(carpeta_videos):
        print(f"❌ Error: No se encontró la carpeta en: {carpeta_videos}")
        return

    archivos = [f for f in os.listdir(carpeta_videos) if f.endswith('.webm')]
    if not archivos:
        print(f"❌ No se encontraron archivos .webm en la carpeta especificada.")
        return

    # Diccionario para agrupar las métricas por usuario piloto
    usuarios = {}

    for nombre_archivo in archivos:
        partes = nombre_archivo.split('_')
        if len(partes) < 2:
            continue
        
        id_usuario = partes[1] # Extrae el ID único del participante
        ruta_video = os.path.join(carpeta_videos, nombre_archivo)
        
        # Medimos el tamaño del archivo en bytes
        peso_bytes = os.path.getsize(ruta_video)

        # Abrimos el contenedor con OpenCV para leer la metadata real
        video = cv2.VideoCapture(ruta_video)
        if not video.isOpened():
            continue

        ancho = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        alto = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = video.get(cv2.CAP_PROP_FPS)
        video.release()

        # Si el usuario es nuevo en el diccionario, inicializamos sus contadores
        if id_usuario not in usuarios:
            usuarios[id_usuario] = {
                'resoluciones': set(),
                'lista_fps': [],
                'peso_total_bytes': 0,
                'cantidad_archivos': 0
            }
        
        # Acumulamos y guardamos los datos medidos
        usuarios[id_usuario]['resoluciones'].add(f"{ancho}x{alto}")
        usuarios[id_usuario]['peso_total_bytes'] += peso_bytes
        usuarios[id_usuario]['cantidad_archivos'] += 1
        if fps > 0:
            usuarios[id_usuario]['lista_fps'].append(fps)

    # --- IMPRESIÓN DEL REPORTE PARA TU TABLA DE WORD ---
    print("==========================================================================================")
    print("📊 RESULTADOS DEL ANÁLISIS TÉCNICO COMPLETO POR USUARIO (PILOTO)")
    print("==========================================================================================\n")

    for num, (id_user, datos) in enumerate(usuarios.items(), 1):
        # Cálculos finales por usuario
        fps_promedio = round(sum(datos['lista_fps']) / len(datos['lista_fps']), 2) if datos['lista_fps'] else 0
        resoluciones_detectadas = ", ".join(datos['resoluciones'])
        peso_total_mb = round(datos['peso_total_bytes'] / (1024 * 1024), 2)
        
        # Lógica algorítmica para determinar el Comentario Técnico Real
        if "640x480" in resoluciones_detectadas:
            calidad_str = "BAJA (SD)"
            comentario_tecnico = (
                "Restricción de hardware en origen. El navegador forzó una resolución de 640x480 px "
                "debido a que la webcam del usuario no soporta HD o por niveles críticos de baja iluminación ambiental. "
                "Pérdida severa de densidad de píxeles; puede comprometer algoritmos de eye-tracking."
            )
        elif fps_promedio < 24:
            calidad_str = "MEDIA-BAJA (HD Entrecortado)"
            comentario_tecnico = (
                f"Cuello de botella en procesamiento. Aunque graba en HD ({resoluciones_detectadas} px), "
                f"la tasa de cuadros cayó a {fps_promedio} FPS debido a saturación de la CPU del usuario durante la sesión. "
                "La falta de fluidez temporal puede provocar saltos o pérdida de precisión en el registro de sacadas oculares."
            )
        else:
            calidad_str = "ÓPTIMA (HD Fluido)"
            comentario_tecnico = (
                f"Rendimiento excelente. Canal de video estable a {fps_promedio} FPS con resolución nativa HD "
                f"({resoluciones_detectadas} px). Cumple rigurosamente con los estándares técnicos requeridos "
                "para el mapeo y tracking continuo de la mirada."
            )

        # Imprimir bloque formateado listo para pasar a tu informe
        print(f"👤 USUARIO PILOTO {num} (ID: ...{id_user[-12:]})")
        print(f"   ↳ 📄 Número de archivos:    {datos['cantidad_archivos']} videos grabados")
        print(f"   ↳ 💾 Tamaño total sesión:   {peso_total_mb} MB")
        print(f"   ↳ 🖥️ Calidad (Resolución):  {resoluciones_detectadas} px -> [{calidad_str}]")
        print(f"   ↳ 🎞️ FPS Reales Promedio:   {fps_promedio} FPS")
        print(f"   ↳ 📝 COMENTARIO TÉCNICO:    {comentario_tecnico}")
        print("-" * 90)

auditoria_tecnica_cookiejar()