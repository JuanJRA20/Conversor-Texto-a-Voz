================================================================================
          PROYECTO: CONVERSOR DE TEXTO A AUDIO CON DETECCIÓN DE IDIOMA
================================================================================

DESCRIPCIÓN GENERAL
===================

Este proyecto implementa un sistema completo de conversión de texto a audio con capacidad de procesamiento inteligente de idiomas mixtos. 
El sistema está diseñado para manejar contenido en ESPAÑOL E INGLÉS, detectando automáticamente el idioma de cada segmento del texto y aplicando la 
pronunciación adecuada.

El proyecto se divide en TRES ETAPAS PRINCIPALES que trabajan de forma integrada:

1. Extracción y Validación de Datos
2. Procesamiento de Datos y Detección de Idioma
3. Conversión de Texto a Audio


================================================================================
REQUISITOS DEL SISTEMA
================================================================================

DEPENDENCIAS DE PYTHON
----------------------

Todas las dependencias necesarias están listadas en el archivo requirements.txt

DEPENDENCIAS DEL SISTEMA OPERATIVO
-----------------------------------

pyttsx3: Requiere motores TTS del sistema operativo
python-magic: Requiere la biblioteca libmagic
pydub: Requiere FFmpeg para manipulación de audio

RECURSOS NLTK
-------------

El programa descarga automáticamente los recursos necesarios de NLTK:
  - punkt (tokenización)
  - stopwords (palabras vacías en español e inglés)

================================================================================
ESTRUCTURA DEL PROYECTO
================================================================================

proyecto/
│
├── main.py                      # Archivo principal de ejecución
├── Extraccion_datos.py          # Módulo de extracción y validación
├── Procesado_datos.py           # Módulo de procesamiento e idioma
├── Convetir_Texto_Audio.py      # Módulo de conversión a audio
├── Logger.py                    # Sistema de logging personalizado
├── requirements.txt             # Dependencias del proyecto
│
└── logs/                        # Archivos de registro (generados automáticamente)
    ├── Info.log
    ├── Debug.log
    └── Warning.log

================================================================================
ETAPA 1: EXTRACCIÓN Y VALIDACIÓN DE DATOS
================================================================================

Archivo: Extraccion_datos.py

Esta etapa se encarga de IDENTIFICAR, VALIDAR Y EXTRAER el texto desde diferentes fuentes de entrada.

CLASES PRINCIPALES
------------------

1.1 TipoEntrada
---------------

Propósito: Determinar el tipo de entrada proporcionada por el usuario.

Métodos:

  - determinar_tipo(entrada, esquemas_permitidos=None)
    
    Entrada: String con texto plano, ruta de archivo o URL
    
    Salida: Tupla (tipo, valor) donde tipo puede ser:
      - "Textoplano": Entrada directa de texto
      - "Archivo": Ruta a un archivo local
      - "URL": Dirección web válida
    
    Comportamiento: 
      - Verifica primero si es un archivo existente
      - Luego valida si es una URL con formato correcto
      - Por defecto, clasifica como texto plano
      - Añade automáticamente http:// si falta el esquema en URLs

1.2 ValidadorDatos
------------------

Propósito: Asegurar la integridad y validez de los datos antes de procesarlos.

Métodos:

  - texto(entrada)
    
    Entrada: String con texto
    
    Validaciones: 
      - Verifica que sea tipo str
      - Comprueba que no esté vacío
    
    Salida: True si es válido, False en caso contrario

  - archivo(entrada, mime_esperado=None)
    
    Entrada: Ruta al archivo
    
    Validaciones:
      - Verifica existencia del archivo
      - Comprueba que no esté vacío
      - Detecta tipo MIME usando python-magic
      - Valida tipo MIME si se especifica uno esperado
    
    Salida: True si es válido, False en caso contrario

  - url(entrada)
    
    Entrada: String con URL
    
    Validaciones:
      - Valida formato de URL con librería validators
      - Verifica que el dominio sea válido
    
    Salida: True si es válido, False en caso contrario

1.3 ExtraccionDatos
-------------------

Propósito: Extraer el contenido textual de las diferentes fuentes.

