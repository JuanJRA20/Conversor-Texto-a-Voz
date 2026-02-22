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
        self.signos_silencio = signos_silencio or \
        {'.': 600, '!': 650, '?': 650, ';': 500, ':': 500, '...': 700, ',': 300, '(': 250,       
            ')': 400, '[': 250, ']': 400, '{': 250, '}': 400, '"': 200, "'": 200, '\n': 500}

    def procesar(self, segmentos: list[dict]) -> list[dict]:
        resultado = []
        for segmento in segmentos:
            tokens_limpios = segmento['tokens_limpios']
            tokens_con_silencio = []
            for token_info in tokens_limpios:
                token = token_info['token']
                es_silencio = token in self.signos_silencio and token_info.get('es_puntuacion', True)
                tiempo_silencio = self.signos_silencio.get(token, 0) if es_silencio else 0
                # Añadir campos de silencio en cada token
                token_info_con_silencio = {**token_info, 
                                           'silencio': es_silencio, 
                                           'tiempo': tiempo_silencio}
                tokens_con_silencio.append(token_info_con_silencio)
            resultado.append({'linea': segmento['linea'], 'tokens_limpios': tokens_con_silencio})
        return resultado
    
class AgruparProtegidos(ProcesadoDatos):
    def __init__(self, logger=None):
        self.logger = logger

    def agrupar_tokens(self, tokens_limpios):
        grupos = []
        stack = []
        i = 0
        delimitadores_abre = {'(', '[', '{', '"', "'"}
        delimitadores_cierra = {')':'(', ']':'[', '}':'{', '"':'"', "'":"'"}
        while i < len(tokens_limpios):
            token = tokens_limpios[i]['token']
            token_info = tokens_limpios[i]
            if token in delimitadores_abre:
                stack.append({'abre': token, 'cierra': {'(':')', '[':']', '{':'}', '"':'"', "'":"'"}[token], 'tokens': []})
                i += 1
            elif token in delimitadores_cierra:
                if stack and token == stack[-1]['cierra']:
                    bloque = stack.pop()
                    grupo = {'tokens': bloque['tokens'], 'protegido': True,
                             'delimitador_abre': bloque['abre'], 'delimitador_cierra': bloque['cierra']}
                    if stack:
                        stack[-1]['tokens'].append(grupo)
                    else:
                        grupos.append(grupo)
                    i += 1
                else:
                    if stack:
                        stack[-1]['tokens'].append({**token_info, 'protegido': False})
                    else:
                        grupos.append({**token_info, 'protegido': False})
                    i += 1
            else:
                if stack:
                    stack[-1]['tokens'].append({**token_info, 'protegido': False})
                else:
                    grupos.append({**token_info, 'protegido': False})
                i += 1
        while stack:
            bloque = stack.pop()
            grupos.append({'tokens': bloque['tokens'], 'protegido': True,
                           'delimitador_abre': bloque['abre'], 'delimitador_cierra': bloque['cierra']})
        return grupos

    def procesar(self, segmentos: list[dict]) -> list[dict]:
        resultado = []
        for segmento in segmentos:
            tokens_limpios = segmento['tokens_limpios']
            grupos = self.agrupar_tokens(tokens_limpios)
            # Conserva estructura para cada línea
            salida = {**segmento, 'tokens_protegidos': grupos}
            resultado.append(salida)
        return resultado