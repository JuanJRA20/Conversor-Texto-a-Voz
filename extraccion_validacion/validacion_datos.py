"codigo encargado de la validacion de los datos de entrada"

# Librerías estándar de Python
import os          # Manejo de archivos y directorios
import re          # Manejo de expresiones regulares

# Librerías externas (instaladas con pip)
import validators  # Validación de URLs
import magic       # Detección de tipos MIME de archivos

# Importación del logger personalizado para el sistema
from Logger import Telemetriaindustrial

# Inicializacion del logger
logger = Telemetriaindustrial(nombre="ValidacionDatosLogger").logger

# Segunda clase: Validacion de datos
class ValidadorDatos:

        # Metodos estaticos para validar diferentes tipos de datos
        @staticmethod
        def texto(entrada):

            # Validar que la entrada sea una cadena
            if not isinstance(entrada, str):
                logger.warning(f"Validación de texto: La entrada no es una cadena válida (tipo: {type(entrada)}).")
                return False # Retornar False si no es una cadena
            
            # Validar que el texto no este vacio y sea una cadena
            if entrada.strip() == "":
                logger.warning("Validacion de texto: El texto esta vacio") 
                return False # Retornar False si el texto esta vacio
            
            # Si pasa todas las validaciones, retornar True
            else:
                logger.info("Validacion de texto: Exitoso")
                return True # Retornar True si el texto es valido
        
        # Metodos estaticos para validar archivos y URLs
        @staticmethod
        def archivo(entrada, mime_esperado=None):

            try: #bloque try-except para capturar errores inesperados

                # Verificar si el archivo existe
                if not os.path.isfile(entrada): #volvemos a verificar si el archivo existe por seguridad
                    logger.warning("Validacion de archivo: El archivo no existe")
                    return False # Retornar False si el archivo no existe
                
                # Verificar si el archivo esta vacio
                if os.path.getsize(entrada) == 0:
                    logger.warning("Validacion de archivo: El archivo esta vacio")
                    return False # Retornar False si el archivo esta vacio
                
                # Obtener el tipo MIME del archivo usando la libreria magic
                tipo_archivo = magic.from_file(entrada, mime=True) # Obtener el tipo MIME del archivo
                logger.info(f"Tipo MIME del archivo: {tipo_archivo}") # Registrar el tipo MIME obtenido
                
                # verificar que se obtuvo un tipo MIME valido
                if not tipo_archivo:
                    logger.warning("Validacion de archivo: No se pudo determinar el tipo MIME del archivo")
                    return False # Retornar False si no se pudo determinar el tipo MIME
                
                # Verificar si el tipo MIME coincide con el esperado en caso de tener un tipo esperado
                if mime_esperado and tipo_archivo != mime_esperado:
                    logger.warning(f"Validacion de archivo: Tipo MIME no coincide (esperado: {mime_esperado}, obtenido: {tipo_archivo})")
                    return False # Retornar False si el tipo MIME no coincide

                # Si pasa todas las validaciones, retornar True
                logger.info("Validacion de archivo: Exitoso")
                return True 
            
            # Capturar cualquier excepcion inesperada
            except Exception as e:
                logger.error(f"Validacion de archivo: Error al validar el archivo - {str(e)}")
                return False # Retornar False en caso de error
        
        # Metodos estaticos para validar URLs
        @staticmethod
        def url(entrada):

            try: #bloque try-except para capturar errores inesperados

                # Validar que la entrada sea una URL válida usando validators
                if not validators.url(entrada):
                    logger.warning(f"Validacion de URL: La entrada no es una URL valida ({entrada})")
                    return False # Retornar False si no es una URL valida
                
                # Como ya se valido la URL en la clase TipoEntrada, aqui solo se validara el dominio
                dominio = re.match(r'^(?:http[s]?://)?([^/]+)', entrada) # Extraer el dominio de la URL
                dominio = dominio.group(1) if dominio else None # Obtener el dominio si se encontro

                # Validar el dominio usando validators
                if not dominio or not validators.domain(dominio):
                    logger.warning(f"Dominio no valido ({dominio})")
                    return False # Retornar False si el dominio no es valido

                # Si pasa todas las validaciones, retornar True
                logger.info("Validacion de URL: Exitoso")
                return True
            
            except Exception as e:
                logger.error(f"Validacion de URL: Error al validar la URL - {str(e)}")
                return False # Retornar False en caso de error