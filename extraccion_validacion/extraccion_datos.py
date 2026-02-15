"Codigo encargado exclusivamente de la extraccion de datos"

# Librerías estándar de Python
import os          # Manejo de archivos y directorios
import json        # Manejo de archivos JSON

from typing import Optional, Callable
from abc import ABC, abstractmethod
# Librerías externas (instaladas con pip)
import PyPDF2 as pdf  # Manipulación de archivos PDF
import requests    # Realizar solicitudes HTTP
import lxml.html as html  # Parseo eficiente de HTML
from bs4 import BeautifulSoup as bs  # Parseo personalizable de HTML
from newspaper import Article  # Extracción de noticias y artículos
import validators  # Validación de URLs

time_request_limit = 10

class IExtraccion(ABC):
    @abstractmethod
    def extraer(self, entrada) -> Optional[str]:
        pass
    @abstractmethod
    def puede_extraer(self, entrada) -> bool:
        pass

class ManejadorArchivos:
    """
    Manejador genérico para apertura/cierre de archivos.
    Elimina duplicación de código usando Template Method Pattern.
    """ 
    def __init__(self, logger=None):
        """
        Args: logger: Logger opcional para registrar eventos
        """
        self.logger = logger
    
    def procesar_archivo(self, ruta: str, procesador: Callable, tipo_archivo: str, modo: str = 'r',
                          encoding: Optional[str] = 'utf-8') -> Optional[str]:
        """
        Template method para procesamiento genérico de archivos.
        Maneja apertura, procesamiento, cierre y errores de forma uniforme.
        
        Args:
            ruta: Ruta del archivo a procesar
            procesador: Función que recibe el archivo abierto y retorna el texto
            tipo_archivo: Descripción del tipo para logging (ej: "TXT", "PDF")
            modo: Modo de apertura del archivo ('r' para texto, 'rb' para binario)
            encoding: Codificación del archivo (None para modo binario)
            
        Returns: Texto extraído o None si ocurre algún error
        """
        try:
            # Determinar encoding según modo
            codificado = encoding if modo != 'rb' else None
            
            # Abrir archivo con context manager (cierre automático)
            with open(ruta, mode=modo, encoding=codificado) as archivo:
                texto = procesador(archivo)
                
                if self.logger:
                    self.logger.info(f"Extracción {tipo_archivo}: Exitosa - {ruta}")
                
                return texto
        
        except FileNotFoundError:
            if self.logger:
                self.logger.error(f"Extracción {tipo_archivo}: Archivo no encontrado - {ruta}")
            return None
        
        except PermissionError:
            if self.logger:
                self.logger.error(f"Extracción {tipo_archivo}: Permiso denegado - {ruta}")
            return None
        
        except UnicodeDecodeError as e:
            if self.logger:
                self.logger.error(
                    f"Extracción {tipo_archivo}: Error de codificación - {ruta} - {e}"
                )
            return None
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Extracción {tipo_archivo}: Error inesperado - {ruta} - {e}")
            return None

class ExtraccionTextoPlano(IExtraccion):
    def __init__(self, logger=None):
        self.logger = logger

    def extraer(self, entrada):
        try: #bloque try-except para capturar errores inesperados

            texto = entrada.strip() # Eliminar espacios en blanco al inicio y final
            return texto # Retornar el texto plano extraido
        
        except Exception as e: # Capturar cualquier excepcion inesperada
            if self.logger:
                self.logger.error(f"Extraccion de texto plano: Error al extraer el texto - {str(e)}")
            return None # Retornar None en caso de error
        
    def puede_extraer(self, entrada):
        return isinstance(entrada, str) and bool(entrada.strip()) # Verificar que la entrada sea una cadena no vacía
    
class ExtraccionTXT(IExtraccion):
    def __init__(self, logger=None):
        self.logger = logger
        self.manejador = ManejadorArchivos(logger)

    def extraer(self, entrada):
        return self.manejador.procesar_archivo(ruta=entrada, procesador=lambda x: x.read(),
                                               tipo_archivo="TXT")
    
    
    def puede_extraer(self, entrada):
        return os.path.isfile(entrada) and entrada.lower().endswith('.txt') # Verificar que la entrada sea un archivo con extension .txt
    
