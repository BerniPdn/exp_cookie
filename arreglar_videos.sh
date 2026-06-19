#!/bin/bash
#para correr en terminal: ./arreglar_videos.sh

# 1. Definir los nombres de las carpetas
ORIGEN="videos_cookie_piloto"
DESTINO="videos_cookie_piloto_arreglados"

# 2. Crear la carpeta de destino si no existe
if [ ! -d "$DESTINO" ]; then
    mkdir "$DESTINO"
    echo "📁 Carpeta '$DESTINO' creada con éxito."
fi

echo "🚀 Iniciando el procesamiento de videos..."
echo "----------------------------------------"

# Ignorar mayúsculas/minúsculas en la extensión (.webm o .WEBM)
shopt -s nocaseglob

# 3. Recorrer los videos de la carpeta origen
for f in "$ORIGEN"/*.webm; do
    # Verificar si realmente hay archivos en la carpeta
    [ -e "$f" ] || continue
    
    # Extraer el nombre del archivo sin la ruta externa
    nombre_completo=$(basename "$f")
    
    # Quitarle la extensión .webm al nombre para poder agregarle el sufijo
    nombre_sin_extension="${nombre_completo%.*}"
    
    # Definir el nuevo nombre con la palabra arreglado
    nuevo_nombre="${nombre_sin_extension}_arreglado.webm"
    
    echo "🎬 Arreglando: $nombre_completo ➡️ $nuevo_nombre"
    
    # Ejecutar ffmpeg guardándolo en la carpeta de destino
    ffmpeg -i "$f" -fflags +genpts -c copy "$DESTINO/$nuevo_nombre" -loglevel quiet
done

# Desactivar la opción por seguridad
shopt -u nocaseglob

echo "----------------------------------------"
echo "✨ ¡Listo! Todos los videos modificados se guardaron en '$DESTINO'."