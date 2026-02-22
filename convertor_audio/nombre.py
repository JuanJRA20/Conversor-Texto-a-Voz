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

@staticmethod
def nombre_archivo_temporal(palabras, idioma):
    return f"audio_temp_{uuid.uuid4().hex}_{idioma}.mp3"
