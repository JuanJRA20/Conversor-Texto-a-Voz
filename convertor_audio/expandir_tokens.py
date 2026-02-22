from abc import ABC, abstractmethod

class Expansion(ABC):
    """
    Interfaz abstracta para clases de expansión de tokens.
    Permite definir distintos métodos de expansión según el motor o contexto.
    """
    @abstractmethod
    def expandir(self, token: str) -> str:
        """
        Expande un token según las reglas del motor/contexto.
        Args:
            token (str): Token a expandir.

        Returns:
            str: Token expandido.
        """
        pass

class ExpansionToken(Expansion):
    """
    Expande símbolos comunes y palabras técnicas (ej. 'C++' -> 'C plus plus')
    para mejorar la pronunciación en motores TTS.
    """
    def __init__(self, logger=None):
        self.logger = logger

    def expandir(self, token: str) -> str:
        """
        Expande símbolos y palabras técnicas para mejorar la pronunciación en TTS.
        Ejemplo: 'C++' -> 'C plus plus', 'C#' -> 'C sharp'
        Puedes añadir más reglas aquí.
        """
        if '++' in token:
            res = token.replace('++', ' plus plus')
        elif '+' in token:
            res = token.replace('+', ' plus')
        elif '#' in token:
            res = token.replace('#', ' sharp')
        else:
            res = token
        if self.logger:
            self.logger.debug(f"ExpansionToken.expandir: '{token}' -> '{res}'")
        return res

    @staticmethod
    def expand_for_gtts(tok):
        """
        Expande tokens para gTTS según reglas estándar.
        """
        return ExpansionToken().expandir(tok)
    
    @staticmethod
    def expand_for_pyttsx3(tok):
        """
        Expande tokens para pyttsx3 según reglas estándar.
        Puedes especializar si lo requieren en el futuro.
        """
        return ExpansionToken().expandir(tok)