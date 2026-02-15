"Codigo encargado de la verificacion del tipo de entrada"

# Librerías estándar de Python
import os          # Manejo de archivos y directorios

# Librerías externas (instaladas con pip)
import validators  # Validación de URLs

# Importación del logger personalizado para el sistema
from Logger import Telemetriaindustrial

# Inicializacion del logger
logger = Telemetriaindustrial(nombre="ExtraccionDatosLogger").logger

#Primera clase: tipo de entrada a la funcion
class prefijo:

    #variable de clase con los prefijos comunes
    Prefijos = tuple(f"{prefijo}://" for prefijo in ['http', 'https'])

    # Metodo estatico para construir prefijos
    @staticmethod
    def construir_prefijos(esquemas_permitidos=None):

        # Si no se proporcionan esquemas, usar los predeterminados
        if not esquemas_permitidos:  
            return prefijo.Prefijos # Retornar los prefijos predeterminados

        # En caso de tener esquemas permitidos, validar que todos sean cadenas no vacías
        if all(isinstance(esquema, str) and esquema for esquema in esquemas_permitidos):
            return tuple(f"{esquema}://" for esquema in esquemas_permitidos) # Retornar los prefijos construidos

        # Si hay esquemas no válidos, registrar un error y usar los predeterminados
        logger.error(f"Esquemas permitidos no válidos: {esquemas_permitidos}. Usando prefijos predeterminados.")
        return prefijo.Prefijos # Retornar los prefijos predeterminados

prefijos_construidos = prefijo.construir_prefijos() # Construir los prefijos al cargar el módulo para su uso posterior

class tipoentrada:
    # Metodo estatico para determinar el tipo de entrada
    @staticmethod
    def determinar_tipo(entrada, esquemas_permitidos=None):

        # Caso 1: Es un archivo existente
        if os.path.isfile(entrada):
            return "Archivo", entrada # Retornar tipo "Archivo" y la ruta del archivo
        
        # Caso 2: Es una URL
        if validators.url(entrada):

            #registro en logger
            logger.info(f"Tipo de entrada: '{entrada}' URL valida detectada")

            #Creacion de prefijos permitidos
            
            prefijos = prefijos_construidos

            # Verificar y corregir si falta algún esquema
            if not entrada.startswith(prefijos):
                logger.info(f"URL sin esquema detectada, añadiendo esquema predeterminado 'http://': {entrada}")
                entrada = 'http://' + entrada  # Añadir esquema predeterminado

            return "URL", entrada # Retornar tipo "URL" y la URL corregida
        
        # Caso 3: Es un texto plano
        if isinstance(entrada, str):
            logger.info(f"Tipo de entrada: '{entrada}' Texto plano detectado")
            return "Textoplano", entrada # Retornar tipo "Textoplano" y el texto plano
        
        else:
            logger.warning(f"Tipo de entrada desconocido: '{entrada}'. No es Archivo, URL válida ni Texto Plano.")
            return None, entrada # Retornar None si no coincide con ningun tipo conocido