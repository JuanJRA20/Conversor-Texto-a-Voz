import os
import uuid

# Librerias de terceros:
from gtts import gTTS
import pyttsx3
from pydub import AudioSegment
from tqdm import tqdm
from abc import ABC, abstractmethod
#Importacion del logger
#  personalizado
from Logger import Telemetriaindustrial

#Configurar el logger
logger = Telemetriaindustrial("Convertir_Texto_Audio").logger

class IGenerador(ABC):
    @abstractmethod
    def generar(self):
        pass


#Metodo para generar audio usando gTTS

class generaraudio_gtts(IGenerador):

    def __init__(self, logger, palabras, idioma):
        self.palabras = palabras
        self.idioma = idioma
        self.logger = logger

    def generar(self, logger=logger):
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


class generaraudio_pytts(IGenerador):

    def __init__(self, logger, palabras, idioma):
        self.palabras = palabras
        self.idioma = idioma
        self.logger = logger

    def generar(self, logger=logger):

        texto = " ".join(self.palabras) # Unir las palabras en un solo texto
        engine = pyttsx3.init() # Inicializar el motor pyttsx3
        engine.say(texto) # Agregar el texto al motor
        logger.debug(f"generaraudio_pytts: idioma_hint={self.idioma} tokens={len(self.palabras)}")

        engine.setProperty('rate', velocidad) # Configurar la velocidad de habla
        engine.setProperty('volume', volumen) # Configurar el volumen de habla
        nombre_archivo = ConvertidorTextoVoz.nombre_archivo_temporal(self.palabras, self.idioma) # Generar nombre de archivo temporal

        engine.save_to_file(texto, nombre_archivo) # Guardar el archivo de audio
        engine.runAndWait() # Ejecutar el motor para generar el audio
        seg = AudioSegment.from_file(nombre_archivo)
        try:
            os.remove(nombre_archivo)
        except Exception:
            pass
        return seg

        
#Metodo para generar audio, usando gTTS y pyttsx3 como respaldo

class GestionadorAudio:

    def __init__(self, palabras, idioma):
        self.palabras = palabras
        self.idioma = idioma
        self.audio_seg = None
        self.motor = None

    def generar(self, logger=logger):
        try:
            audio_seg = ConvertidorTextoVoz.generaraudio_gtts(self.palabras, self.idioma)
            if audio_seg is not None:
                self.motor = 'gTTS'
        except Exception:
            audio_seg = None
            self.motor = None

        # Si gTTS falla o devuelve None, intentar con pyttsx3
        if audio_seg is None:
            try:
                logger.warning(f"Intentando generar con motor pyttsx3, gTTS falló para {self.idioma}.")
                audio_seg = ConvertidorTextoVoz.generaraudio_pytts(self.palabras, self.idioma)
                if audio_seg is not None:
                    self.motor = 'pyttsx3'
            except Exception:
                audio_seg = None
                self.motor = None

        # Si ambos motores fallan, retornar None
        if audio_seg is None:
            logger.error(f"No se pudo generar el audio para el idioma {self.idioma} con ninguno de los motores.")
            return None

        # Devolver el segmento y el motor usado para diagnóstico
        return (audio_seg, self.motor)