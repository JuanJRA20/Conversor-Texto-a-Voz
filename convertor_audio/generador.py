from abc import ABC, abstractmethod
from gtts import gTTS
import pyttsx3
from pydub import AudioSegment
import re

class IGenerador(ABC):
    @abstractmethod
    def generar(self, bloques_tokens, nombrador) -> list:
        """
        Genera fragmentos de audio a partir de los bloques de tokens.
        Args:
            bloques_tokens (list[dict]): Cada dict contiene ya el texto expandido y tiempo de silencio.
            nombrador: Objeto o función para generar nombres únicos de archivos temporales.
        Returns:
            list: Lista de AudioSegment (fragmentos y silencios).
        """
        pass

class Generador(IGenerador, ABC):
    """
    Clase base abstracta para generación de audio por bloques y silencios.
    Procesa los tokens, separa fragmentos de voz y pausas, y delega a subclases
    la creación de cada fragmento concreto.
    """
    def __init__(self, logger=None):
        self.logger = logger

    def generar(self, bloques_tokens, nombrador):
        bloque_palabras = []
        idioma_actual = None

        for token_data in bloques_tokens:
            token = token_data['token']
            idioma = token_data['idioma']
            tiempo_silencio = token_data.get('tiempo_silencio')
            # Silencio / pausa
            if idioma is None and tiempo_silencio:
                if bloque_palabras:
                    audio, nombre = self._generar_fragmento_audio(bloque_palabras, idioma_actual, nombrador)
                    if audio:
                        yield (audio, nombre)
                    bloque_palabras = []
                yield (AudioSegment.silent(duration=tiempo_silencio), f"silencio_{tiempo_silencio}ms")
            else:
                if idioma_actual and idioma != idioma_actual and bloque_palabras:
                    audio, nombre = self._generar_fragmento_audio(bloque_palabras, idioma_actual, nombrador)
                    if audio:
                        yield (audio, nombre)
                    bloque_palabras = []
                bloque_palabras.append(token)
                idioma_actual = idioma

        # Último bloque
        if bloque_palabras:
            audio, nombre = self._generar_fragmento_audio(bloque_palabras, idioma_actual, nombrador)
            if audio:
                yield (audio, nombre)

    @abstractmethod
    def _generar_fragmento_audio(self, palabras, idioma, nombrador):
        """
        Genera un fragmento de audio para un bloque de palabras con el motor concreto.
        Args:
            palabras (list[str]): Palabras (ya expandidas) del bloque.
            idioma (str): Idioma asociado.
            nombrador: Objeto para generar filename temporal.
        Returns:
            tuple: (AudioSegment, str) o (None, None) si falla.
        """
        pass

class GTTS(Generador):
    """
    Generador de fragmentos de audio usando Google Text-to-Speech (gTTS).
    Convierte bloques de texto y pausas en segmentos de audio,
    asignando nombres únicos a cada archivo temporal mediante el nombrador.
    """
    def __init__(self, logger=None):
        super().__init__(logger)

    def _generar_fragmento_audio(self, palabras, idioma, nombrador):
        codigo_idioma = {"español": "es", "ingles": "en"}.get(idioma, None)
        if not codigo_idioma:
            if self.logger:
                self.logger.warning(f"Idioma no soportado por gTTS: {idioma}")
            return None, None
        texto = " ".join(palabras)
        texto = " ".join(palabras)
        texto = re.sub(r'["\']', '', texto)
        try:
            tts = gTTS(text=texto, lang=codigo_idioma)
            nombre_archivo = nombrador.generar_nombre(palabras, idioma)
            tts.save(nombre_archivo)
            seg = AudioSegment.from_file(nombre_archivo)
            return seg, nombre_archivo
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al generar audio gTTS: {e}")
            return None, None

class Pyttsx3(Generador):
    """
    Generador de fragmentos de audio usando pyttsx3.
    Convierte bloques de texto y pausas en segmentos de audio,
    asignando nombres únicos a cada archivo temporal mediante el nombrador.
    """
    def __init__(self, logger=None):
        super().__init__(logger)

    def _generar_fragmento_audio(self, palabras, idioma, nombrador):
        texto = " ".join(palabras)
        texto = " ".join(palabras)
        texto = re.sub(r'["\']', '', texto)
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1.0)
            engine.say(texto)
            nombre_archivo = nombrador.generar_nombre(palabras, idioma)
            engine.save_to_file(texto, nombre_archivo)
            engine.runAndWait()
            seg = AudioSegment.from_file(nombre_archivo)
            return seg, nombre_archivo
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al generar audio pyttsx3: {e}")
            return None, None