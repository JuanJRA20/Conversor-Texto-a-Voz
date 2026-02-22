# Importacion de librerias necesarias:
from extraccion_validacion.tipo_datos import ClasificadorTipoEntrada
from extraccion_validacion.extraccion_datos import GestorExtractores
from extraccion_validacion.validacion_datos import GestorValidadores

class Gestionador:
    """
    Gestionador de la fase 1 del pipeline de conversión texto a voz.

    Encapsula todo el proceso de extracción y validación de texto, utilizando un logger personalizado para registrar eventos importantes y errores.
    """
    def __init__(self, logger=None):
        """
        Inicializa el gestionador para la fase 1.
        
        Args:
            logger (object, optional): Logger para auditoría y debugging.
        """
        self.logger = logger
        self.clarificador = ClasificadorTipoEntrada(logger=logger)
        self.extractor = GestorExtractores(logger=logger)
        self.validador = GestorValidadores(logger=logger)

#funcion que combina la extraccion y validacion de texto, utilizando el logger para registrar eventos importantes y errores.
    def extraccion_y_validacion(self, texto):

        
        try: #bucle try-except para manejar errores al determinar el tipo de entrada

            #Determinar tipo de entrada
            tipo, entrada = self.clarificador.determinar_tipo(texto) #determina el tipo de entrada (texto plano, archivo o URL) y su valor asociado

            if tipo is None:
                self.logger.error("No se pudo determinar el tipo de entrada: %s", texto[:50])
                return None
            
            self.logger.info("Tipo de entrada detectado: %s", tipo)
            
            # 2. Validar entrada según tipo
            if not self.validador.validar_por_tipo(entrada, tipo):
                self.logger.warning("Validación fallida para %s: %s", tipo, entrada[:50])
                return None
            self.logger.info("Entrada validada exitosamente")

            # 3. Extraer contenido
            contenido = self.extractor.extraer(entrada)
            
            if contenido:
                self.logger.info("Extracción exitosa, contenido obtenido: %d caracteres", len(contenido))
                return contenido
            else:
                self.logger.error("Extracción falló, no se obtuvo contenido")
                return None
            
        except Exception as e:
            self.logger.error("Error en extracción y validación: %s", e, exc_info=True)
            return None