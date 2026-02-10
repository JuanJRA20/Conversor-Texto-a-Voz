"""
En este archivo python, pasaremos a desarrollar la primera etapa del proyecto "Extraccion y validacion de datos".

Aqui se encontraran las funciones necesarias con respecto a la extraccion de datos desde diversas fuentes,
tales como archivos JSON, textos planos y extractos de paginas web.

Ademas, se implementaran mecanismos basicos de validacion para asegurar la integridad
y calidad de los datos extraidos.

El archivo constara de tres clases principales:
- TipoEntrada: Determina el tipo de entrada (archivo, URL o texto plano). Con dos metodos estaticos:
    - construir_prefijos: Construye prefijos de esquema para URLs.
    - determinar_tipo: Determina el tipo de entrada.
- ExtraccionDatos: Proporciona metodos para extraer datos de diferentes fuentes. Con tres metodos estaticos:
    - textoplano: Extrae texto plano.
    - archivo: Extrae texto desde archivos (txt, json, pdf).
    - URL: Extrae texto desde paginas web.
- ValidadorDatos: Proporciona métodos para validar textos, archivos y URLs. Con tres metodos estaticos:
    - texto: Valida textos.
    - archivo: Valida archivos.
    - url: Valida URLs.
"""

# Importacion de librerias necesarias:

# Librerías estándar de Python
import os          # Manejo de archivos y directorios
import re          # Manejo de expresiones regulares
import json        # Manejo de archivos JSON

# Librerías externas (instaladas con pip)
import validators  # Validación de URLs
import PyPDF2 as pdf  # Manipulación de archivos PDF
import magic       # Detección de tipos MIME de archivos
import requests    # Realizar solicitudes HTTP
import lxml.html as html  # Parseo eficiente de HTML
from bs4 import BeautifulSoup as bs  # Parseo personalizable de HTML
from newspaper import Article  # Extracción de noticias y artículos

# Importación del logger personalizado para el sistema
from Logger import Telemetriaindustrial

# Inicializacion del logger
logger = Telemetriaindustrial(nombre="ExtraccionDatosLogger").logger

#Primera clase: tipo de entrada a la funcion
class TipoEntrada:

    #variable de clase con los prefijos comunes
    prefijos = tuple(f"{prefijo}://" for prefijo in ['http', 'https'])

    # Metodo estatico para construir prefijos
    @staticmethod
    def construir_prefijos(esquemas_permitidos=None):

        # Si no se proporcionan esquemas, usar los predeterminados
        if not esquemas_permitidos:  
            return TipoEntrada.prefijos # Retornar los prefijos predeterminados

        # En caso de tener esquemas permitidos, validar que todos sean cadenas no vacías
        if all(isinstance(esquema, str) and esquema for esquema in esquemas_permitidos):
            return tuple(f"{esquema}://" for esquema in esquemas_permitidos) # Retornar los prefijos construidos

        # Si hay esquemas no válidos, registrar un error y usar los predeterminados
        logger.error(f"Esquemas permitidos no válidos: {esquemas_permitidos}. Usando prefijos predeterminados.")
        return TipoEntrada.prefijos # Retornar los prefijos predeterminados

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
            prefijos = TipoEntrada.construir_prefijos(esquemas_permitidos)

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
        
