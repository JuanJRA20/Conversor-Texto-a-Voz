#Importacion de las librerias necesarias:

#Librerias internas de python
from nltk.tokenize import word_tokenize, sent_tokenize
from abc import ABC, abstractmethod
#Importacion de los modulos desarrollados en el proyecto


# Segunda clase: ProcesadoDatos
class ProcesadoDatos(ABC):
    @abstractmethod
    def procesar(self, texto: str):
        pass


class ObtenerTokens(ProcesadoDatos):

    def __init__(self, logger=None):
        self.logger = logger
    # Método estático para procesar un texto completo, segmentándolo en líneas y clasificando cada token con su idioma, 
    # aplicando reglas especiales para tokens protegidos por comillas o paréntesis.
    def procesar(self, texto: str) -> list[dict]:
        """Devuelve una lista de dicts por línea/oración, con sus tokens."""
        if not isinstance(texto, str) or not texto.strip():
            return []
        texto = texto.replace('\n', ' ')
        oraciones = sent_tokenize(texto)
        resultado = []
        for oracion in oraciones:
            tokens = word_tokenize(oracion)
            resultado.append({'linea': oracion, 'tokens': tokens})
        return resultado
    
class MarcarSilencios(ProcesadoDatos):
    def __init__(self, signos_silencio=None, logger=None):
        self.logger = logger
        self.signos_silencio = signos_silencio or {'.', '!', '?', ';', ':'}

    def procesar(self, segmentos: list[dict]) -> list[dict]:
        """
        Recibe lista de dicts con formato {'linea': ..., 'tokens': [...]}, 
        y añade marca 'es_silencio' en cada token.
        """
        resultado = []
        for segmento in segmentos:
            tokens_con_silencio = []
            for token in segmento['tokens']:
                es_silencio = token in self.signos_silencio
                if self.logger:
                    self.logger.debug(
                        f"Token '{token}' marcado como {'silencio' if es_silencio else 'palabra'}")
                tokens_con_silencio.append({"token": token, "es_silencio": es_silencio})
            resultado.append({"linea": segmento["linea"], "tokens": tokens_con_silencio})
        return resultado