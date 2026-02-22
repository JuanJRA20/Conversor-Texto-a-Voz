from abc import ABC, abstractmethod
import os

class ILimpiador(ABC):
    """
    Interfaz para limpiadores de archivos temporales de audio.
    Permite definir distintas estrategias de limpieza según el contexto o motor.
    """
    @abstractmethod
    def limpiar(self, archivos):
        """
        Elimina los archivos temporales generados durante el proceso.
        Args:
            archivos_generados (list[tuple]): Lista de tuplas (AudioSegment, nombre_archivo).
                Los fragmentos pueden ser audio de voz o silencios (cuyo nombre_archivo puede ser None).
        Returns:
            int: Número de archivos eliminados exitosamente.
        """
        pass

class LimpiadorArchivos(ILimpiador):
    """
    Implementación estándar de ILimpiador.
    Elimina archivos temporales de audio generados en el pipeline.
    Utiliza os.remove para eliminar cada archivo listado y loguea el proceso si aplica.
    """
    def __init__(self, logger=None):
        """
        Inicializa el limpiador.
        Args:
            logger (object, optional): Logger para auditoría y debugging.
        """
        self.logger = logger

    def limpiar(self, archivos):
        """
        Elimina archivos temporales especificados en archivos_generados.
        Args:
            archivos_generados (list[tuple]): Tuplas (AudioSegment, nombre_archivo).
        Returns:
            int: Cantidad de archivos eliminados exitosamente.
        """
        eliminados = 0
        for idx, (audio, nombre) in enumerate(archivos):
            # Solo intentamos eliminar si nombre (ruta) no es None y es un archivo real.
            if nombre and os.path.isfile(nombre):
                try:
                    os.remove(nombre)
                    eliminados += 1
                    if self.logger:
                        self.logger.debug(f"Archivo eliminado: {nombre}")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Error al eliminar {nombre}: {e}")
            else:
                if self.logger:
                    self.logger.info(f"No se elimina: {nombre} (silencio virtual o no es archivo) en fragmento {idx}.")
        if self.logger:
            self.logger.info(f"{eliminados} archivos temporales eliminados exitosamente.")
        return eliminados