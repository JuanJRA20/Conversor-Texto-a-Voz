import logging
import time
import functools
import inspect
import sys
from logging.handlers import TimedRotatingFileHandler

class FiltradoNivel(logging.Filter):
    def __init__(self, bajo, alto):
        super().__init__()
        self.bajo = bajo
        self.alto = alto

    def filter(self, record):
        return self.bajo <= record.levelno <= self.alto


#Configuracion basica del logger
class Telemetriaindustrial:
    
    def __init__(self, nombre="Decoracion", tiempo=7):
    
        self.logger = logging.getLogger(nombre)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            self._configurar_handlers(tiempo)
        
    def _configurar_handlers(self, tiempo):
        #Formateador
        formateador = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')

        #Configuracion del primer handler
        Handler_1 = TimedRotatingFileHandler("Info.log", when="midnight", interval=1, backupCount=tiempo)
        Handler_1.setLevel(logging.INFO)
        Handler_1.addFilter(FiltradoNivel(logging.INFO, logging.INFO))
        Handler_1.setFormatter(formateador)

        #Configuracion del segundo handler (debug)
        Handler_2 = TimedRotatingFileHandler("Debug.log", when="midnight", interval=1, backupCount=tiempo)
        Handler_2.setLevel(logging.DEBUG)
        Handler_2.addFilter(FiltradoNivel(logging.DEBUG, logging.DEBUG))
        Handler_2.setFormatter(formateador)

        #Configuracion del tercer handler (warning)
        Handler_3 = TimedRotatingFileHandler("Warning.log", when="midnight", interval=1, backupCount=tiempo)
        Handler_3.setLevel(logging.WARNING)
        Handler_3.addFilter(FiltradoNivel(logging.WARNING, logging.WARNING))
        Handler_3.setFormatter(formateador)

        #Configuracion del cuarto handler (errores en consola)
        Handler_4 = logging.StreamHandler(sys.stderr)
        Handler_4.setLevel(logging.ERROR)
        Handler_4.setFormatter(formateador)

        self.logger.addHandler(Handler_1)
        self.logger.addHandler(Handler_2)
        self.logger.addHandler(Handler_3)
        self.logger.addHandler(Handler_4)

    @staticmethod
    def procesador_inteligente(data, limite_str=500):
        """
        Identifica el tipo de dato ANTES de procesar para evitar colapsos.
        """
        # CASO A: Objetos estructurados (Priorizamos Legibilidad)
        if isinstance(data, (list, dict, tuple)):
            longitud = len(data)
            if longitud > 100:
                return f"[{type(data).__name__}] Muy grande ({longitud} elementos). No procesado."
            
            # Si es manejable, usamos tu lógica de filtrado de negocio
            return Telemetriaindustrial._filtrado_negocio(data)

        # CASO B: Generadores (No queremos consumirlos)
        if inspect.isgenerator(data):
            return "<Generator object: contenido omitido para evitar consumo>"

        # CASO C: Strings o datos desconocidos (Priorizamos Seguridad)
        res_str = str(data)
        if len(res_str) > limite_str:
            return f"{res_str[:limite_str]}... [TRUNCADO: String masivo]"
        
        return res_str

    @staticmethod
    def _filtrado_negocio(data):
        if isinstance(data, list):
            return f"Lista(len={len(data)}): {data[:5]}..."
        if isinstance(data, dict):
            return f"Dict(len={len(data)}): Claves={list(data.keys())[:5]}..."
        return repr(data)
    
    # --- EL DECORADOR (LOGGER) ---
def logger_modular(log):
    def decorador(funcion):
        @functools.wraps(funcion)  # Conservamos la metadata de la funcion original
        def decoracion(*args, **kwargs):

            if funcion.__name__ == "main":
                print("Iniciando programa...")

            if log.isEnabledFor(logging.DEBUG):
                args_seguros = Telemetriaindustrial.procesador_inteligente(args)
                log.debug(f"Iniciando: {funcion.__name__} | Args: {args_seguros}")
            tiempo_inicial = time.perf_counter()  # Tiempo inicial
            
            try:
                resultado = funcion(*args, **kwargs)
                tiempo_final = time.perf_counter() # Tiempo final
                tiempo=tiempo_final-tiempo_inicial
                # 2. LAZY LOGGING: Solo procesamos si el nivel INFO está activo
                if log.isEnabledFor(logging.INFO):
                    # Aplicamos el procesado inteligente (Doble Vía)
                    data_final = Telemetriaindustrial.procesador_inteligente(resultado)
                    log.info(f"✅ {funcion.__name__} | {tiempo:.4f}s | Data: {data_final}")
                return resultado
            except Exception as e:
                log.error(f"❌ Error en {funcion.__name__}: {str(e)}", exc_info=True)
                raise e
        return decoracion
    return decorador


























