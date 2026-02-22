from pydub import AudioSegment
from abc import ABC, abstractmethod

class ICombinador(ABC):
    """
    Interfaz abstracta para combinadores de fragmentos de audio.
    Permite definir múltiples estrategias de combinación según contexto o motor.
    """
    @abstractmethod
    def combinar(self, archivos) -> AudioSegment:
        """
        Combina los fragmentos de audio en un solo objeto AudioSegment.
        Args:
            archivos (list): Lista de tuplas (AudioSegment, nombre_archivo) a combinar.
                Los fragmentos pueden ser audio de voz o silencios.
        Returns:
            AudioSegment: Objeto de audio concatenado en memoria.
        Raises:
            ValueError: Si la lista de archivos está vacía.
        """
        pass

class CombinadorAudio(ICombinador):
    """
    Realiza la combinación secuencial de fragmentos de audio (voz y silencios) usando pydub.
    Puede loguear el proceso de combinación si se provee un logger.
    No exporta el archivo físico; la responsabilidad queda en el exportador.
    """
    def __init__(self, logger=None):
        """
        Inicializa el combinador.
        Args:
            logger (object, optional): Logger para auditoría y debugging.
        """
        self.logger = logger

    def combinar(self, archivos) -> AudioSegment:
        """
        Concatena todos los fragmentos de audio en el orden original.
        Filtra fragmentos None y distingue silencios en los logs.
        Args:
            archivos (list): Lista de tuplas (AudioSegment, nombre_fragmento).
        Returns:
            AudioSegment: Audio combinado en memoria listo para exportar.
        Raises:
            ValueError: Si no hay ningún archivo para combinar.
        """
        if not archivos:
            raise ValueError("No hay archivos para combinar.")

        audio_final = AudioSegment.empty()
        for idx, (audio, nombre_fragmento) in enumerate(archivos):
            if audio is None:
                if self.logger:
                    self.logger.warning(f"Fragmento {idx} ({nombre_fragmento}) es None y será omitido.")
                continue
            if nombre_fragmento and "silencio" in nombre_fragmento:
                if self.logger:
                    self.logger.debug(f"Agregando silencio: {nombre_fragmento}")
            else:
                if self.logger:
                    self.logger.debug(f"Agregando fragmento: {nombre_fragmento}")
            audio_final += audio

        if self.logger:
            self.logger.info("Combinación de audio completada exitosamente.")
        return audio_final