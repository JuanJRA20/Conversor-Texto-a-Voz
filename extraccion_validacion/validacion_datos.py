"codigo encargado de la validacion de los datos de entrada"

# Librerías estándar de Python
import os          # Manejo de archivos y directorios
import re          # Manejo de expresiones regulares

# Librerías externas (instaladas con pip)
import validators  # Validación de URLs
import magic       # Detección de tipos MIME de archivos
from abc import ABC, abstractmethod # Clases abstractas para definir interfaces
from typing import Optional, Dict # Tipos para anotaciones
MIMES_SOPORTADOS: Dict[str, str] = {'.txt': 'text/plain', '.json': 'application/json',
                                     '.pdf': 'application/pdf'}

# Segunda clase: Validacion de datos
class IValidador(ABC):
    @abstractmethod
    def validar(self, entrada) -> bool:
        pass

class ValidarTextoPlano(IValidador):
    def __init__(self, logger=None):
        self.logger = logger
         
    def validar(self, entrada):
            # Validar que la entrada sea una cadena
        if not isinstance(entrada, str):
            if self.logger:
                self.logger.warning("Entrada no es una cadena: %s", type(entrada))
            return False # Retornar False si no es una cadena
        
        # Validar que el texto no este vacio y sea una cadena
        if entrada.strip() == "":
            return False # Retornar False si el texto esta vacio
        
        # Si pasa todas las validaciones, retornar True
        else:
            return True # Retornar True si el texto es valido
    
class ValidarArchivo(IValidador):

    def __init__(self, mime_esperado: Optional[str] = None, logger=None):
        self.mime_esperado = mime_esperado
        self.logger = logger

   
    def validar(self, entrada):

        try: #bloque try-except para capturar errores inesperados

            existe = self._validar_existencia(entrada) # Validar que el archivo exista
            if not existe:
                return False # Retornar False si el archivo no existe
            
            tamano_valido = self._validar_tamano(entrada) # Validar que el archivo no este vacio
            if not tamano_valido:
                return False # Retornar False si el archivo esta vacio
            
            tipo_valido = self._validar_tipo_mime(entrada, self.mime_esperado) # Validar que el tipo MIME del archivo sea el esperado
            if not tipo_valido:
                return False # Retornar False si el tipo MIME no es el esperado
            
            if self.logger:
                self.logger.info("Archivo validado: %s", entrada) # Registrar en el logger que el archivo ha sido validado exitosamente

            # Si pasa todas las validaciones, retornar True
            return True
        
        except (OSError, IOError) as e:
            if self.logger:
                self.logger.error(f"Validación de archivo: Error de I/O - {e}")
            return False
    
        except Exception as e:
            if self.logger:
                self.logger.error(f"Validación de archivo: Error inesperado - {e}")
            return False
    
    def _validar_existencia(self, ruta: str) -> bool:
        if not os.path.isfile(ruta):
            if self.logger:
                self.logger.warning("Archivo no encontrado: %s", ruta)
            return False
        return True
    
    def _validar_tamano(self, ruta: str) -> bool:
        if os.path.getsize(ruta) == 0:
            if self.logger:
                self.logger.warning("Archivo vacío: %s", ruta)
            return False
        return True
    
    def _validar_tipo_mime(self, ruta: str, mime_esperado: Optional[str]) -> bool:
        tipo_archivo = magic.from_file(ruta, mime=True)
        if not tipo_archivo:
            if self.logger:
                self.logger.warning("No se pudo determinar el tipo MIME del archivo: %s", ruta)
            return False
        if mime_esperado and tipo_archivo != mime_esperado:
            if self.logger:
                self.logger.warning("Tipo MIME no coincide (esperado: %s, encontrado: %s): %s", mime_esperado, tipo_archivo, ruta)
            return False
        return True
    
class ValidarURL(IValidador):      
    # Metodos estaticos para validar URLs
    def __init__(self, logger=None):
        self.logger = logger
            
    def validar(self, entrada):

        try: #bloque try-except para capturar errores inesperados

            # Validar que la entrada sea una URL válida usando validators
            if not self._validar_formato(entrada):
                return False # Retornar False si el formato de la URL no es válido
            if not self._validar_dominio(entrada):
                return False # Retornar False si el dominio de la URL no es válido
            # Si pasa todas las validaciones, retornar True
            if self.logger:
                self.logger.info("URL validada: %s", entrada) # Registrar en el logger que la URL ha sido validada exitosamente
            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"Validación de URL: Error inesperado - {e}")
            return False # Retornar False en caso de error
        
    def _validar_formato(self, url: str) -> bool:
        # Validar que la URL tenga un formato correcto usando validators
        return validators.url(url) is True
    
    def _validar_dominio(self, url: str) -> bool:
        # Extraer el dominio de la URL y validarlo usando validators
        dominio = re.match(r'^(?:http[s]?://)?([^/]+)', url)
        dominio = dominio.group(1) if dominio else None
        return dominio and validators.domain(dominio)

class GestorValidadores:
    """
    Gestor que coordina múltiples validadores.
    Patrón Strategy para seleccionar el validador apropiado.
    """
    def __init__(self, logger=None):
        """
        Args:
            logger: Logger para todos los validadores
        """
        self.logger = logger
        self.validadores = {"texto": ValidarTextoPlano(logger), "archivo": ValidarArchivo(logger=logger),
                            "url": ValidarURL(logger)}
    
    def validar_texto(self, entrada: str) -> bool:
        """Valida texto plano."""
        return self.validadores["texto"].validar(entrada)
    
    def validar_archivo(self, entrada: str, mime_esperado: Optional[str] = None) -> bool:
        """
        Valida archivo.
        Args:
            entrada: Ruta del archivo
            mime_esperado: Tipo MIME esperado (opcional)
        """
        # Si no se especifica MIME, buscar por extensión
        if mime_esperado is None:
            mime_esperado = self._obtener_mime_por_extension(entrada)

        validador = ValidarArchivo(mime_esperado=mime_esperado, logger=self.logger)
        return validador.validar(entrada)
    
    def validar_url(self, entrada: str) -> bool:
        """Valida URL."""
        return self.validadores["url"].validar(entrada)
    
    def validar_por_tipo(self, entrada: str, tipo: str) -> bool:
        """
        Valida según el tipo especificado.
        Args:
            entrada: Dato a validar
            tipo: "texto", "archivo" o "url"  
        Returns: True si es válido
        """
        tipo_lower = tipo.lower()
        
        if tipo_lower == "archivo":
            return self.validar_archivo(entrada)
        elif tipo_lower == "url":
            return self.validar_url(entrada)
        elif tipo_lower in ("textoplano", "texto"):
            return self.validar_texto(entrada)
        else:
            raise ValueError(f"Tipo de validación no reconocido: {tipo}")
    
    def _obtener_mime_por_extension(self, ruta: str) -> Optional[str]:
        """
        Obtiene el MIME esperado según la extensión del archivo.
        
        Args:
            ruta: Ruta del archivo
            
        Returns:
            MIME tipo esperado o None si la extensión no está soportada
        """
        _, extension = os.path.splitext(ruta)
        mime = MIMES_SOPORTADOS.get(extension.lower())
        
        if mime is None and self.logger:
            self.logger.warning(f"Extensión no soportada: {extension}")
        
        return mime
