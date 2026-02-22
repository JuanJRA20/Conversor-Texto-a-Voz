"""
Archivo python donde se crea el codigo que combina las tres etapas del proyecto:
1. Extraccion y validacion de texto
2. procesado de datos
3. Conversion de texto a audio

Utiliza el logger personalizado para registrar eventos importantes durante el proceso.
"""

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
    #Solicita al usuario que ingrese un texto, ruta de archivo o URL para convertir a audio.
    texto = input("Ingrese texto, ruta de archivo o URL a convertir: \n")

    #Llama a la función de extracción y validación de texto, pasando el texto ingresado por el usuario. 
    #Si la función devuelve None, se indica que la entrada no es procesable
    datos = gestionador_extraccion.extraccion_y_validacion(texto)
    if not datos:
        print("Entrada no procesable. Revisa los logs para más detalles.")
        return
    
    #Llama a la función de procesamiento de datos, pasando los datos extraídos y validados. 
    #Si la función devuelve None, se indica que hubo un error en el procesamiento
    procesado = gestionador_procesado.procesado_datos(datos)
    if not procesado:
        print("Error en el procesado. Revisa los logs.")
        return
    
    #Llama a la función de conversión de texto a audio, pasando los datos procesados. 
    #Si la función devuelve None, se indica que no se generó ningún archivo de audio
    salida = gestionador_audio.convertir(procesado)
    if not salida:
        #si no se generó ningún archivo de audio, se muestra un mensaje al usuario indicando que no se generó ningún archivo de audio.
        print("No se generó ningún archivo de audio.") 

if __name__ == "__main__":
    main()
