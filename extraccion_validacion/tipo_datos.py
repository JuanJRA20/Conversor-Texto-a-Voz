"Codigo encargado de la verificacion del tipo de entrada"

# Librerías estándar de Python
import os          # Manejo de archivos y directorios
from abc import ABC, abstractmethod # Clases abstractas para definir interfaces
from typing import Optional, List, Tuple # Tipos para anotaciones
# Librerías externas (instaladas con pip)
import validators  # Validación de URLs

PREFIJOS_DEFAULT = ('http', 'https', 'ftp') # Prefijos de URL predeterminados

#Primera clase: tipo de entrada a la funcion
def construir_prefijos(esquemas: Optional[List[str]] = None) -> Tuple[str, ...]:
    """
    Construye tupla de prefijos de esquema para URLs.
    Args:
        esquemas: Lista de esquemas (ej: ['http', 'https', 'ftp'])
    Returns:
        Tupla de prefijos construidos    
"""
    if not esquemas:
        return PREFIJOS_DEFAULT
    
    # Validar que todos sean strings no vacíos
    if not all(isinstance(e, str) and e for e in esquemas):
        return PREFIJOS_DEFAULT
    
    return tuple(f"{esquema}://" for esquema in esquemas)
    
class IDetectorTipo(ABC):
    """Interfaz para detectores de tipo de entrada."""
    
    @abstractmethod
    def detectar(self, entrada: str) -> bool:
        """Verifica si la entrada es de este tipo."""
        pass
    
    @abstractmethod
    def obtener_tipo(self) -> str:
        """Retorna el nombre del tipo."""
        pass


class DetectorArchivo(IDetectorTipo):
    """Detecta si la entrada es un archivo existente."""
    
    def detectar(self, entrada: str) -> bool:
        return os.path.isfile(entrada)
    
    def obtener_tipo(self) -> str:
        return "Archivo"


class DetectorURL(IDetectorTipo):
    """Detecta si la entrada es una URL válida."""
    
    def __init__(self, prefijos: Optional[Tuple[str, ...]] = PREFIJOS_DEFAULT):
        self.prefijos = construir_prefijos(prefijos)
    
    def detectar(self, entrada: str) -> bool:
        return validators.url(entrada) is True
    
    def obtener_tipo(self) -> str:
        return "URL"
    
    def normalizar_entrada(self, entrada: str) -> str:
        """Normaliza la URL agregando esquema si falta."""
        if not entrada.startswith(self.prefijos):
            return f'http://{entrada}'
        return entrada

class DetectorTextoPlano(IDetectorTipo):
    """Detecta texto plano (fallback final)."""
    
    def detectar(self, entrada: str) -> bool:
        return isinstance(entrada, str)
    
    def obtener_tipo(self) -> str:
        return "Textoplano"

class ClasificadorTipoEntrada:
    """
    Clasifica y normaliza diferentes tipos de entrada.
    Usa Chain of Responsibility para determinar el tipo.
    """
    
    def __init__(self, prefijos: Optional[Tuple[str, ...]] = PREFIJOS_DEFAULT, logger=None):
        """
        Args:
            prefijos: Tupla de prefijos de esquema para URLs
            logger: Logger opcional para registrar eventos
        """
        self.logger = logger
        
        self.detector_archivo = DetectorArchivo()
        self.detector_url = DetectorURL(prefijos=prefijos)
        self.detector_texto = DetectorTextoPlano()
        
        # Detectores en orden de prioridad
        self.detectores = [self.detector_archivo, self.detector_url, self.detector_texto]
    
    def determinar_tipo(self, entrada: str) -> Tuple[Optional[str], str]:
        """
        Determina el tipo de entrada y la normaliza si es necesario.
        
        Args:
            entrada: Texto, archivo o URL a clasificar
            
        Returns:
            Tupla (tipo, entrada_normalizada)
            donde tipo puede ser: "Archivo", "URL", "Textoplano", None
        """
        for detector in self.detectores:
            if detector.detectar(entrada):
                tipo = detector.obtener_tipo()
                
                # Normalizar si es URL
                if isinstance(detector, DetectorURL):
                    entrada = detector.normalizar_entrada(entrada)
                    if self.logger:
                        self.logger.info(f"URL detectada y normalizada: {entrada}")
                
                if self.logger:
                    self.logger.info(f"Tipo de entrada detectado: {tipo}")
                
                return tipo, entrada
        
        # No se pudo determinar
        if self.logger:
            self.logger.warning(f"Tipo de entrada desconocido: {entrada}")
        
        return None, entrada
    
    def es_archivo(self, entrada: str) -> bool:
        """Verifica rápidamente si es archivo."""
        return self.detector_archivo.detectar(entrada)
    
    def es_url(self, entrada: str) -> bool:
        """Verifica rápidamente si es URL."""
        return self.detector_url.detectar(entrada)
    
    def es_texto_plano(self, entrada: str) -> bool:
        """Verifica rápidamente si es texto plano."""
        return not self.es_archivo(entrada) and not self.es_url(entrada)
    
 