class ExtraccionJSON(IExtraccion):
    def __init__(self, logger=None):
        self.logger = logger
        self.manejador = ManejadorArchivos(logger)

    def extraer(self, entrada):

        def procesar_json(archivo):
            data = json.load(archivo)
            if isinstance(data, dict):
                return " ".join(str(value) for value in data.values()) # Unir los valores del diccionario en una sola cadena
            elif isinstance(data, list):
                return " ".join(str(item) for item in data) # Unir los elementos de la lista en una sola cadena
            else:
                raise ValueError(f"El archivo JSON {entrada} no tiene un formato válido.") # Lanzar una excepcion si el formato no es valido

        return self.manejador.procesar_archivo(ruta=entrada, procesador=procesar_json, tipo_archivo="JSON")

    def puede_extraer(self, entrada):
        return os.path.isfile(entrada) and entrada.lower().endswith('.json') # Verificar que la entrada sea un archivo con extension .json
    
class ExtraccionPDF(IExtraccion):
    def __init__(self, logger=None):
        self.logger = logger
        self.manejador = ManejadorArchivos(logger)
    def extraer(self, entrada):
        def procesar_pdf(archivo):
            texto = ""
            lector_pdf = pdf.PdfReader(archivo)
            for pagina in lector_pdf.pages:
                texto += pagina.extract_text()

            if self.logger:
                self.logger.info("Extraccion de archivo PDF: Exitoso")
            return texto
        
        
        return self.manejador.procesar_archivo(ruta=entrada, procesador=procesar_pdf, tipo_archivo="PDF", modo='rb')
    
    def puede_extraer(self, entrada):
        return os.path.isfile(entrada) and entrada.lower().endswith('.pdf') # Verificar que la entrada sea un archivo con extension .pdf
    
class EstrategiaExtraccionURL(ABC):
    @abstractmethod
    def extraer(self, entrada) -> Optional[str]:
        pass

class ExtraccionURLNewspaper(EstrategiaExtraccionURL):
    def __init__(self, logger=None):
        self.logger = logger

    def extraer(self, entrada):
        try:
            articulo = Article(entrada)
            articulo.download()
            articulo.parse()

            if articulo.text:
                if self.logger:
                    self.logger.info("Extraccion de URL (newspaper): Exitoso")
                return articulo.text.strip()
        
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Extraccion de URL (newspaper): Fallo -{str(e)}")
        return None
    
class ExtraccionURLRequests(EstrategiaExtraccionURL):
    def __init__(self, logger=None, parser='lxml', timeout=time_request_limit):
        self.logger = logger
        self.parser = parser
        self.timeout = timeout
    def extraer(self, entrada):
        try:
            respuesta = requests.get(entrada, self.timeout) # Realizar una solicitud GET a la URL con un timeout definido

            if respuesta.status_code != 200:
                if self.logger:
                    self.logger.warning(f"Extracción de URL: Código de estado HTTP no válido: {respuesta.status_code}.")
                return None
            
            if self.parser == 'lxml':
                texto = self._extraer_lxml(respuesta)

            
            else:
                texto = self._extraer_bs(respuesta)

            if texto:
                if self.logger:
                    self.logger.info(f"Extracción de URL ({self.parser}): Exitosa")
                return texto
            else:
                if self.logger:
                    self.logger.warning(f"Extracción URL ({self.parser}): Sin contenido - {entrada}")
        
        except requests.exceptions.Timeout:
            if self.logger:
                self.logger.warning(f"Extracción URL: Timeout ({self.timeout}s) - {entrada}")
        
        except requests.exceptions.ConnectionError:
            if self.logger:
                self.logger.error(f"Extracción URL: Error de conexión - {entrada}")
        
        except requests.exceptions.RequestException as e:
            if self.logger:
                self.logger.error(f"Extracción URL: Error de requests - {e}")
        
        return None
        
    def _extraer_lxml(self, respuesta):
        try:
            arbol = html.fromstring(respuesta.content)
            encabezado = arbol.xpath('//h1/text() | //h2/text() | //h3/text()')
            parrafos = arbol.xpath('//p/text()')
            texto_encabezados = ' '.join(encabezado)
            texto_parrafos = ' '.join(parrafos)
            return (texto_encabezados + " " + texto_parrafos).strip()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Extracción de URL (lxml): Error al extraer el contenido - {str(e)}")
            return None
    
    def _extraer_bs(self, respuesta):
        try:
            soup = bs(respuesta.content, 'html.parser')
            texto_encabezados = ' '.join(h.get_text() for h in soup.find_all(['h1', 'h2', 'h3']))
            texto_parrafos = ' '.join(p.get_text() for p in soup.find_all('p'))
            texto = (texto_encabezados + " " + texto_parrafos).strip()
            return texto if texto else None
        except Exception as e:
            if self.logger:
                self.logger.error(f"Extracción de URL (BeautifulSoup): Error al extraer el contenido - {str(e)}")
            return None
    
