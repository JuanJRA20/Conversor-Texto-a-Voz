"""
En este archivo python, desarrollaremos la tercera etapa del proyecto,
que consiste en la conversión del texto procesado a audio.

Haremos uso de las librerias gTTS y pyttsx3 para la conversión de texto a voz,
pydub para la manipulación y combinación de archivos de audio, os para gestion de archivos temporales
y uuid para generar nombres de archivos temporales únicos.

El archivo constara de una clase principal con 6 métodos estáticos:
- convertir_texto_voz: Convierte el texto procesado a voz, manteniendo el orden original.
- generaraudio_gtts: Genera un archivo de audio para un bloque de palabras en un idioma específico.
- generaraudio_pytts: Genera un archivo de audio utilizando pyttsx3 como respaldo.
- generaraudio: Genera un archivo de audio utilizando gTTS y si falla, usa pyttsx3 como respaldo.
- nombre_archivo_temporal: Genera un nombre de archivo temporal único para cada bloque de palabras.
- combinaraudios: Combina múltiples archivos de audio en un solo archivo final.
"""

# Importar las librerias necesarias:

# Librerias internas de python:
import os
import uuid

# Librerias de terceros:
from gtts import gTTS
import pyttsx3
from pydub import AudioSegment
from tqdm import tqdm

#Importacion del logger personalizado
from Logger import Telemetriaindustrial

#Configurar el logger
logger = Telemetriaindustrial("Convertir_Texto_Audio").logger

# Idioma por defecto cuando no se detecta uno
idioma_defecto = 'español'

