from abc import ABC, abstractmethod

class ConversorTextoAudio(ABC):
    """
    Interfaz abstracta para conversores de producto fase2 a estructura para generador de audio.
    """
    @abstractmethod
    def convertir(self, segmentos: list[dict]) -> list[dict]:
        """
        Transforma el producto de la fase 2 en una lista de diccionarios para el generador de audio.
        
        Args:
            segmentos (list[dict]): Lista de segmentos, cada uno con tokens enriquecidos.

        Returns:
            list[dict]: Lista de dicts con campos:
                - 'token': palabra o signo de puntuación.
                - 'idioma': idioma del token o None si es silencio.
                - 'tiempo_silencio': duración en ms si es token de pausa, None si no.
                - 'linea_idx': ��ndice del segmento de origen.
        """
        pass

class ConvertidorTextoVoz(ConversorTextoAudio):
    """
    Implementación para convertir la salida del pipeline lingüístico
    en datos consumibles por el generador de audio, añadiendo el índice de línea para facilitar el debugging.
    """
    def __init__(self, logger=None):
        """
        Inicializa el convertidor.

        Args:
            logger: Logger opcional para diagnóstico.
        """
        self.logger = logger

    def convertir(self, producto_fase2):
        """
        Convierte la lista estructurada de dicts por línea (producto_fase2) en lista de dicts para audio.
        Cada dict incluye el token, idioma, tiempo de silencio y el índice de línea para trazabilidad.
        
        Args:
            producto_fase2 (list[dict]): Estructura por línea, salida de la fase 2.

        Returns:
            list[dict]: Estructura lista para el generador de audio:
                [
                    {
                        'token': str,
                        'idioma': str | None,
                        'tiempo_silencio': int | None,
                        'linea_idx': int
                    },
                    ...
                ]
        """
        tokens_audio = []
        for i, segmento in enumerate(producto_fase2):
            for token in segmento.get("tokens_idioma", []):
                palabra = token.get("token")
                idioma = token.get("idioma_token")
                tiempo = token.get("tiempo", None) if token.get("silencio", False) else None
                tokens_audio.append({
                    "token": palabra,
                    "idioma": idioma if not token.get("silencio", False) else None,
                    "tiempo_silencio": tiempo,
                    "linea_idx": i
                })
        return tokens_audio