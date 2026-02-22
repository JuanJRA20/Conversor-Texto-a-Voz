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
        Primero intenta cada fragmento con gTTS; si falla, usa pyttsx3 como fallback.

        Args:
            segmentos (list[dict]): Lista de segmentos lingüísticos enriquecidos.
            nombre_final (str): Nombre base del archivo final exportado (sin extensión).
            formato (str): Formato del archivo exportado ('mp3', 'wav', etc.).
            mostrar_progreso (bool): Si se muestra la barra de progreso durante la generación.

        Returns:
            str: Ruta del archivo de audio final generado.

        Raises:
            Exception: Si ocurre algún error durante el proceso principal.
        """
        try:
            # Conversión y expansión de tokens
            tokens = self.convertidor.convertir(segmentos)
            tokens_audio = self.expansion.expandir(tokens)

            # Barra de progreso
            archivos_generados = []
            iterator = tqdm(tokens_audio, desc="Generando fragmentos de audio",
                             unit="fragmento") if mostrar_progreso else tokens_audio
            for token_data in iterator:
                resultado = None
                # Intentar con el motor principal (gTTS)
                try:
                    resultado = self.generadorGTTS.generar([token_data], self.nombrador)
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Error generando audio gTTS para token: {token_data}. Error: {e}")
                # Si falla o no se genera audio, usar fallback (pyttsx3)
                if not resultado or not resultado[0][0]:
                    if self.logger:
                        self.logger.info(f"Usando fallback pyttsx3 para token: {token_data}")
                    try:
                        resultado = self.generadorPyttsx3.generar([token_data], self.nombrador)
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Error generando audio fallback pyttsx3 para token: {token_data}. Error: {e}")
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