#Clase para la conversión de texto a voz
class ConvertidorTextoVoz:

    @staticmethod #Función estática para convertir texto a voz
    def convertir_texto_voz(texto_idioma, nombre_salida="resultado.mp3", mostrar_progreso=True):
        
        #Validamos que la entrada sea una lista de tuplas (palabra, idioma)
        if not isinstance(texto_idioma, list) or not all(isinstance(token, tuple) and len(token) == 2 for token in texto_idioma):
            logger.warning("Entrada no válida: se esperaba lista de tuplas (palabra, idioma).")
            return None # Retornar None si la entrada no es válida
        
        #Lista para almacenar los segmentos de audio en memoria o rutas temporales
        archivos_temporales = []

        #Variables para agrupar palabras por idioma
        bloque_palabras_actuales = [] #lista de palabras del mismo idioma
        idioma_actual = idioma_defecto #idioma actual del bloque

        progreso = None
        if mostrar_progreso:
            progreso = tqdm(total=len(texto_idioma), desc="Convirtiendo texto a audio", unit="token")

        try:
            #Iterar sobre las palabras y sus idiomas. Si idioma es None -> marcador de pausa.
            for palabra, idioma in texto_idioma:
                if progreso:
                    progreso.update(1)

                # si no hay idioma, mantener el idioma_actual (o usar defecto)
                if idioma is None:
                    # Este token es un marcador de pausa. Si tenemos un bloque de palabras acumulado, generamos su audio antes de procesar la pausa.
                    if bloque_palabras_actuales:
                        archivo = ConvertidorTextoVoz.generaraudio(bloque_palabras_actuales, idioma_actual)

                        if archivo:
                            if isinstance(archivo, tuple): #si el resultado es una tupla (segmento, motor), extraemos el segmento
                                seg, motor = archivo
                            else: #si el resultado es directamente un segmento, lo usamos tal cual
                                seg, motor = archivo, None

                            archivos_temporales.append(seg)

                        bloque_palabras_actuales = []

                    # mapear signos de puntuación a duración de silencio (ms)
                    duracion_silencio = {'.': 900, ',': 230, ';': 400, ':': 400, "(": 400, ")": 400, "\n": 800}
                    duracion = 0
                    # elegir la duración más larga si el token tiene repetidos (eg '...')
                    for caracter in palabra:
                        duracion = max(duracion, duracion_silencio.get(caracter, 0))

                    if duracion > 0: # Si se detectó un marcador de pausa válido, generar un segmento de silencio y añadirlo a la lista de segmentos
                        try:
                            # crear silencio en memoria y añadirlo a la lista de segmentos
                            silencio = AudioSegment.silent(duration=duracion)
                            # si el último elemento ya es silencio, fusionar tomando la duración máxima
                            if archivos_temporales and isinstance(archivos_temporales[-1], AudioSegment):
                                try: # Si el último segmento es silencio puro (rms == 0), fusionar tomando la duración máxima para evitar fragmentación excesiva
                                    ultimo = archivos_temporales[-1]

                                    if ultimo.rms == 0:
                                        unir_duracion = max(len(ultimo), len(silencio))
                                        archivos_temporales[-1] = AudioSegment.silent(duration=unir_duracion)

                                    else: # Si el último segmento no es silencio puro, añadir el nuevo silencio sin fusionar para evitar perder fonemas finales
                                        archivos_temporales.append(silencio)

                                except Exception: # En caso de error al analizar el segmento anterior, añadir el nuevo silencio sin fusionar para evitar perder fonemas finales
                                    archivos_temporales.append(silencio)

                            else: # Si el último elemento no es silencio o no hay elementos, añadir el nuevo silencio directamente
                                archivos_temporales.append(silencio)

                        except Exception as e:
                            logger.error(f"Error generando silencio en memoria: {e}")
                    continue

                # Si el bloque está vacío y el idioma difiere del idioma actual por defecto,
                # inicializamos `idioma_actual` al idioma del primer token para evitar
                # producir la primera palabra con el idioma por defecto incorrecto.
                if idioma is not None and not bloque_palabras_actuales and idioma != idioma_actual:
                    idioma_actual = idioma

                # Si el idioma cambia respecto al bloque actual y ya tenemos palabras, cerrar bloque y generar audio
                if idioma != idioma_actual and bloque_palabras_actuales:
                    archivo = ConvertidorTextoVoz.generaraudio(bloque_palabras_actuales, idioma_actual)

                    if archivo: #si se generó el segmento correctamente, lo agregamos a la lista de segmentos temporales
                        if isinstance(archivo, tuple):
                            seg, motor = archivo
                        else: #si el resultado es directamente un segmento, lo usamos tal cual
                            seg, motor = archivo, None

                        archivos_temporales.append(seg)
                    
                    # Reiniciar el bloque de palabras para el nuevo idioma
                    bloque_palabras_actuales = []
                    idioma_actual = idioma

                bloque_palabras_actuales.append(palabra) # Agregar la palabra al bloque actual
        finally:
            if progreso:
                progreso.close()

        #Si al terminar el bucle quedan palabras en el bloque actual, generamos su audio
        if bloque_palabras_actuales:
            resultado_audio = ConvertidorTextoVoz.generaraudio(bloque_palabras_actuales, idioma_actual)
            #si el segmento se generó correctamente, lo agregamos a la lista
            if resultado_audio:
                if isinstance(resultado_audio, tuple):
                    seg, motor = resultado_audio
                else:
                    seg, motor = resultado_audio, None
                archivos_temporales.append(seg)
        
        # Asegurar que el nombre de salida termina en .mp3
        if not nombre_salida.lower().endswith('.mp3'):
            nombre_salida = nombre_salida + '.mp3'

        #Combinar todos los archivos temporales en un solo archivo final usando el metodo combinaraudios
        archivo_final = ConvertidorTextoVoz.combinaraudios(archivos_temporales, nombre_salida)

        # Si no se generó ningún archivo temporal, crear un MP3 silencioso válido
        if not archivo_final:
            try:
                silent = AudioSegment.silent(duration=500)
                silent.export(nombre_salida, format='mp3')
                logger.warning(f"No se generaron archivos temporales; creando MP3 silencioso: {nombre_salida}")
                return nombre_salida
            except Exception as e:
                logger.error(f"Error al crear MP3 silencioso: {e}")
                return None

        logger.info(f"Archivo de audio final generado: {archivo_final}")

        return archivo_final #Retornar el archivo de audio final generado
    
    #Metodo para generar un nombre de archivo temporal unico usando uuid y el idioma para facilitar el diagnóstico
    @staticmethod
    def nombre_archivo_temporal(palabras, idioma):
        return f"audio_temp_{uuid.uuid4().hex}_{idioma}.mp3"

    #Metodo para generar audio usando gTTS
    @staticmethod
    def generaraudio_gtts(palabras, idioma):

        try: #bloque try-except para capturar errores inesperados

            # funcion para Expandir tokens con símbolos para mejor pronunciación
            def expand_token(tok):
                if '+' in tok:
                    # convertir C++ -> C plus plus, C# -> C sharp
                    t = tok.replace('++', ' plus plus').replace('+', ' plus')
                    return t
                if '#' in tok:
                    return tok.replace('#', ' sharp')
                return tok

            # Expandir tokens con símbolos para mejorar la pronunciación en gTTS
            texto = " ".join(expand_token(p) for p in palabras) # Unir las palabras en un solo texto
            codigo_idioma = {"español": "es", "ingles": "en"}.get(idioma, None)  # Mapear el idioma al código de gTTS
            logger.debug(f"generaraudio_gtts: idioma={idioma} -> codigo={codigo_idioma} tokens={len(palabras)}")

            #Si el idioma no es soportado por gTTS
            if codigo_idioma is None:
                logger.warning(f"Idioma no soportado por gTTS: {idioma}")
                return None # Retornar None si el idioma no es soportado
            
            #En caso de idioma soportado, generar el audio
            tts = gTTS(text=texto, lang=codigo_idioma) # Crear el objeto gTTS
            nombre_archivo = ConvertidorTextoVoz.nombre_archivo_temporal(palabras, idioma) # Generar nombre de archivo temporal
            tts.save(nombre_archivo) # Guardar el archivo de audio

            # cargar en memoria y eliminar el archivo temporal
            seg = AudioSegment.from_file(nombre_archivo)

            try: # Intentar eliminar el archivo temporal, pero si falla (eg bloqueo por antivirus), no interrumpir el proceso
                os.remove(nombre_archivo)
            except Exception:
                pass
            return seg

        except Exception as e: #En caso de error en gTTS retornamos None
            logger.error(f"Error al generar audio con gTTS para el idioma {idioma}: {str(e)}")
            return None 

    #Metodo para generar audio usando pyttsx3 
    @staticmethod
    def generaraudio_pytts(palabras, idioma, velocidad=150, volumen=1.0):

        try: #bloque try-except para capturar errores inesperados

            texto = " ".join(palabras) # Unir las palabras en un solo texto
            engine = pyttsx3.init() # Inicializar el motor pyttsx3
            engine.say(texto) # Agregar el texto al motor
            logger.debug(f"generaraudio_pytts: idioma_hint={idioma} tokens={len(palabras)}")

            engine.setProperty('rate', velocidad) # Configurar la velocidad de habla
            engine.setProperty('volume', volumen) # Configurar el volumen de habla
            nombre_archivo = ConvertidorTextoVoz.nombre_archivo_temporal(palabras, idioma) # Generar nombre de archivo temporal

            engine.save_to_file(texto, nombre_archivo) # Guardar el archivo de audio
            engine.runAndWait() # Ejecutar el motor para generar el audio
            seg = AudioSegment.from_file(nombre_archivo)
            try:
                os.remove(nombre_archivo)
            except Exception:
                pass
            return seg
        
        except Exception as e: #En caso de error en pyttsx3 retornamos None
            logger.error(f"Error al generar audio con pyttsx3 para el idioma {idioma}: {str(e)}")
            return None
        
    #Metodo para generar audio, usando gTTS y pyttsx3 como respaldo
    @staticmethod
    def generaraudio(palabras, idioma):

        # Intentar generar el audio con gTTS primero
        audio_seg = None
        motor = None

        try:
            audio_seg = ConvertidorTextoVoz.generaraudio_gtts(palabras, idioma)
            if audio_seg is not None:
                motor = 'gTTS'
        except Exception:
            audio_seg = None
            motor = None

        # Si gTTS falla o devuelve None, intentar con pyttsx3
        if audio_seg is None:
            try:
                logger.warning(f"Intentando generar con motor pyttsx3, gTTS falló para {idioma}.")
                audio_seg = ConvertidorTextoVoz.generaraudio_pytts(palabras, idioma)
                if audio_seg is not None:
                    motor = 'pyttsx3'
            except Exception:
                audio_seg = None
                motor = None

        # Si ambos motores fallan, retornar None
        if audio_seg is None:
            logger.error(f"No se pudo generar el audio para el idioma {idioma} con ninguno de los motores.")
            return None

        # Devolver el segmento y el motor usado para diagnóstico
        return (audio_seg, motor)

    
    #Metodo para combinar múltiples archivos de audio en uno solo
    @staticmethod
    def combinaraudios(archivos, nombre_salida):

        try: #bloque try-except para capturar errores inesperados

            if not archivos:
                logger.warning("No hay archivos para combinar.")
                return None
            
            audio_combinado = AudioSegment.empty() # Crear un segmento de audio vacío

            #Iterar sobre los archivos y combinarlos (detectando el formato automáticamente)
            for item in archivos:
                segmento = None
                # Si ya es un AudioSegment en memoria, usarlo directamente
                if isinstance(item, AudioSegment):
                    segmento = item

                elif isinstance(item, str): # Si es una ruta de archivo, intentar cargarlo como audio

                    if not os.path.exists(item): # Si el archivo no existe, registrar una advertencia y continuar con el siguiente para evitar interrumpir todo el proceso
                        logger.warning(f"Archivo no encontrado para combinar: {item}")
                        continue

                    try: # Intentar cargar el archivo de audio, detectando el formato automáticamente
                        segmento = AudioSegment.from_file(item)
                    except Exception as e:
                        logger.warning(f"No se pudo leer archivo {item}: {e}")
                        continue
                else:
                    logger.warning(f"Elemento de entrada no válido en combinaraudios: {type(item)}")
                    continue

                # Si el segmento es silencio puro (rms == 0)
                try: 
                    es_silencio = (segmento.rms == 0)
                except Exception:
                    es_silencio = False                

                # si la combinacion esta vacia, iniciar con el primer segmento
                if len(audio_combinado) == 0:
                    audio_combinado = segmento

                else: # Si ya hay audio combinado, añadir el nuevo segmento
                    try:
                        # Evitar crossfade para segmentos cortos (puede eliminar consonantes iniciales)
                        if es_silencio:
                            audio_combinado += segmento

                        else: # Para segmentos de habla, usar crossfade si ambos segmentos son suficientemente
                                # largos para evitar fragmentación excesiva
                            if len(audio_combinado) > 800 and len(segmento) > 800:
                                audio_combinado = audio_combinado.append(segmento, crossfade=10)

                            else: # Para segmentos cortos, evitar crossfade para no perder fonemas finales
                                # insertar pequeño padding entre bloques de habla para evitar pérdida
                                try:
                                    cola = audio_combinado[-50:] if len(audio_combinado) > 50 else audio_combinado
                                    silencio_cola = (cola.rms == 0)
                                except Exception:
                                    silencio_cola = False
                                if not silencio_cola:
                                    audio_combinado += AudioSegment.silent(duration=40)
                                audio_combinado += segmento
                    except Exception:
                        audio_combinado += segmento
            
            
            audio_combinado.export(nombre_salida, format="mp3") # Exportar el audio combinado a un archivo mp3

            # Intentar eliminar sólo los elementos que sean rutas de archivo
            for item in archivos:
                if isinstance(item, str) and os.path.exists(item):
                    try:
                        os.remove(item)
                    except Exception:
                        pass

            # Registrar información sobre la combinación exitosa y retornar el archivo final con su nombre
            logger.info(f"Archivos combinados en: {nombre_salida}")
            return nombre_salida

        except Exception as e: #En caso de error al combinar los audios retornamos None
            logger.error(f"Error al combinar audios: {str(e)}")
            return None