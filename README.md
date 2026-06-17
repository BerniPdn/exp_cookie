# Experimento CookieJar: Lenguaje y Percepcion (jsPsych)

Este repositorio contiene la implementación del frontend para el experimento cognitivo **CookieJar**, desarrollado sobre el framework **jsPsych (v8.2.3)**. El sistema está diseñado para capturar de forma síncrona flujos de audio y video con el fin de analizar relatos verbales de imagenes combinados con métricas de seguimiento ocular remotos[cite: 1].

## 🚀 Características del Sistema
* **Línea de Tiempo Multimétodo:** Combina calibración psicofísica, pruebas de descripción verbal y evaluación emocional reactiva.
* **Aleatorización Completa:** Bloques aleatorios para las láminas de la prueba de las imagenes Cookie Theft (Variantes: Nueva Original, Nueva Invertida, Vieja Original, Vieja Invertida) y del set de imágenes emocionales OASIS[cite: 1].
* **Garantía de Persistencia:** Cola de subidas asrincrónica (`Promise-driven`) combinada con un bloque *fallback* de descarga local inmediata en formato `.webm` ante fallas de red.

---

## 🛠️ Especificaciones Técnicas de Calidad

Para asegurar datos homogéneos aptos para modelos de análisis automatizado (como *WebGazer* o descriptores de microexpresiones faciales), se restringe el hardware bajo los siguientes parámetros:

* **Resolución de Captura:** `1280 x 720` (HD 720p) mediante *constraints* de video para evitar la degradación automática a 480p que imponen los navegadores.
* **Tasa de Refresco:** `30 FPS` constantes para el registro lineal de sacadas oculares.
* **Compresión de Almacenamiento:** Bitrate forzado a `5.000.000 bps` (5 Mbps) con el códec `video/webm;codecs=vp8,opus` mediante `MediaRecorder`.

---

## 📂 Estructura Crítica del Código

* `index.html`: Inicializa jsPsych, carga las extensiones de WebGazer, define los estilos dinámicos de las tarjetas de la interfaz y estructura el *timeline* del experimento.
* `recorder.js`: Administra los estados del hardware (`start`, `stop`, `requestData`), maneja el buffer temporal (`fragmentosVideo`) y coordina la pantalla de bloqueo informativa para el usuario durante la transferencia.
* `runtime.js`: Capa de conectividad API. Gestiona las llamadas `POST` hacia los endpoints `/api/v1/record_data/` y `/api/v1/record_video/` inyectando tokens CSRF de seguridad.
* `servidor.py`: Entorno local simulado (Flask) configurado en el puerto `8002` para emular el comportamiento del backend real de Datapruebas, procesando y almacenando los archivos `.webm` físicos.

---

## 📡 Flujo de Red y Contingencias

El experimento opera bajo una arquitectura desacoplada:

1. El frontend realiza la llamada de datos generales y genera un empaquetado binario (`Blob`) con la filmación de cada tarea.
2. Si la variable `domain` apunta a un servidor sin permisos de escritura, la promesa del pipeline se interrumpe.
3. El sistema activa automáticamente la contingencia en el navegador, descargando el archivo crudo directo al ordenador del participante.

## 👥 Estado del Piloto
Fase de pruebas técnicas validada con una muestra inicial de **5 usuarios**.
Reporte de calidad: n