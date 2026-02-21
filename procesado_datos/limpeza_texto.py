import re
from abc import ABC, abstractmethod
from typing import List, Dict
from functools import lru_cache

class LimpiezaTexto(ABC):
    @abstractmethod
    def limpiar(self, tokens: List[str]) -> List[Dict]:
        """Limpia una lista de tokens y los clasifica"""
        pass

class LimpiarPalabras(LimpiezaTexto):
    def __init__(self, logger=None):
        self.logger = logger


    def limpiar(self, segmentos: list[dict]) -> list[dict]:
        resultado = []
        for segmento in segmentos:
            tokens = segmento['tokens']
            tokens_limpios = []
            for token in tokens:
                token_info = self.limpiar_token(token)
                if self.logger:
                    self.logger.debug(
                        f"Token '{token}' - limpio: '{token_info['token']}', palabra: {token_info['es_palabra']}, protegido: {token_info['protegido']}, puntuación: {token_info['es_puntuacion']}"
                    )
                tokens_limpios.append(token_info)
            resultado.append({'linea': segmento['linea'], 'tokens_limpios': tokens_limpios})
        return resultado
    
    @staticmethod
    @lru_cache(maxsize=4096)
    def limpiar_token(token: str) -> dict:
        token_limpio = token.strip().lower()
        patron_palabra = re.compile(r"^[A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ_\+'\#\-]+$")
        patron_protegida = re.compile(r"^[\"'‘“(\[].*[\"'’”)\]]$")
        patron_puntuacion = re.compile(r"^[.,:;!?\-]+$")
        protegido = bool(patron_protegida.match(token))
        es_palabra = bool(patron_palabra.match(token)) and not protegido and not patron_puntuacion.match(token)
        es_puntuacion = bool(patron_puntuacion.match(token))
        return {
            'token': token_limpio,
            'es_palabra': es_palabra,
            'protegido': protegido,
            'es_puntuacion': es_puntuacion
        }