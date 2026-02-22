import uuid
from abc import ABC, abstractmethod
import hashlib

class INombrador(ABC):
    """
    Interfaz para generar nombres únicos de archivos temporales de audio.
    Permite implementar distintas estrategias de nombrado según el contexto o motor.
    """
    @abstractmethod
    def generar_nombre(self, palabras, idioma) -> str:
        """
        Genera un nombre único para un fragmento de audio basado en las palabras e idioma.
        Args:
            palabras (list[str]): Palabras del bloque de texto.
            idioma (str): Idioma asociado al bloque.
        Returns:
            str: Nombre único para el archivo temporal de audio.
        """
        pass

class NombreTemporal(INombrador):
    def __init__(self, logger=None):
        self.logger = logger
    
    def generar_nombre(self, palabras, idioma) -> str:
        hash_palabras = hashlib.md5(" ".join(palabras).encode()).hexdigest()[:6]
        nombre = f"audio_{uuid.uuid4().hex[:8]}_{idioma}_{hash_palabras}.mp3"
        if self.logger:
            self.logger.debug(f"Archivo generado: {nombre} para idioma: {idioma} | palabras: {palabras[:3]}")
        return nombre
