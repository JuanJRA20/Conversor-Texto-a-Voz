from procesado_datos.procesar_texto import ObtenerTokens, MarcarSilencios, AgruparProtegidos
from procesado_datos.limpieza_texto import LimpiarPalabras
from procesado_datos.detectar_idioma import GestorDetectorIdioma

class Gestionador:
    """
    Gestionador de la fase 2 del pipeline de conversión texto a voz.

    Encapsula todo el proceso de procesamiento de datos, utilizando un logger personalizado para registrar eventos importantes y errores.
    """
    def __init__(self, logger=None):
        """
        Inicializa el gestionador para la fase 2.
        
        Args:
            logger (object, optional): Logger para auditoría y debugging.
        """
        self.logger = logger
        self.tokenizer = ObtenerTokens(logger=logger)
        self.limpiador = LimpiarPalabras(logger=logger)
        self.marcador_silencios = MarcarSilencios(logger=logger)
        self.agrupador_protegidos = AgruparProtegidos(logger=logger)
        self.detector_idioma = GestorDetectorIdioma(logger=logger)

    #Procesado de datos
    def procesado_datos(self, contenido):
        try:
            # 1. Segmentar en oraciones y tokens
            tokenizer = ObtenerTokens(logger=self.logger)
            segmentos = tokenizer.procesar(contenido)

            # 2. Limpiar tokens
            limpiador = LimpiarPalabras(logger=self.logger)
            segmentos_limpios = limpiador.limpiar(segmentos)

            # 3. Marcar silencios
            marcador_silencios = MarcarSilencios(logger=self.logger)
            segmentos_silencio = marcador_silencios.procesar(segmentos_limpios)

            #4. Agrupar protegidos
            agrupador_protegidos = AgruparProtegidos(logger=self.logger)
            segmentos_agrupados = agrupador_protegidos.procesar(segmentos_silencio)

            # 5. Detectar idioma
            detector = GestorDetectorIdioma(logger=self.logger)
            resultado = detector.detectar(segmentos_agrupados)

            self.logger.info("Datos procesados exitosamente. Total líneas: %d", len(resultado))
            return resultado

        except Exception as e:
            self.logger.error("Error procesando datos: %s", e, exc_info=True)
            return None