Métodos:

  - textoplano(entrada)
    
    Entrada: String con texto
    Salida: Texto limpio (sin espacios al inicio/final)

  - archivo(entrada)
    
    Entrada: Ruta al archivo
    Formatos soportados: .txt, .json, .pdf
    Salida: Texto extraído del archivo
    
    Comportamiento:
      - TXT: Lee el contenido completo
      - JSON: Extrae valores de diccionarios o elementos de listas
      - PDF: Extrae texto de todas las páginas usando PyPDF2

  - url(entrada, parser='lxml')
    
    Entrada: URL válida
    Salida: Texto extraído de la página web
    
    Estrategias (en orden de prioridad):
      1. newspaper3k: Extracción especializada de artículos
      2. lxml: Parseo rápido de encabezados y párrafos
      3. BeautifulSoup: Fallback con parseo personalizable
    
    Elementos extraídos: Encabezados (h1, h2, h3) y párrafos (p)

================================================================================
ETAPA 2: PROCESAMIENTO DE DATOS Y DETECCIÓN DE IDIOMA
================================================================================

Archivo: Procesado_datos.py

Esta etapa TOKENIZA EL TEXTO Y DETECTA EL IDIOMA de cada segmento, preparando los datos para la conversión a audio.

CARACTERÍSTICAS ESPECIALES
---------------------------

Detección de Idioma Multi-nivel
--------------------------------

El sistema implementa un enfoque JERÁRQUICO de detección:

  1. Nivel de línea: Detecta el idioma predominante de cada oración
  2. Nivel de palabra: Analiza tokens individuales, especialmente los protegidos
  3. Nivel de contexto: Aplica heurísticas según el entorno


Manejo de Textos Mixtos
------------------------

El sistema está optimizado para textos con ESPAÑOL e INGLÉS MEZCLADOS:

  - Tokens protegidos: Palabras entre comillas (" ", ' ') o paréntesis (( )) se analizan individualmente
  
  - Prefijos en inglés: Detecta secuencias iniciales de tokens en inglés (ej: "C++ programming en español")
  
  - Diacríticos fuertes: Presencia de ñ, á, é, etc. fuerza clasificación como español
  
  - Stopwords: Usa listas de palabras comunes para mejorar detección


CLASES PRINCIPALES
------------------

2.1 Idiomas
-----------

Propósito: Gestionar la detección de idioma usando langid y heurísticas.

Métodos:

  - normalizacion_probabilidad(probabilidad_base)
    
    Entrada: Puntuación de langid (puede ser negativa)
    Salida: Probabilidad normalizada (0.0 a 0.99)
    
    Escala:
      >= 3.0: 99% de confianza
      >= 1.0: 90% de confianza
      0.0 a 1.0: 80% de confianza
      Valores negativos: 50-70% de confianza

  - detectar_idioma_texto(texto)
    
    Entrada: String de texto
    Salida: Tupla (idioma, probabilidad)
      - idioma: "español", "ingles" o None
      - probabilidad: Float entre 0.0 y 1.0
    
    Proceso:
      1. Verifica diacríticos españoles (retorna español con probabilidad 1.0)
      2. Usa langid para clasificar
      3. Normaliza la probabilidad
      4. Retorna None si el idioma no es español ni inglés


2.2 ProcesadoDatos
------------------

Propósito: Tokenizar y clasificar el texto completo.

Métodos:

  - procesar_texto(texto)
    
    Entrada: String con el texto completo
    
    Salida: Lista de listas de tuplas [(palabra, idioma), ...]
      - Cada sublista representa una línea/oración
      - Cada tupla contiene: (token_string, idioma_string_o_None)
      - idioma es None para marcadores de puntuación (pausas)
    
    Estructura de salida:
      [
          [("Hello", "ingles"), ("world", "ingles"), (".", None)],
          [("Hola", "español"), ("mundo", "español"), (".", None)]
      ]

  - procesar_lineas(linea, idioma_hint=None)
    
    Entrada: 
      - linea: String con una oración
      - idioma_hint: Idioma sugerido (opcional)
    
    Salida: Lista de tuplas [(token, idioma), ...]
    
    Proceso:
      1. Detecta idioma predominante de la línea
      2. Tokeniza usando word_tokenize de NLTK
      3. Limpia y clasifica tokens con limpiar_palabras
      4. Detecta prefijos en inglés (3+ tokens consecutivos)
      5. Procesa tokens protegidos individualmente
      6. Aplica heurísticas contextuales

  - procesar_palabras(palabra, idioma_hint=None, is_parenthesized=False, prob_linea='low')
    
    Decorado con: @lru_cache(maxsize=4096) para optimización
    
    Entrada:
      - palabra: Token individual (lowercase)
      - idioma_hint: Idioma sugerido
      - is_parenthesized: True si está entre paréntesis
      - prob_linea: Confianza del idioma de línea ('high', 'med', 'low')
    
    Salida: Tupla (palabra, idioma, probabilidad) o None
    
    Lógica especial para paréntesis:
      - Requiere probabilidad >= 0.95 para aceptar langid
      - Si la línea es fuertemente inglesa y token >= 0.90, acepta inglés
      - De lo contrario, usa idioma_hint o fuerza español

  - limpiar_palabras(palabras)
    
    Entrada: Lista de tokens crudos de NLTK
    
    Salida: Lista de tuplas [(token, tipo), ...]
      Tipos: 'palabra', 'palabra_protegida', 'palabras_protegidas', 'puntuacion'
    
    Proceso:
      1. Detecta tokens entre comillas o paréntesis
      2. Clasifica si son single-word o multi-word
      3. Separa puntuación pegada a palabras
      4. Marca puntuación como tipo especial


