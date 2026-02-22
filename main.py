"""
Archivo python donde se crea el codigo que combina las tres etapas del proyecto:
1. Extraccion y validacion de texto
2. procesado de datos
3. Conversion de texto a audio

Utiliza el logger personalizado para registrar eventos importantes durante el proceso.
"""
from UI import (mostrar_intro, pedir_texto, mensaje_procesando, mostrar_progreso,
                resultado_final, mensaje_error, despedida)
from extraccion_validacion.gestionador import Gestionador as GestionadorExtraccion
from procesado_datos.gestionador import Gestionador as GestionadorProcesado
from convertor_audio.gestionador import Gestionador as GestionadorAudio
from Logger import Telemetriaindustrial, logger_modular

# Configuracion del logger personalizado
logger = Telemetriaindustrial("Main_Proceso_Texto_Voz").logger

gestionador_extraccion = GestionadorExtraccion(logger=logger)
gestionador_procesado = GestionadorProcesado(logger=logger)
gestionador_audio = GestionadorAudio(logger=logger)

#Funcion principal que combina las tres etapas del proyecto.
@logger_modular(logger)
def main():
    mostrar_intro()
    texto = pedir_texto()

    print("Extrayendo y validando texto...")
    datos = gestionador_extraccion.extraccion_y_validacion(texto)
    if not datos:
        mensaje_error("Entrada no procesable. Revisa los logs para más detalles.")
        despedida()
        return

    mensaje_procesando()
    procesado = gestionador_procesado.procesado_datos(datos)
    if not procesado:
        mensaje_error("Error en el procesado. Revisa los logs.")
        despedida()
        return

    # Muestra la barra de progreso sobre el iterable real: puedes adaptar esta parte
    print("Generando audio (esto puede tardar unos segundos)...")
    salida = gestionador_audio.convertir(procesado, mostrar_progreso=True)
    if not salida:
        mensaje_error("No se generó ningún archivo de audio.")
        despedida()
        return

    resultado_final(salida)
    despedida()

if __name__ == "__main__":
    main()