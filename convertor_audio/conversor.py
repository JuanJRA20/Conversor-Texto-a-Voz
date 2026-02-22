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
    