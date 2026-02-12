<div align="center">

# 🎙️ Conversor de Texto a Voz con Detección de Idioma

### Sistema Inteligente de Text-to-Speech con Procesamiento Multilingüe (ES/EN)

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)]()

</div>

---

## 📖 Descripción

Sistema completo de **conversión de texto a audio** con capacidad de procesamiento inteligente de idiomas mixtos. El sistema está diseñado para manejar contenido en **Español e Inglés**, detectando automáticamente el idioma de cada segmento del texto y aplicando la pronunciación adecuada.

### ✨ Características Principales

- 🌐 **Detección automática de idioma** a nivel de línea y palabra
- 📄 **Múltiples fuentes de entrada**: Texto plano, archivos (TXT, PDF, JSON) y URLs
- 🎯 **Procesamiento inteligente** con NLTK y langid
- 🔊 **Conversión de alta calidad** con gTTS y pyttsx3 como respaldo
- 📊 **Sistema de logging robusto** con rotación de archivos
- 🔍 **Manejo de contenido mixto** (español e inglés en el mismo texto)

---

## 🏗️ Arquitectura del Proyecto

El proyecto se divide en **tres etapas principales**:

```
┌─────────────────────────────────────────────────────────┐
│                    FLUJO DEL SISTEMA                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣ EXTRACCIÓN Y VALIDACIÓN                            │
│     ├─ Detección de tipo de entrada                    │
│     ├─ Validación de datos                             │
│     └─ Extracción desde múltiples fuentes              │
│                                                         │
│  2️⃣ PROCESAMIENTO DE DATOS                             │
│     ├─ Tokenización con NLTK                           │
│     ├─ Detección de idioma con langid                  │
│     └─ Clasificación inteligente de segmentos          │
│                                                         │
│  3️⃣ CONVERSIÓN A AUDIO                                 │
│     ├─ Generación de audio por bloques                 │
│     ├─ Conversión con gTTS/pyttsx3                     │
│     └─ Combinación de segmentos con pydub              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 Estructura del Proyecto

```
Conversor-Texto-a-Voz/
│
├── main.py                      # Punto de entrada principal
├── Extraccion_datos.py          # Módulo de extracción y validación
├── Procesado_datos.py           # Módulo de procesamiento de idioma
├── Convetir_Texto_Audio.py      # Módulo de conversión a audio
├── Logger.py                    # Sistema de logging personalizado
├── requirements.txt             # Dependencias del proyecto
├── .gitignore                   # Archivos ignorados por Git
│
└── logs/                        # Archivos de log (generados automáticamente)
    ├── Info.log
    ├── Debug.log
    └── Warning.log
```

---

## 🚀 Instalación

### Requisitos Previos

- **Python 3.8+**
- **FFmpeg** (para manipulación de audio con pydub)
- **libmagic** (para detección de tipos de archivo)

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/JuanJRA20/Conversor-Texto-a-Voz.git
cd Conversor-Texto-a-Voz
```

### Paso 2: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 3: Instalar FFmpeg (según tu sistema operativo)

**Windows:**
```bash
# Usar chocolatey
choco install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg libmagic1
```

---

## 💻 Uso

### Ejemplo Básico

```python
from main import extraccion_y_validacion, procesado_datos, conversion_audio

# 1. Extraer y validar el texto
texto = "Tu texto aquí o ruta de archivo"
datos_extraidos = extraccion_y_validacion(texto)

# 2. Procesar y detectar idioma
datos_procesados = procesado_datos(datos_extraidos)

# 3. Convertir a audio
conversion_audio(datos_procesados, nombre_salida="resultado.mp3")
```

### Fuentes de Entrada Soportadas

#### 📝 Texto Plano
```python
texto = "La programación es esencial. Programming is an essential skill."
datos = extraccion_y_validacion(texto)
```

#### 📄 Archivo de Texto
```python
archivo = "documento.txt"
datos = extraccion_y_validacion(archivo)
```

#### 🌐 URL
```python
url = "https://ejemplo.com/articulo"
datos = extraccion_y_validacion(url)
```

#### 📕 PDF
```python
pdf = "documento.pdf"
datos = extraccion_y_validacion(pdf)
```

---

## 🧩 Módulos Principales

### 1️⃣ **Extracción de Datos** (`Extraccion_datos.py`)

