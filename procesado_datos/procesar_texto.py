#Importacion de las librerias necesarias:

#Librerias internas de python
import re
from functools import lru_cache

#librerias externas 
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import langid
from abc import ABC, abstractmethod
#Importacion de los modulos desarrollados en el proyecto
from Logger import Telemetriaindustrial
from procesado_datos.detectar_idioma import DetectarIdioma as Idiomas
from procesado_datos.limpeza_texto import limpiar_palabras as LimpiarTexto
#Configuracion de nltk: descargar recursos necesarios para tokenización y stopwords, 
#con manejo de excepciones para evitar errores si ya están descargados.
nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except Exception:
    nltk.download('stopwords', quiet=True)

#precargar stopwords para evitar llamadas repetidas
try:
    STOP_ES = set(stopwords.words('spanish'))
except Exception:
    STOP_ES = set()
try:
    STOP_EN = set(stopwords.words('english'))
except Exception:
    STOP_EN = set()

#Configuracion del logger personalizado para esta etapa del proyecto
logger = Telemetriaindustrial("Procesado_datos").logger

# Definimos un idioma principal por defecto para casos ambiguos.
idioma_principal = 'español'

# Configuración de langid para limitar a español e inglés, mejorando precisión en textos mixtos.
langid.set_languages(['es', 'en'])



# Segunda clase: ProcesadoDatos
class ProcesadoDatos(ABC):
    @abstractmethod
    def procesar(self, texto: str):
        pass


class ProcesarTexto(ProcesadoDatos):

    def __init__(self, logger=None):
        self.logger = logger
    # Método estático para procesar un texto completo, segmentándolo en líneas y clasificando cada token con su idioma, 
    # aplicando reglas especiales para tokens protegidos por comillas o paréntesis.
    
    def procesar(self, texto: str):
        # Manejo de casos vacíos o no string para evitar errores en el procesamiento de texto.
        if texto is None:
            return []
        
        # Reemplazar saltos de línea por espacios para evitar problemas en la tokenización, pero mantener la segmentación por oraciones.
        texto = texto.replace("\n", " ")

        # Segmentar el texto en líneas utilizando sent_tokenize, luego procesar cada línea individualmente con procesar_lineas
        lineas = sent_tokenize(texto)
        resultado = []

        # Bucle para procesar cada línea del texto, aplicando la función de procesamiento de líneas definida en la clase
        for linea in lineas: 

            # Limpiar espacios en blanco al inicio y fin de la línea
            linea = linea.strip()

            if not linea: # Si la línea queda vacía después de limpiar, se omite para evitar procesar líneas sin contenido.
                continue

            # Procesar la línea utilizando el método procesar_lineas, que devuelve una lista de tuplas (token, idioma) para cada token en la línea.
            procesado = self.Procesarlineas.procesar(linea)

            if procesado: # Comprobamos que la linea procesada no este vacia
                # Si la última tupla de la línea procesada no es un punto con idioma None, se añade un marcador de fin de línea con un punto 
                # y idioma None para indicar el final de la línea.
                if not (len(procesado) > 0 and procesado[-1][0] == '.' and procesado[-1][1] is None):
                    procesado.append(('.', None))

            # Se añade la línea procesada al resultado final, que es una lista de líneas, cada una con su lista de tuplas (token, idioma).
            resultado.append(procesado) 

        return resultado #Devuelve la lista de líneas procesadas, cada línea con su lista de tuplas (token, idioma).

    # Método estático para procesar una línea individual, aplicando reglas de detección de idioma y clasificación de tokens,
    # con manejo especial para tokens protegidos por comillas o paréntesis.
