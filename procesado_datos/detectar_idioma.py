#Importacion de las librerias necesarias:
from functools import lru_cache
from typing import Tuple, Optional
import langid
from abc import ABC, abstractmethod


# Configuración de langid para limitar a español e inglés, mejorando precisión en textos mixtos.
langid.set_languages(['es', 'en'])

DIACRITICOS_ESPANOL = frozenset('ñáéíóúüÁÉÍÓÚÜ¿¡')
MAPEO_IDIOMAS = {'es': 'español', 'en': 'ingles'}

class IDetectarIdiomas(ABC):
    @abstractmethod
    def detectar_idioma(self, texto: str) -> Tuple[Optional[str], float]:
        """
        Detecta el idioma de un texto.
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Tuple[Optional[str], float]: (idioma, confianza)
        """
        pass
    
class DetectarIdioma(IDetectarIdiomas):

    IDIOMA_PRINCIPAL = 'español'

    def __init__(self, logger=None):
        self.logger = logger 

    # Método estático para detectar el idioma de un texto, utilizando heurísticas de diacríticos y langid, con manejo de excepciones.
    @staticmethod
    @lru_cache(maxsize=128)
    def detectar_idioma_langid(texto: str) -> Tuple[Optional[str], float]:
        try: # Bucle try-except para manejar errores en la detección de idioma con langid, registrando cualquier excepción en el logger para diagnóstico.
            codigo_idioma, probabilidad = langid.classify(texto) # Utiliza langid para clasificar el idioma del texto, obteniendo el código de idioma y la puntuación de confianza.
            if codigo_idioma in MAPEO_IDIOMAS:
                idioma = MAPEO_IDIOMAS[codigo_idioma]
                probabilidad_normalizada = DetectarIdioma.normalizacion_probabilidad(probabilidad) # Normaliza la puntuación de langid a una escala de probabilidad más interpretable utilizando el método definido anteriormente.
                return idioma, probabilidad_normalizada
            else:
                return None, 0.0
                
        except Exception as e:
            return None, 0.0
        
    def detectar_idioma(self, texto: str) -> Tuple[Optional[str], float]:

        # Manejo de casos vacíos o no string para evitar errores en la detección de idioma.
        if not texto or not texto.strip():
            return None, 0.0
        
        # Diacríticos fuertes para español
        if self._contiene_diacriticos_espanol(texto):
            if self.logger:
                self.logger.debug("Idioma detectado por diacríticos: español")
            return 'español', 1.0
        
        return self.detectar_idioma_langid(texto)
        
    @staticmethod
    def _contiene_diacriticos_espanol(texto: str) -> bool:
        """
        Verifica si el texto contiene diacríticos característicos del español.
        
        Args:
            texto: Texto a verificar
            
        Returns:
            bool: True si contiene diacríticos españoles
        """
        return any(char in DIACRITICOS_ESPANOL for char in texto)
    
    # Método estático para normalizar la puntuación de langid a una escala de probabilidad más interpretable.
    @staticmethod
    def normalizacion_probabilidad(probabilidad_base: float) -> float:
        try:
            prob = float(probabilidad_base)
        except (ValueError, TypeError):
            return 0.5
        
        # Mapeo basado en experiencia empírica con langid
        if prob >= 3.0:
            return 0.99
        elif prob >= 1.0:
            return 0.90
        elif prob > 0.0:
            return 0.80
        elif prob > -1.5:
            return 0.70
        elif prob > -3.0:
            return 0.60
        else:
            return 0.50

class GestorDetectorIdioma:
    """
    Gestor Facade para simplificar la detección de idioma.
    """
    def __init__(self, logger=None):
        """
        Inicializa el gestor.
        Args:logger: Logger opcional
        """
        self.logger = logger
        self.detector = DetectarIdioma(logger=logger)

    def detectar(self, texto: str) -> Tuple[Optional[str], float]:
        """
        Detecta el idioma del texto.
        Args: texto: Texto a analizar
        Returns: Tuple[Optional[str], float]: (idioma, confianza)
        """

        return self.detector.detectar_idioma(texto)
    
    def es_espanol(self, texto: str, umbral: float = 0.7) -> bool:
        """
        Verifica si el texto es español con confianza mínima.
        Args:
            texto: Texto a verificar
            umbral: Confianza mínima requerida (0-1) 
        Returns: bool: True si es español con confianza >= umbral
        """

        idioma, confianza = self.detector.detectar_idioma(texto)
        return idioma == 'español' and confianza >= umbral
    
    def es_ingles(self, texto: str, umbral: float = 0.7) -> bool:
        """
        Verifica si el texto es inglés con confianza mínima.
        Args:
            texto: Texto a verificar
            umbral: Confianza mínima requerida (0-1) 
        Returns: bool: True si es inglés con confianza >= umbral
        """

        idioma, confianza = self.detector.detectar_idioma(texto)
        return idioma == 'ingles' and confianza >= umbral