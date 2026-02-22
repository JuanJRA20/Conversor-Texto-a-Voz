#Importacion de las librerias necesarias:
from functools import lru_cache
from typing import Tuple, Optional
import langid
from abc import ABC, abstractmethod
from nltk.corpus import stopwords
import nltk

try:
    español_stopwords = frozenset(stopwords.words('spanish'))
except LookupError:
    nltk.download('stopwords', quiet=True)
    español_stopwords = frozenset(stopwords.words('spanish'))
try:
    ingles_stopwords = frozenset(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords', quiet=True)
    ingles_stopwords = frozenset(stopwords.words('english'))

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
        
        tokens = texto.strip().split()

        if len(tokens) == 1:
            # Sólo para palabra suelta: usar heurística de stopwords
            token_lower = tokens[0].lower()
            if token_lower in español_stopwords:
                if self.logger:
                    self.logger.debug(f"Token '{token_lower}' es stopword española")
                return 'español', 1.0
        
            elif token_lower in ingles_stopwords:
                if self.logger:
                    self.logger.debug(f"Token '{token_lower}' es stopword inglesa")
                return 'ingles', 1.0
        
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
        
    def detectar_segmentos(self, segmentos: list[dict]) -> list[dict]:
        """
        Recibe lista de segmentos con tokens limpios, 
        devuelve cada línea con idioma detectado y tokens enriquecidos con idioma por token.
        """
        resultado = []
        for segmento in segmentos:
            linea = segmento["linea"]
            idioma_linea, conf_linea = self.detectar_idioma(linea)
            tokens_protegidos = segmento.get("tokens_protegidos", [])
            tokens_resultado = []
            for item in tokens_protegidos:
                tokens_resultado.extend(self._procesar_bloque(item, idioma_linea, conf_linea))
            resultado.append({
                "linea": linea,
                "idioma_linea": idioma_linea,
                "conf_linea": conf_linea,
                "tokens_idioma": tokens_resultado
            })
        return resultado

    def detectar_idioma_token(
        self,
        token: str,
        es_palabra: bool,
        es_puntuacion: bool,
        protegido: bool,
        silencio: Optional[bool],
        tiempo_silencio: Optional[int],
        idioma_linea: Optional[str],
        conf_linea: float
    ) -> Tuple[Optional[str], float]:
        """
        Detecta idioma de un token, usando heurísticas y hint de línea.
        """
        token_lower = token.lower()
        # Check puntuación: no idioma, return None
        if es_puntuacion or silencio:
            return None, 0.0
        # Protegidos: confiar en idioma de línea si confianza alta
        if protegido or not es_palabra or len(token) < 2:
            if idioma_linea and conf_linea >= 0.7:
                return idioma_linea, conf_linea
            else:
                return self.detectar_idioma_langid(token)
        # Diacríticos
        if self._contiene_diacriticos_espanol(token):
            return "español", 1.0
        # Stopword (en contexto palabra suelta)
        if len(token) == 1:
        # Solo para palabra suelta: usar heurística de stopwords
            if token_lower in español_stopwords:
                if self.logger:
                    self.logger.debug(f"Token '{token_lower}' es stopword española")
                return 'español', 1.0
            elif token_lower in ingles_stopwords:
                if self.logger:
                    self.logger.debug(f"Token '{token_lower}' es stopword inglesa")
                return 'ingles', 1.0
        # Por defecto: langid, con fallback a línea si confianza baja
        idioma, conf = self.detectar_idioma_langid(token)
        if conf < 0.7 and idioma_linea is not None and conf_linea >= 0.7:
            return idioma_linea, conf_linea
        else:
            return idioma, conf
        
    def _procesar_bloque(self, bloque, idioma_linea, conf_linea):
        resultado = []
        if isinstance(bloque, dict) and 'tokens' in bloque and bloque.get('protegido', False):
            # Es un bloque protegido
            texto_bloque = ' '.join(token['token'] for token in bloque['tokens'])
            # Detecta idioma del bloque completo
            idioma_bloque, conf_bloque = self.detectar_idioma(texto_bloque)
            # Si es una sola palabra, lógica de token suelto
            if len(bloque['tokens']) == 1 and bloque['tokens'][0]['es_palabra']:
                idioma_token, conf_token = self.detectar_idioma_token(
                    bloque['tokens'][0]['token'],
                    es_palabra=bloque['tokens'][0]['es_palabra'],
                    es_puntuacion=bloque['tokens'][0]['es_puntuacion'],
                    protegido=True,
                    es_silencio=bloque['tokens'][0].get('es_silencio', False),
                    tiempo_silencio=bloque['tokens'][0].get('tiempo_silencio', 0),
                    idioma_linea=idioma_linea,
                    conf_linea=conf_linea
                )
                bloque['tokens'][0]['idioma_token'] = idioma_token
                bloque['tokens'][0]['conf_token'] = conf_token
                resultado.append(bloque['tokens'][0])
            else:
                # Es frase: asigna idioma del bloque a cada token interno
                for token in bloque['tokens']:
                    idioma_token = idioma_bloque
                    conf_token = conf_bloque
                    token['idioma_token'] = idioma_token
                    token['conf_token'] = conf_token
                    resultado.append(token)
        elif isinstance(bloque, dict) and 'token' in bloque:
            # Token simple
            idioma_token, conf_token = self.detectar_idioma_token(
                bloque['token'],
                es_palabra=bloque['es_palabra'],
                es_puntuacion=bloque['es_puntuacion'],
                protegido=False,
                es_silencio=bloque.get('es_silencio', False),
                tiempo_silencio=bloque.get('tiempo_silencio', 0),
                idioma_linea=idioma_linea,
                conf_linea=conf_linea
            )
            bloque['idioma_token'] = idioma_token
            bloque['conf_token'] = conf_token
            resultado.append(bloque)
        return resultado
    
class GestorDetectorIdioma:
    """
    Gestor Facade para simplificar la detección de idioma.
    """
    def __init__(self, logger=None):
        """
        Inicializa el gestor.
        Args:
            logger: Logger opcional
        """
        self.logger = logger
        self.detector = DetectarIdioma(logger = logger)

    def detectar(self, texto: str) -> Tuple[Optional[str], float]:
        """
        Detecta el idioma del texto.
        Args: texto: Texto a analizar
        Returns: Tuple[Optional[str], float]: (idioma, confianza)
        """

        return self.detector.detectar_segmentos(texto)
    
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