class ExtraccionURL(IExtraccion):
    def __init__(self, logger=None, timeout=time_request_limit):
        self.logger = logger
        self.estrategias = [ExtraccionURLNewspaper(logger), ExtraccionURLRequests(parser='lxml', timeout=timeout, logger=logger),
            ExtraccionURLRequests(parser='beautifulsoup', timeout=timeout, logger=logger)]
        
    def extraer(self, entrada):
        #bloque try-except para capturar errores inesperados
        for estrategia in self.estrategias:
            nombre_estrategia = estrategia.__class__.__name__
            if self.logger:
                self.logger.debug(f"Intentando extracción con: {nombre_estrategia}")
            texto = estrategia.extraer(entrada)
            if texto:
                return texto
        
        # Todas las estrategias fallaron
        if self.logger:
            self.logger.warning(f"Extracción URL: Todas las estrategias fallaron - {entrada}")
        
        return None
    
    def puede_extraer(self, entrada: str) -> bool:
        """Verifica si es una URL válida."""
        return validators.url(entrada) is True
    

class GestorExtractores:
    """
    Gestor que coordina múltiples extractores.
    Implementa patrón Facade para simplificar la interfaz.
    Implementa Chain of Responsibility para selección automática.
    
    Características:
    - Selección automática del extractor apropiado
    - Orden de prioridad configurable
    - Extensible: permite agregar nuevos extractores dinámicamente
    - Manejo unificado de errores
    """
    
    def __init__(self, logger=None, timeout_http=time_request_limit):
        """
        Inicializa el gestor con extractores predeterminados.
        
        Args:
            logger: Logger opcional para todos los extractores
            timeout_http: Timeout para peticiones HTTP (solo URLs)
        """
        self.logger = logger
        
        # Extractores en orden de prioridad
        # El orden importa: se prueba de arriba a abajo hasta encontrar uno compatible
        self.extractores = [ExtraccionURL(logger, timeout=timeout_http), ExtraccionPDF(logger), ExtraccionJSON(logger),                       
            ExtraccionTXT(logger), ExtraccionTextoPlano(logger)]
        
        if self.logger:
            self.logger.info(f"GestorExtractores inicializado con {len(self.extractores)} extractores")
    
    def extraer(self, entrada: str) -> Optional[str]:
        """
        Extrae texto usando el extractor apropiado.
        Método principal del gestor (Facade Pattern).
        
        Proceso:
        1. Itera sobre extractores en orden de prioridad
        2. Llama a puede_procesar() para verificar compatibilidad
        3. Usa el primer extractor compatible
        4. Retorna texto extraído o None si todos fallan
        
        Args: entrada: Texto, archivo o URL a procesar
        Returns: Texto extraído o None si falla
        """
        for extractor in self.extractores:
            # Verificar si este extractor puede extraer la entrada
            if extractor.puede_extraer(entrada):
                nombre_extractor = extractor.__class__.__name__
                
                if self.logger:
                    self.logger.debug(f"Usando extractor: {nombre_extractor} para '{entrada}'")
                
                # Intentar extracción
                texto = extractor.extraer(entrada)
                
                if texto:
                    return texto
                else:
                    if self.logger:
                        self.logger.warning(f"Extractor {nombre_extractor} compatible pero falló la extracción")
        
        # Ningún extractor pudo extraer o todos fallaron
        if self.logger:
            self.logger.error(f"No se pudo extraer texto de: {entrada[:100]}... "
                               "(ningún extractor compatible o todos fallaron)")
        return None