REGLAS DE DETECCIÓN AVANZADAS
------------------------------

Tokens Protegidos
-----------------

  Single-word protegido: "C++"  → ('C++', 'palabra_protegida')

  Multi-word protegido:
    "Vox Populi Vox Dei"  → ('Vox Populi Vox Dei', 'palabras_protegidas')

Sufijos Españoles
-----------------

Si un token tiene sufijos como -ción, -mente, -dad, -able, etc., y langid lo clasifica como inglés, se FUERZA A ESPAÑOL para evitar errores.

Símbolos en Tokens
------------------

  - C++ se expande a "C plus plus"
  - C# se expande a "C sharp"

================================================================================
ETAPA 3: CONVERSIÓN DE TEXTO A AUDIO
================================================================================

Archivo: Convetir_Texto_Audio.py

Esta etapa SINTETIZA EL AUDIO a partir de los tokens clasificados, respetando 
el idioma de cada segmento.


MOTORES TTS UTILIZADOS
-----------------------

1. gTTS (Google Text-to-Speech): Motor principal
   - Requiere conexión a internet
   - Alta calidad de voz
   - Soporta español (es) e inglés (en)

2. pyttsx3: Motor de respaldo
   - Funciona offline
   - Usa voces del sistema operativo
   - Se activa si gTTS falla

CLASE PRINCIPAL
---------------

3.1 ConvertidorTextoVoz
-----------------------

Métodos:

  - convertir_texto_voz(texto_idioma, nombre_salida="resultado.mp3", mostrar_progreso=True)
    
    Entrada:
      - texto_idioma: Lista de tuplas [(palabra, idioma), ...]
      - nombre_salida: Nombre del archivo MP3 resultante
      - mostrar_progreso: Mostrar barra de progreso con tqdm
    
    Salida: Ruta al archivo MP3 generado o None si falla
    
    Proceso:
      1. Valida que la entrada sea una lista de tuplas
      2. Agrupa tokens consecutivos del mismo idioma en bloques
      3. Para cada bloque:
         - Genera audio con generaraudio()
         - Carga el segmento en memoria (AudioSegment)
      4. Procesa marcadores de puntuación (idioma=None):
         - . → 900ms de silencio
         - , → 230ms de silencio
         - ; / : → 400ms de silencio
         - \n → 800ms de silencio
      5. Combina todos los segmentos con combinaraudios()
      6. Exporta el archivo final en formato MP3

  - generaraudio(palabras, idioma)
    
    Entrada:
      - palabras: Lista de strings a convertir
      - idioma: "español" o "ingles"
    
    Salida: Tupla (AudioSegment, motor_usado) o None
    
    Estrategia en cascada:
      1. Intenta con generaraudio_gtts()
      2. Si falla, intenta con generaraudio_pytts()
      3. Si ambos fallan, retorna None y registra error

  - generaraudio_gtts(palabras, idioma)
    
    Entrada: Lista de palabras y código de idioma
    
    Proceso:
      1. Expande símbolos (C++ → "C plus plus")
      2. Mapea idioma: español → es, ingles → en
      3. Crea objeto gTTS
      4. Guarda en archivo temporal
      5. Carga como AudioSegment
      6. Elimina archivo temporal
    
    Salida: AudioSegment o None

  - generaraudio_pytts(palabras, idioma, velocidad=150, volumen=1.0)
    
    Entrada: Lista de palabras, idioma, parámetros de voz
    
    Proceso:
      1. Inicializa motor pyttsx3
      2. Configura velocidad y volumen
      3. Guarda en archivo temporal
      4. Carga como AudioSegment
      5. Elimina archivo temporal
    
    Salida: AudioSegment o None

  - combinaraudios(archivos, nombre_salida)
    
    Entrada:
      - archivos: Lista de AudioSegment o rutas de archivos
      - nombre_salida: Nombre del archivo MP3 resultante
    
    Salida: Ruta al archivo combinado o None
    
    Técnicas de combinación:
      - Silencio: Concatenación directa sin crossfade
      - Habla larga (>800ms): Crossfade de 10ms para suavizar
      - Habla corta: Sin crossfade + padding de 40ms para evitar pérdida 
        de fonemas

  - nombre_archivo_temporal(palabras, idioma)
    
    Salida: String con formato audio_temp_{uuid}_{idioma}.mp3
    Propósito: Evitar colisiones de nombres en archivos temporales

