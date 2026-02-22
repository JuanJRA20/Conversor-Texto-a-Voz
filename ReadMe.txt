============================================
        Conversor Texto a Voz (Python)
============================================

Descripción:
-------------
Este proyecto permite convertir cualquier texto, archivo o URL en un archivo de audio de forma natural y profesional. Incluye detección de idioma, silencios personalizados por puntuación y motores de voz de Google TTS y Pyttsx3.

Características:
---------------
- Entrada: texto directo, archivos, URLs.
- Procesamiento: segmentación en frases/tokens, protección de bloques, silencios ajustados.
- Audio fluido: evita cortes entre palabras, ignora signos innecesarios y ajusta pausas.
- Detección de idioma (español/inglés) con selección óptima de voz.
- Barra de progreso y mensajes de estado en terminal.
- Logging modular para auditoría.
- Modular, escalable, fácil de extender.

Instalación:
------------
1. Clona el repositorio:
   > git clone https://github.com/JuanJRA20/Conversor-Texto-a-Voz.git
2. Activa un entorno virtual (opcional):
   > python -m venv venv
   > source venv/bin/activate
3. Instala las dependencias:
   > pip install -r requirements.txt

Uso:
----
1. Ejecuta el programa principal:
   > python main.py
2. Ingresa el texto, archivo o URL cuando se te pida.
3. Espera la barra de progreso y recibe el archivo de audio generado.

Estructura:
-----------
main.py                - Programa principal
requirements.txt       - Dependencias
ui.py                  - Interfaz terminal amigable
extraccion_validacion/ - Extracción y validación de texto
procesado_datos/       - Procesado y segmentación
convertor_audio/       - Generación y combinación de audio
Logger.py              - Logging profesional

Personalización:
----------------
- Ajusta los tiempos de silencios en procesado_datos/procesar_texto.py
- Añade idiomas o motores en convertor_audio/generador.py
- Configura logging en Logger.py

Licencia:
---------
MIT - Libre para usar y modificar.

Contacto y soporte:
-------------------
Para sugerencias, errores o mejoras, abre un issue en:
https://github.com/JuanJRA20/Conversor-Texto-a-Voz

¡Gracias por usar Conversor-Texto-a-Voz!