# Tercera clase: Extraccion de datos
class ExtraccionDatos:

    # Mapeo por extensión a métodos (constante de clase)
    FORMATO_MANEJADORES = {'.txt': '_extraer_texto_txt', '.json': '_extraer_texto_json', '.pdf': '_extraer_texto_pdf'}

    # Metodo estatico para extraer datos de texto plano
    @staticmethod
    def textoplano(entrada):

        try: #bloque try-except para capturar errores inesperados

            texto = entrada.strip() # Eliminar espacios en blanco al inicio y final
            logger.info("Extraccion de texto plano: Exitoso") 
            return texto # Retornar el texto plano extraido
        
        except Exception as e: # Capturar cualquier excepcion inesperada
            logger.error(f"Extraccion de texto plano: Error al extraer el texto - {str(e)}")
            return None # Retornar None en caso de error
    
    # Metodo estatico para extraer datos de archivos
    @staticmethod
    def archivo(entrada):

        try: #bloque try-except para capturar errores inesperados

            _, formato = os.path.splitext(entrada) # Obtener la extension del archivo
            formato = formato.lower() # Convertir la extension a minusculas

            # Verificar si el formato es soportado, verificando si se encuentra dentro del diccionario de manejadores
            if not formato in ExtraccionDatos.FORMATO_MANEJADORES:
                logger.error(f"Extraccion de archivo: Formato no soportado ({formato})")
                return None # Retornar None si el formato no es soportado

            # Llamada al metodo correspondiente segun el formato
            metodo = getattr(ExtraccionDatos, ExtraccionDatos.FORMATO_MANEJADORES[formato]) # Obtener el metodo correspondiente
            texto = metodo(entrada) # Llamar al metodo para extraer el texto
            logger.info(f"Extraccion de archivo ({formato}): Exitoso")
            return texto # Retornar el texto extraido
        
        except Exception as e: # Capturar cualquier excepcion inesperada
            logger.error(f"Extraccion de archivo: Error al extraer el archivo - {str(e)}")
            return None # Retornar None en caso de error
    
    # Metodo estatico generico para gestionar extracciones de archivos
    @staticmethod
    def gestionador_extracciones(entrada, metodo, tipo, modo='r', encoding='utf-8'):

        try: #bloque try-except para capturar errores inesperados

            # Abrir el archivo en modo lectura con encoding especificado por el extractor
            with open(entrada, mode=modo, encoding=None if modo=='rb' else encoding) as archivo:
                texto = metodo(archivo)  # Ejecutar el extractor específico
                logger.info(f"Extracción de archivo {tipo}: Exitosa.")
                return texto # Retornar el texto extraido
            
        except Exception as e: # Capturar cualquier excepcion inesperada
            logger.error(f"Extracción de archivo {tipo}: Error - {str(e)}")
            return None # Retornar None en caso de error

    # Metodo estatico para extraer datos de archivos txt
    @staticmethod
    def _extraer_texto_txt(entrada):
        # Llamar al gestor de extracciones con la funcion de lectura para devolver el texto extraido
        return ExtraccionDatos.gestionador_extracciones(entrada, lambda archivo: archivo.read(), "TXT")
    
    # Metodo estatico para extraer datos de archivos json
    @staticmethod
    def _extraer_texto_json(entrada):

            # Funcion interna para procesar archivos JSON
            def procesar_json(file):

                data = json.load(file) # Cargar el contenido del archivo JSON

                # Verificar si el contenido es un diccionario y extraer el texto
                if isinstance(data, dict):
                    return " ".join(str(value) for value in data.values()) # Unir los valores del diccionario en una sola cadena
                
                # Verificar si el contenido es una lista y extraer el texto
                if isinstance(data, list):
                    return " ".join(str(item) for item in data) # Unir los elementos de la lista en una sola cadena
                
                # Si el formato no es valido, registrar un error
                else:
                    raise ValueError(f"El archivo JSON {entrada} no tiene un formato válido.") # Lanzar una excepcion si el formato no es valido

            # Llamar al gestor de extracciones con el procesador JSON para devolver el texto extraido
            return ExtraccionDatos.gestionador_extracciones(entrada, procesar_json, "JSON")

    
    # Metodo estatico para extraer datos de archivos pdf
    @staticmethod
    def _extraer_texto_pdf(entrada):

        # Funcion interna para procesar archivos PDF
        def procesar_pdf(archivo):
            texto = "" # Variable para almacenar el texto extraido

            # Crear un lector de PDF usando PyPDF2
            lector_pdf = pdf.PdfReader(archivo)

            # Iterar sobre todas las paginas y extraer el texto
            for pagina in lector_pdf.pages:
                texto += pagina.extract_text() # Extraer el texto de la pagina y agregarlo al texto total

            logger.info("Extraccion de archivo PDF: Exitoso")
            return texto # Retornar el texto extraido
        
        # Llamar al gestor de extracciones con el procesador PDF para devolver el texto extraido
        return ExtraccionDatos.gestionador_extracciones(entrada, procesar_pdf, "PDF", modo='rb')
    
    # Metodo estatico para extraer datos de URLs
    @staticmethod
    def url(entrada, parser='lxml'):

        #bloque try-except para capturar errores inesperados
        try: 
            try:

                articulo = Article(entrada) # Crear un objeto Article de newspaper3k
                articulo.download() # Descargar el contenido del articulo
                articulo.parse() # Parsear el contenido del articulo

                #verificar si el texto extraido no esta vacio
                if articulo.text: 
                    texto = articulo.text # si el texto no esta vacio, obtener el texto del articulo
                    logger.info("Extraccion de URL: Exitoso")
                    return texto.strip() # Retornar el texto extraido, eliminando espacios en blanco al inicio y final
                
            except Exception as e: # Capturar cualquier excepcion inesperada en newspaper3k
                logger.warning(f"Extraccion de URL (newspaper): Fallo -{str(e)}")  

            # Metodo alternativo usando requests y lxml o BeautifulSoup
            respuesta = requests.get(entrada, timeout=10) # Realizar una solicitud GET a la URL con un tiempo de espera de 10 segundos

            # Verificar el codigo de estado HTTP
            if respuesta.status_code != 200: # Si el codigo de estado no es 200, registrar una advertencia
                logger.warning(f"Extracción de URL: Código de estado HTTP no válido: {respuesta.status_code}.")
                return None # Retornar None si el codigo de estado no es valido
            
            # Parsear el contenido HTML usando lxml o BeautifulSoup segun el parser especificado
            if parser == 'lxml': # Si el parser es lxml, o no es especificado

                arbol = html.fromstring(respuesta.content) # Parsear el contenido HTML con lxml
                encabezado = arbol.xpath('//h1/text() | //h2/text() | //h3/text()') # Extraer encabezados (h1, h2, h3)
                parrafos = arbol.xpath('//p/text()') # Extraer párrafos relevantes
                texto_encabezados = ' '.join(encabezado) # Unir los encabezados en una sola cadena
                texto_parrafos = ' '.join(parrafos) # Unir los párrafos en una sola cadena
                texto = (texto_encabezados + " " + texto_parrafos).strip() # Combinar encabezados y párrafos, eliminando espacios en blanco al inicio y final

                # Verificar si se encontro texto en los parrafos
                if not texto.strip():
                    logger.warning("Extraccion de URL: No se encontro texto en los parrafos.")
                    return None # Retornar None si no se encontro texto
                
                #Si todo es exitoso, retornar el texto extraido
                logger.info("Extraccion de URL (metodo alternativo): Exitoso")
                return texto

            # si se ingresa otro parser, usar BeautifulSoup
            else:
                # Parsear el contenido HTML con BeautifulSoup
                soup = bs(respuesta.content, 'html.parser')

            # Extraer encabezados (h1, h2, h3) y párrafos relevantes
            texto_encabezados = ' '.join(h.get_text() for h in soup.find_all(['h1', 'h2', 'h3']))
            texto_parrafos = ' '.join(p.get_text() for p in soup.find_all('p'))

            # Combinar encabezados y párrafos, eliminando espacios en blanco al inicio y final
            texto = (texto_encabezados + " " + texto_parrafos).strip()

            # Verificar si se encontro texto en los parrafos
            if not texto:
                logger.warning("Extraccion de URL: No se encontro texto en los parrafos.")
                return None # Retornar None si no se encontro texto
            
            #Si todo es exitoso, retornar el texto extraido
            logger.info("Extraccion de URL (metodo alternativo): Exitoso")
            return texto
        
        # Capturar excepciones específicas de requests por tiempo de espera agotado
        except requests.exceptions.Timeout:
            logger.warning("Extracción de URL: Tiempo de espera agotado al intentar acceder a la URL.")
            return None # Retornar None en caso de timeout
        
        # Capturar cualquier otra excepcion inesperada de requests
        except requests.exceptions.RequestException as e:
            logger.error(f"Extracción de URL: Error al realizar la solicitud - {str(e)}")
            return None # Retornar None en caso de error
    
    # Metodo estatico para gestionar la extraccion y validacion de datos segun el tipo de entrada
    @classmethod
    def formatos_manejadores(entrada):
        return {'.txt': '_extraer_texto_txt', '.json': '_extraer_texto_json', 
                        '.pdf': '_extraer_texto_pdf'}
    
    # Metodo estatico para verificar que los manejadores definidos en formatos_manejadores existan en la clase
    @classmethod
    def varificar_manejadores(entrada):
        assert all(hasattr(ExtraccionDatos, metodo) for metodo in entrada.formatos_manejadores().values()), \
                "Algunos métodos definidos en FORMATO_MANEJADORES no existen en la clase."




