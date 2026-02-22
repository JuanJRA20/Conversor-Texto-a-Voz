<!-- README.md para Conversor-Texto-a-Voz -->

# Conversor Texto a Voz

[![Build Status](https://img.shields.io/github/workflow/status/JuanJRA20/Conversor-Texto-a-Voz/CI?style=flat-square)](https://github.com/JuanJRA20/Conversor-Texto-a-Voz/actions)
[![License](https://img.shields.io/github/license/JuanJRA20/Conversor-Texto-a-Voz?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg?style=flat-square)](https://www.python.org/)
[![Issues](https://img.shields.io/github/issues/JuanJRA20/Conversor-Texto-a-Voz?style=flat-square)](https://github.com/JuanJRA20/Conversor-Texto-a-Voz/issues)

---

## 🚀 Descripción

**Conversor-Texto-a-Voz** es una solución modular Python para convertir texto, archivos y URLs a un audio natural.  
Incluye detección de idioma, silencios ajustados por signos de puntuación, motores de voz Google TTS y Pyttsx3, y una interfaz terminal amigable.  
Pensado para una experiencia profesional, escalable y flexible.

---

## 🛠️ Características

- **Entrada flexible:** texto directo, archivos `.txt`, URLs.
- **Procesamiento inteligente:** segmentación en frases/tokens, protección de bloques, análisis de idioma y silencios.
- **Audio fluido:** evita cortes entre palabras, ajusta pausas naturales según puntuación, ignora signos innecesarios.
- **Detección de idioma:** español/inglés para voz óptima.
- **Motores TTS:** Google Text-to-Speech, pyttsx3 (fallback automático).
- **Pipeline modular:** extracción → procesamiento → conversión.
- **UI Terminal profesional:** colores, barra de progreso, mensajes claros.
- **Logging completo:** auditoría, debugging y telemetría industrial.
- **Fácil de extender:** añade más idiomas, motores, lógica de silencios.

---

## 🌟 Captura de pantalla (terminal)

```
============================================
           Conversor Texto a Voz
============================================
Bienvenido al Conversor Texto a Voz.
Puedes ingresar:
 - Un texto directo
 - Una ruta de archivo de texto
 - Una URL

Procesando texto...
Generando audio (esto puede tardar unos segundos):
Progreso: [██████████████████████████] 100%
¡Audio generado exitosamente!
Archivo guardado en: audio_resultado.mp3
Gracias por usar el Conversor Texto a Voz. ¡Hasta pronto!
```

---

## 📦 Instalación

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/JuanJRA20/Conversor-Texto-a-Voz.git
   cd Conversor-Texto-a-Voz
   ```

2. **Crea un entorno virtual (recomendado):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/macOS
   venv\Scripts\activate     # En Windows
   ```
3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Uso

1. **Ejecuta el programa principal:**
   ```bash
   python main.py
   ```
2. **Sigue las instrucciones en pantalla:**
   - Introduce el texto, archivo o URL.
   - Espera la barra de progreso.
   - Recibe el archivo de audio generado.

---

## 📝 Estructura del Proyecto

```
Conversor-Texto-a-Voz/
│
├── main.py                      # Programa principal (control de pipeline)
├── requirements.txt             # Dependencias del proyecto
├── ui.py                        # Lógica de interfaz terminal
│
├── extraccion_validacion/
│   └── gestionador.py           # Extractor y validador de texto
├── procesado_datos/
│   ├── gestionador.py           # Pipeline de procesado y segmentación
│   ├── detectar_idioma.py       # Detección de idioma por línea/token
│   └── procesar_texto.py        # Tokenización, agrupación, silencios
│
├── convertor_audio/
│   ├── gestionador.py           # Gestor de generación de audio
│   ├── generador.py             # Motores TTS, generación y combinación
├── Logger.py                    # Logger modular y telemetría
│
├── README.md                    # Este archivo
└── README.txt                   # Versión texto para usuarios básicos
```

---

## 🔧 Configuración y Personalización

- **Silencios:** puedes ajustar los tiempos para cada signo en `MarcarSilencios` (`procesado_datos/procesar_texto.py`).
- **Motores de voz:** añade/edita generadores en `convertor_audio/generador.py`.
- **Logging:** modifica la configuración en `Logger.py`.

---

## 🧪 Tests

**(Recomendación)**  
Agrega tests unitarios para verificar:

- Segmentación de texto y tokens
- Detección de idioma
- Generación y combinación de audio
- Silencios naturales por puntuación

---

## 💡 Principios Profesionales

- Modularización por fases
- Interface limpia y separada
- Logging y telemetría de eventos
- Pipeline extensible y escalable
- Uso de patrones industria (SRP, modularidad, fallback, etc.)

---

## 📚 Créditos y Licencia

Proyecto desarrollado por [JuanJRA20](https://github.com/JuanJRA20)  
Licencia MIT – Libre para uso y modificación.

---

## 🧐 Contactar / Feedback

¿Tienes sugerencias o detectaste bugs?  
Abre un issue o pull request en [GitHub](https://github.com/JuanJRA20/Conversor-Texto-a-Voz/issues).

---

## 🏁 ¡Gracias por usar Conversor-Texto-a-Voz!
