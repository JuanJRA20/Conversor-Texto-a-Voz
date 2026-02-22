from conversor import ConvertidorTextoVoz
from generador import Generador
from combinador import CombinadorAudio
from nombre import NombreTemporal
from expandir_tokens import ExpansionToken
from exportador import Exportador
from limpiador import LimpiadorArchivos
from tqdm import tqdm

class Gestionador:
    """
    Gestionador de la fase 3 del pipeline de conversión texto a voz.

    Encapsula todo el proceso: conversión, generación de audio, combinación, exportación y limpieza.
    Muestra una barra de progreso (tqdm) durante la generación de fragmentos de audio.
    """
    def __init__(self, logger=None):
        """
        Inicializa el gestionador para la fase 3.
        
        Args:
            logger (object, optional): Logger para auditoría y debugging.
        """
        self.logger = logger
        self.convertidor = ConvertidorTextoVoz(logger)
        self.generador = Generador(logger)
        self.combinador = CombinadorAudio(logger)
        self.nombrador = NombreTemporal()
        self.expansion = ExpansionToken(logger)
        self.exportador = Exportador(logger)
        self.limpiador = LimpiadorArchivos(logger)

    def convertir(self, segmentos, nombre_final="audio_resultado", formato="mp3", mostrar_progreso=True):
        """
        Ejecuta el flujo completo de la fase 3.
        Presenta barra de progreso (tqdm) durante la generación de fragmentos de audio.

        Args:
            segmentos (list[dict]): Lista de segmentos lingüísticos enriquecidos.
            nombre_final (str): Nombre base del archivo final exportado (sin extensión).
            formato (str): Formato del archivo exportado ('mp3', 'wav', etc.).
            mostrar_progreso (bool): Si se muestra la barra de progreso durante la generación.

        Returns:
            str: Ruta del archivo de audio final generado.

        Raises:
            Exception: Si ocurre algún error durante el proceso.
        """
        try:
            tokens = self.convertidor.convertir(segmentos)
            tokens_audio = self.expansion.expandir(tokens)

            # Barra de progreso durante la generación de fragmentos
            archivos_generados = []
            gen_entries = tokens_audio
            iterator = tqdm(gen_entries, desc="Generando fragmentos de audio",
                             unit="fragmento") if mostrar_progreso else gen_entries
            for token_data in iterator:
                # Aquí llamamos al generador para cada fragmento individualmente
                resultado = self.generador.generar([token_data], self.nombrador)
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