class Procesarlineas(ProcesadoDatos):
    def __init__(self, logger=None):
        self.logger = logger

    def procesar(self, linea, idioma_hint=None):

        # Lista para almacenar los tokens procesados de la línea, cada token es una tupla (token, idioma)
        tokens_obtenidos = []

        # Detectar el idioma de la línea utilizando el método de detección de idioma definido en la clase Idiomas, 
        # obteniendo el idioma detectado y su probabilidad.
        idioma_linea, prob_linea = Idiomas.detectar_idioma_texto(linea)

        # si langid no determina claramente, usamos hint o el idioma principal
        if idioma_linea not in ['español', 'ingles']:
            idioma_linea = idioma_hint or idioma_principal
            # si no había probabilidad válida, la dejamos en 0.0
            prob_linea = 0.0

        palabras = word_tokenize(linea) #tokeniza la línea en palabras utilizando word_tokenize de nltk, obteniendo una lista de tokens.

        # Limpiar y clasificar los tokens utilizando el método limpiar_palabras, que devuelve una lista de tuplas (token_limpio, tipo) 
        # donde tipo indica si el token es una palabra normal, un token protegido por comillas/paréntesis, o un token de puntuación.
        informacion = LimpiarTexto(palabras)

        # variable para contar la longitud del prefijo en inglés al inicio de la línea, 
        # que se utiliza para aplicar reglas especiales de clasificación de idioma en los primeros tokens de la línea.
        cantidad_prefijos = 0 

        # Si la línea es detectada como principalmente en inglés o la probabilidad de inglés es baja,
        # se aplica una regla especial para detectar un posible prefijo en inglés al inicio de la línea,
        if idioma_linea == 'ingles' or prob_linea < 0.6:

            prefijos_maximos = 4 # Se requiere un mínimo de 3 tokens consecutivos fuertes en inglés para considerar un prefijo.

            # Bucle para iterar sobre los tokens de la línea, aplicando reglas para detectar un posible prefijo en inglés al inicio de la línea,
            for token, tipo in informacion:                
                if tipo != 'palabra': # Solo se consideran tokens de tipo 'palabra' para el prefijo, se ignoran tokens de puntuación o protegidos.
                    break
                if cantidad_prefijos >= prefijos_maximos: # Si se alcanza el número máximo de tokens para el prefijo, se detiene la detección de prefijo.
                    break

                try: # Bucle try-except para manejar errores en la detección de idioma a nivel de token utilizando langid.
                    
                    # Se utiliza langid para clasificar el idioma del token, obteniendo el código de idioma y la puntuación de confianza.
                    idioma, prob = langid.classify(token) 
                    # Si el idioma detectado es inglés y la probabilidad es alta (>= 0.95), se considera que el token forma parte de un prefijo en inglés al inicio de la línea.
                    if idioma == 'en' and Idiomas.normalizacion_probabilidad(prob) >= 0.95:
                        cantidad_prefijos += 1
                        continue
                
                # Si ocurre cualquier excepción durante la detección de idioma a nivel de token, se ignora el error y se detiene la detección de prefijo, permitiendo que el procesamiento continúe con las reglas normales para el resto de la línea.
                except Exception: 
                    pass
                break

            # Requerir al menos 2 tokens consecutivos fuertes en inglés para aceptar prefijo
            if cantidad_prefijos < 3:
                cantidad_prefijos = 0

        # Bucle para procesar cada token de la línea, aplicando reglas de clasificación de idioma y
        # manejo especial para tokens protegidos por comillas o paréntesis,
        for numero, (token, tipo) in enumerate(informacion):

            # Si el tipo es de puntuacion, para marcarlo como none y sea una pausa
            if tipo == 'puntuacion':
                tokens_obtenidos.append((token, None))
                continue

            # si token está dentro del prefijo detectado, forzarlo a inglés
            if numero < cantidad_prefijos:
                tokens_obtenidos.append((token, 'ingles'))
                continue

            # tokens protegidos por comillas o paréntesis (single-token): procesado token-level unificado
            if tipo == 'palabra_protegida':
                palabras = token

                # Si hay diacríticos, preferir español inmediatamente
                if re.search(r'[ñáéíóúüÁÉÍÓÚÜ]', palabras):
                    tokens_obtenidos.append((palabras, 'español'))
                    continue

                # stopwords internas: si hay evidencia clara del idioma por stopwords forzamos el idioma del token
                # obtenemos las palabras internas para detectar stopwords
                palabras_internas = [palabra.lower() for palabra in word_tokenize(palabras)]

                #Comprobamos español
                if any(palabra in STOP_ES for palabra in palabras_internas):
                    tokens_obtenidos.append((palabras, 'español'))
                    continue

                #Comprobamos ingles
                if any(palabra in STOP_EN for palabra in palabras_internas):
                    tokens_obtenidos.append((palabras, 'ingles'))
                    continue

                # intento token-level con pista de parentesis para ajustar comportamiento
                procesado = ProcesadoDatos.procesar_palabras(
                    palabras.lower(),
                    idioma_hint=idioma_linea,
                    is_parenthesized=False,
                    prob_linea='high' if prob_linea >= 0.9 else ('med' if prob_linea >= 0.6 else 'low')
                )

                # heurística adicional para sufijos españoles (aplica especialmente para paréntesis)
                sufijos_españoles = ('ción', 'ciones', 'es', 'as', 'os', 'ante', 'mente', 'idad', 'able', 'ible', 'ista', 'aje', 'anza', 'ico', 'ica', 'ar', 'ir', 'er')
                palabras = palabras.lower() # Convertimos palabras a minusculas

                # Comprobamos si hay palabras con sufijos españoles
                tiene_sufijo_español = any(palabras.endswith(sufijo) for sufijo in sufijos_españoles)
                
                #Si procesado es None, se asigna el idioma de la línea como idioma final.
                if procesado is None: 
                    idioma_final = idioma_linea

                else: # Si procesado no es None, se toma el idioma detectado a nivel de token. 
                    idioma_final = procesado[1]

                # Si el idioma detectado a nivel de token es inglés pero la línea es principalmente en inglés y
                # el token tiene sufijos españoles, se fuerza a español para evitar errores de clasificación en casos mixtos.
                if idioma_final == 'ingles' and tiene_sufijo_español:
                    idioma_final = 'español'

                tokens_obtenidos.append((palabras, idioma_final))
                continue

            # tokens protegidos multi-palabra en comillas o paréntesis: decidir por el contexto interno
            if tipo == 'palabras_protegidas':
                texto_interno = token
                # si hay diacríticos, preferir español
                if re.search(r'[ñáéíóúüÁÉÍÓÚÜ]', texto_interno):
                    elegido = 'español'
                else:
                    # si no hay diacríticos, se detecta el idioma del texto interno utilizando el 
                    # método de detección de idioma definido en la clase Idiomas,
                    idioma_detectado, prob_detectada = Idiomas.detectar_idioma_texto(texto_interno)
                    if idioma_detectado in ('español', 'ingles') and prob_detectada >= 0.40:
                        elegido = idioma_detectado
                    else:
                        palabras = [palabra.lower() for palabra in word_tokenize(texto_interno)]
                        if any(palabra in STOP_ES for palabra in palabras):
                            elegido = 'español'
                        elif any(palabra in STOP_EN for palabra in palabras):
                            elegido = 'ingles'
                        else:
                            elegido = idioma_linea

                # tokenizar el texto interno y limpiar cada token, aplicando la misma lógica de clasificación de idioma
                # para cada token interno, pero con un hint del idioma detectado para la línea.
                tokens_internos = word_tokenize(texto_interno)
                for token_interno in tokens_internos:
                    token_limpio = re.sub(r"^[\"'\(\)\[\]\{\}]+|[\"'\(\)\[\]\{\}]+$", "", token_interno)
                    if token_limpio:
                        tokens_obtenidos.append((token_limpio, elegido))
                continue

            # Resto de tokens: política estricta context-first
            tokens_obtenidos.append((token, idioma_linea))

        return tokens_obtenidos



    # Método estático para procesar una palabra individual, aplicando reglas de detección de idioma 
    # específicas para tokens protegidos por comillas o paréntesis, con optimización mediante lru_cache.