**Clases:**
- `TipoEntrada`: Determina el tipo de entrada (archivo, URL, texto plano)
- `ValidadorDatos`: Valida la integridad de los datos
- `ExtraccionDatos`: Extrae texto desde diferentes fuentes

**Formatos soportados:**
- Texto plano
- Archivos TXT
- Archivos PDF
- Archivos JSON
- URLs (con extracción mediante BeautifulSoup y Newspaper3k)

### 2️⃣ **Procesamiento de Datos** (`Procesado_datos.py`)

**Clases:**
- `Idiomas`: Detección de idioma usando langid y heurísticas
- `ProcesadoDatos`: Tokenización y clasificación de texto

**Características:**
- Detección a nivel de línea
- Manejo especial de comillas y paréntesis
- Caché con `lru_cache` para optimización
- Soporte para contenido mixto español/inglés

### 3️⃣ **Conversión a Audio** (`Convetir_Texto_Audio.py`)

**Clase:**
- `ConvertidorTextoVoz`: Generación y combinación de audio

**Tecnologías:**
- **gTTS** (Google Text-to-Speech) - Primera opción
- **pyttsx3** - Respaldo offline
- **pydub** - Combinación de segmentos de audio

### 4️⃣ **Sistema de Logging** (`Logger.py`)

**Clase:**
- `Telemetriaindustrial`: Logger personalizado con rotación

**Características:**
- Rotación diaria de logs
- Filtros por nivel (INFO, DEBUG, WARNING, ERROR)
- Salida a archivos y consola

---

## 📊 Dependencias Principales

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `gTTS` | 2.5.4 | Conversión texto a voz (Google) |
| `pyttsx3` | 2.99 | Conversión texto a voz (offline) |
| `nltk` | 3.9.2 | Procesamiento de lenguaje natural |
| `langid` | 1.1.6 | Detección de idioma |
| `pydub` | 0.25.1 | Manipulación de audio |
| `PyPDF2` | 3.0.1 | Lectura de PDFs |
| `BeautifulSoup4` | 4.14.3 | Parsing de HTML |
| `newspaper3k` | 0.2.8 | Extracción de artículos web |

Ver archivo completo: [`requirements.txt`](requirements.txt)

---

## 🎯 Casos de Uso

### Uso 1: Convertir un artículo web
```python
url = "https://ejemplo.com/noticia"
datos = extraccion_y_validacion(url)
procesados = procesado_datos(datos)
conversion_audio(procesados, "noticia.mp3")
```

### Uso 2: Procesar un documento PDF
```python
pdf = "documento_tecnico.pdf"
datos = extraccion_y_validacion(pdf)
procesados = procesado_datos(datos)
conversion_audio(procesados, "documento_audio.mp3")
```

### Uso 3: Texto mixto español-inglés
```python
texto_mixto = """
La inteligencia artificial es fascinante.
Artificial intelligence is changing the world.
El futuro está aquí.
"""
datos = extraccion_y_validacion(texto_mixto)
procesados = procesado_datos(datos)
conversion_audio(procesados, "mixto.mp3")
```

---

## 🔧 Configuración Avanzada

### Personalizar el Logger

```python
from Logger import Telemetriaindustrial

# Logger con retención de 14 días
logger = Telemetriaindustrial("MiApp", tiempo=14).logger
```

### Cambiar idioma por defecto

En `Procesado_datos.py`:
```python
idioma_principal = 'español'  # Cambiar a 'ingles' si prefieres
```

---

## 📝 Roadmap

- [ ] Soporte para más idiomas (francés, alemán, italiano)
- [ ] Interfaz gráfica (GUI) con tkinter o PyQt
- [ ] API REST con Flask/FastAPI
- [ ] Mejoras en la detección de idioma
- [ ] Soporte para más formatos de entrada (DOCX, EPUB)
- [ ] Configuración de velocidad y tono de voz

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz un Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

**Juan José Rodríguez Álvarez**

- GitHub: [@JuanJRA20](https://github.com/JuanJRA20)
- Email: juanrodriguez.a20@gmail.com

---

## 🙏 Agradecimientos

- [gTTS](https://github.com/pndurette/gTTS) por la excelente librería de TTS
- [NLTK](https://www.nltk.org/) por las herramientas de NLP
- [langid](https://github.com/saffsd/langid.py) por la detección de idioma

---

<div align="center">

### ⭐ Si este proyecto te fue útil, considera darle una estrella ⭐

**Hecho con ❤️ y Python**

</div>
