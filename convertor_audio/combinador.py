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