class ProcesarPalabras(ProcesadoDatos):
    def __init__(self, logger=None):
        self.logger = logger

    @lru_cache(maxsize=4096)
    def procesar(self, palabra, idioma_hint=None, is_parenthesized=False, prob_linea='low'):

        # Manejo de casos vacíos o no string para evitar errores en la detección de idioma a nivel de palabra.
        if not palabra or not isinstance(palabra, str):
            return None
        
        # Si la palabra contiene diacríticos fuertes para español, se devuelve inmediatamente
        # como español con alta probabilidad, ya que esto es un indicador muy fuerte de que la palabra es española.
        if re.search(r'[ñáéíóúüÁÉÍÓÚÜ]', palabra):
            return (palabra, 'español', 1.0)
        
        try: # Bucle try-except para manejar errores en la detección de idioma a nivel de palabra utilizando langid.

            # Se utiliza langid para clasificar el idioma de la palabra, obteniendo el código de idioma y la puntuación de confianza.
            idioma, prob = langid.classify(palabra)
            mapping = {'es': 'español', 'en': 'ingles'}

            # Si el idioma detectado por langid está en el mapeo definido, se aplica una lógica de clasificación que tiene
            # en cuenta si el token está protegido por paréntesis
            if idioma in mapping: 
                prob = Idiomas.normalizacion_probabilidad(prob)
                
                if is_parenthesized: # Si el token esta protegido por parentesis
                    # si la probabilidad es muy alta, aceptar el idioma detectado por langid incluso para paréntesis.
                    if prob >= 0.95:
                        return (palabra, mapping[idioma], float(prob))
                    
                    # si la linea es fuertemente inglesa y la probabilidad del token es moderada, aceptar inglés
                    if prob_linea == 'high' and mapping[idioma] == 'ingles' and prob >= 0.90:
                        return (palabra, 'ingles', float(prob))
                    
                    # Si las anteriores condiciones no se cumplen, usamos el idioma de pista o forzamos el español
                    return (palabra, idioma_hint or 'español', 0.99)

                # para tokens no protegidos, requerir una probabilidad alta para aceptar el idioma detectado por langid.
                if prob >= 0.95:
                    return (palabra, mapping[idioma], float(prob))
                return None
            
        except Exception:
            self.logger.debug('langid failed for token', exc_info=True)
        return None
