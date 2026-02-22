from abc import ABC, abstractmethod
from pydub import AudioSegment

class IExportador(ABC):
    """
    Interfaz para exportadores de audio.
    Permite definir distintas estrategias de exportación (formatos, rutas, etc).
    """
    @abstractmethod
    def exportar(self, archivo: AudioSegment, nombre: str, formato: str = "mp3") -> str:
        """
        Exporta un objeto AudioSegment a un archivo de audio en disco.
        Args:
            archivo (AudioSegment): Objeto de audio combinado a exportar.
            nombre (str): Nombre del archivo final a exportar (sin extensión).
            formato (str): Formato del archivo (por defecto 'mp3').
        Returns:
            str: Ruta del archivo final exportado.
        Raises:
            ValueError: Si archivo es None.
            Exception: Si ocurre error en la exportación.
        """
        pass

class Exportador(IExportador):
    """
    Implementación estándar del exportador de audio.
    Permite guardar el audio en diferentes formatos y registra el proceso si se provee logger.
    """
    def __init__(self, logger=None):
        self.logger = logger

    def exportar(self, archivo: AudioSegment, nombre: str, formato: str = "mp3") -> str:
        """
        Exporta el AudioSegment como un archivo físico en disco y loguea el proceso.
        Args:
            archivo (AudioSegment): Audio combinado a exportar.
            nombre (str): Nombre del archivo final a exportar (sin extensión).
            formato (str): Formato del archivo (ej. 'mp3', 'wav').
        Returns:
            str: Ruta del archivo final exportado.
        """
        if not archivo:
            raise ValueError("No hay audio para exportar.")

        ruta_final = f"{nombre}.{formato}"
        try:
            archivo.export(ruta_final, format=formato)
            if self.logger:
                self.logger.debug(f"Archivo exportado: {ruta_final}")
            return ruta_final
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al exportar archivo {ruta_final}: {e}")
            raise
        