GESTIÓN DE SILENCIOS
---------------------

El sistema inserta pausas naturales según la puntuación:

  Símbolo     Duración
  -------     --------
  .           900 ms
  \n          800 ms
  ; : ( )     400 ms
  ,           230 ms

Optimización: Si dos silencios consecutivos se detectan, se fusiona tomando la duración máxima para evitar fragmentación excesiva.

================================================================================
SISTEMA DE LOGGING
================================================================================

Archivo: Logger.py

Implementa un sistema de registro MULTI-NIVEL con rotación automática de 
archivos.

CLASE Telemetriaindustrial
---------------------------

Características:

  - Rotación diaria: Los logs se rotan a medianoche
  - Retención: Mantiene logs de los últimos 7 días por defecto
  - Niveles separados: Cada nivel tiene su propio archivo
    - Info.log: Eventos informativos (nivel INFO)
    - Debug.log: Información de depuración (nivel DEBUG)
    - Warning.log: Advertencias (nivel WARNING)
    - Consola (stderr): Solo errores críticos (nivel ERROR)


DECORADOR @logger_modular
--------------------------

Funcionalidad:
  - Registra inicio y fin de funciones
  - Mide tiempo de ejecución
  - Captura y registra excepciones
  - Implementa lazy logging (solo procesa si el nivel está activo)
  - Procesa datos de forma inteligente para evitar colapsos con estructuras grandes

Uso:
  @logger_modular(logger)
  def mi_funcion(param):
      # código
      return resultado

================================================================================
INTEGRACIÓN EN main.py
================================================================================

FLUJO DE EJECUCIÓN
------------------

Usuario ingresa entrada
         ↓
extraccion_y_validacion()
    ├── TipoEntrada.determinar_tipo()
    ├── ValidadorDatos.texto/archivo/url()
    └── ExtraccionDatos.textoplano/archivo/url()
         ↓
procesado_datos()
    └── ProcesadoDatos.procesar_texto()
         ├── sent_tokenize (NLTK)
         ├── procesar_lineas()
         │   ├── detectar_idioma_texto()
         │   ├── word_tokenize (NLTK)
         │   ├── limpiar_palabras()
         │   └── procesar_palabras()
         └── Retorna: [[(token, idioma), ...], ...]
         ↓
conversion_texto_audio()
    └��─ ConvertidorTextoVoz.convertir_texto_voz()
         ├── Agrupa tokens por idioma
         ├── generaraudio() para cada bloque
         │   ├── generaraudio_gtts()
         │   └── generaraudio_pytts() (fallback)
         ├── Inserta silencios según puntuación
         ├── combinaraudios()
         └── Exporta resultado.mp3
         ↓
Archivo MP3 generado


FUNCIONES DEL MAIN
------------------

1. extraccion_y_validacion(texto)
   
   Entrada: String con texto/ruta/URL
   Salida: Texto extraído o None
   
   Proceso:
     - Determina tipo de entrada
     - Selecciona validador y extractor apropiados del diccionario handlers
     - Valida y extrae datos
     - Registra eventos en el logger

2. procesado_datos(datos)
   
   Entrada: Texto extraído
   Salida: Lista de listas de tuplas [[(token, idioma), ...], ...] o None
   
   Proceso: Llama a ProcesadoDatos.procesar_texto()

