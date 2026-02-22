from .conversor import ConvertidorTextoVoz
from .generador import GTTS, Pyttsx3
from .combinador import CombinadorAudio
from .nombre import NombreTemporal
from .expandir_tokens import ExpansionToken
from .exportador import Exportador
from .limpiador import LimpiadorArchivos
from tqdm import tqdm

class Gestionador:
    """
    Gestionador de la fase 3 del pipeline de conversión texto a voz.

    Intenta primero generar audio con gTTS. Si falla, usa pyttsx3 como fallback.
    Centraliza conversión, generación, combinación, exportación y limpieza.
    Muestra una barra de progreso con tqdm durante la generación de fragmentos.
    """
    def __init__(self, logger=None):
        """
        Inicializa el gestionador para la fase 3.
        
        Args:
            logger (object, optional): Logger para auditoría y debugging.
        """
        self.logger = logger
        self.convertidor = ConvertidorTextoVoz(logger)
        self.generadorGTTS = GTTS(logger)
        self.generadorPyttsx3 = Pyttsx3(logger)
        self.combinador = CombinadorAudio(logger)
        self.nombrador = NombreTemporal()
        self.expansion = ExpansionToken(logger)
        self.exportador = Exportador(logger)
        self.limpiador = LimpiadorArchivos(logger)

    def convertir(self, segmentos, nombre_final="audio_resultado", formato="mp3", mostrar_progreso=True):
        """
        Ejecuta el flujo completo de la fase 3.
        Muestra barra de progreso (tqdm) durante generación de audio.
        Primero intenta cada bloque con gTTS; si falla, usa pyttsx3 como fallback.

        Args:
            segmentos (list[dict] or list[list[dict]]): Lista de bloques/frases, cada uno con sus tokens enriquecidos.
            nombre_final (str): Nombre base del archivo final exportado (sin extensión).
            formato (str): Formato del archivo exportado ('mp3', 'wav', etc.).
            mostrar_progreso (bool): Si se muestra la barra de progreso durante la generación.

        Returns:
            str: Ruta del archivo de audio final generado.

        Raises:
            Exception: Si ocurre algún error durante el proceso principal.
        """
        try:
            archivos_generados = []

            # Si segmentos aún no está expandido, puedes hacerlo aquí y convertir cada uno en bloque
            lista_de_bloques = []
            for segmento in segmentos:
                tokens = self.convertidor.convertir([segmento])
                tokens_audio = self.expansion.expandir(tokens)
                if tokens_audio:
                    lista_de_bloques.append(tokens_audio)

            iterator = tqdm(lista_de_bloques, desc="Generando audio", unit="bloque") if mostrar_progreso else lista_de_bloques

            for bloque in iterator:
                resultado = None
                try:
                    resultado = self.generadorGTTS.generar(bloque, self.nombrador)
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Error generando audio gTTS para bloque. Error: {e}")
                if not resultado or not resultado[0][0]:
                    if self.logger:
                        self.logger.info("Usando fallback pyttsx3 para este bloque.")
                    try:
                        resultado = self.generadorPyttsx3.generar(bloque, self.nombrador)
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Error generando audio fallback pyttsx3 para bloque. Error: {e}")
                        resultado = [(None, None)]
                archivos_generados.extend(resultado)

            audio_final = self.combinador.combinar(archivos_generados)
            ruta_final = self.exportador.exportar(audio_final, nombre_final, formato)
            cantidad_eliminados = self.limpiador.limpiar(archivos_generados)
            if self.logger:
                self.logger.info(
                    f"Proceso completado. Exportado a {ruta_final}. {cantidad_eliminados} archivos temporales eliminados."
                )
            return ruta_final
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error en el proceso de conversión: {e}")
            raise