3. conversion_texto_audio(datos_procesados)
   
   Entrada: Lista de listas de tuplas
   Salida: Ruta al archivo MP3 o None
   
   Proceso:
     - Aplana la estructura (lista de listas → lista simple)
     - Llama a ConvertidorTextoVoz.convertir_texto_voz()
     - Muestra progreso con tqdm

4. main()
   
   Función principal decorada con @logger_modular
   
   Flujo:
     1. Solicita entrada al usuario
     2. Ejecuta extracción y validación
     3. Ejecuta procesamiento
     4. Ejecuta conversión
     5. Maneja errores en cada etapa
     6. Muestra mensajes informativos al usuario


EJEMPLO DE USO
--------------

$ python main.py
Ingrese texto, ruta de archivo o URL a convertir:
> The C++ programming language es muy poderoso. "Machine Learning" está 
  revolucionando la tecnología.

Iniciando programa...
Iniciando conversion de texto a audio...
Convirtiendo texto a audio: 100%|██████████| 25/25 [00:03<00:00,  7.21token/s]
Conversion finalizada. Archivo listo: resultado.mp3


================================================================================
RESULTADOS ESPERADOS
================================================================================

ARCHIVO DE SALIDA
-----------------

  - Formato: MP3 (MPEG Audio Layer 3)
  - Nombre por defecto: resultado.mp3
  - Ubicación: Directorio de ejecución del script
  - Características:
    - Audio multi-idioma con transiciones suaves
    - Pausas naturales según puntuación
    - Pronunciación correcta según idioma detectado

================================================================================
LIMITACIONES Y CONSIDERACIONES
================================================================================

IDIOMAS SOPORTADOS
------------------

  - Únicamente español e inglés: El sistema está optimizado para estos dos 
    idiomas
  - Otros idiomas serán clasificados como el idioma principal por defecto 
    (español)
  - La configuración de langid está limitada a ['es', 'en']


REQUISITOS DE CONEXIÓN
-----------------------

  - gTTS requiere internet: Si no hay conexión, se usará pyttsx3 automáticamente
  - Extracción de URLs: Requiere conexión para descargar contenido web

PRECISIÓN DE DETECCIÓN
-----------------------

  - Textos cortos: Palabras de 1-3 caracteres pueden ser ambiguas
  - Nombres propios: Pueden clasificarse incorrectamente (ej: "Paris" como 
    inglés)
  - Jerga técnica: Términos mixtos pueden requerir comillas para forzar 
    detección


RENDIMIENTO
-----------

  - Cache de LRU: procesar_palabras cachea hasta 4096 palabras para optimizar
  - Archivos temporales: Se crean y eliminan automáticamente durante la 
    conversión
  - Memoria: Los segmentos de audio se mantienen en memoria para evitar I/O 
    excesivo

================================================================================
EJEMPLOS DE ENTRADA SOPORTADOS
================================================================================

Texto Plano
-----------
  python main.py
  > El framework Django es muy popular. "Machine Learning" está en auge.

Archivo de Texto
----------------
  python main.py
  > /home/usuario/documentos/articulo.txt

Archivo PDF
-----------
  python main.py
  > C:\Users\Usuario\Documentos\paper.pdf

URL de Artículo
---------------
  python main.py
  > https://es.wikipedia.org/wiki/Inteligencia_artificial

Archivo JSON
------------
  python main.py
  > datos.json

================================================================================
POSIBLES MEJORAS FUTURAS 
================================================================================

1. Soporte multi-idioma: Ampliar a francés, alemán, portugués, etc.
2. Voces personalizables: Permitir selección de voz (masculina/femenina)
3. Control de velocidad: Parámetro global para ajustar velocidad de habla
4. Formato de salida: Soporte para WAV, OGG, FLAC además de MP3
5. API REST: Exponer funcionalidad como servicio web
6. GUI: Interfaz gráfica para facilitar el uso
7. Detección de emociones: Ajustar entonación según contexto

================================================================================
CONTACTO Y SOPORTE
================================================================================

Para reportar problemas o sugerencias, revisar los archivos de log generados en:
  - Info.log
  - Debug.log
  - Warning.log

Los logs proporcionan información detallada sobre el procesamiento y cualquier error que pueda ocurrir.

================================================================================
¡Gracias por usar el Conversor de Texto a Audio!
================================================================================