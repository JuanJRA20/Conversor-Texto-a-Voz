"""
Archivo python donde se crea el codigo que combina las tres etapas del proyecto:
1. Extraccion y validacion de texto
2. procesado de datos
3. Conversion de texto a audio

Utiliza el logger personalizado para registrar eventos importantes durante el proceso.
"""

# Importacion de librerias necesarias:

from Extraccion_datos import TipoEntrada, ExtraccionDatos, ValidadorDatos
from Procesado_datos import ProcesadoDatos
from Convetir_Texto_Audio import ConvertidorTextoVoz
from Logger import Telemetriaindustrial, logger_modular

# Configuracion del logger personalizado
logger = Telemetriaindustrial("Main_Proceso_Texto_Voz").logger

#funcion que combina la extraccion y validacion de texto, utilizando el logger para registrar eventos importantes y errores.
def extraccion_y_validacion(texto):

    try: #bucle try-except para manejar errores al determinar el tipo de entrada
        tipo, valor = TipoEntrada.determinar_tipo(texto) #determina el tipo de entrada (texto plano, archivo o URL) y su valor asociado

    except Exception as e: #maneja cualquier excepción que ocurra durante la determinación del tipo de entrada y registra el error en el logger
        logger.error("Error determinando tipo de entrada: %s", e)
        return None

    #Diccionario que mapea cada tipo de entrada a su correspondiente función de validación y extracción,
    #permitiendo un manejo más limpio y organizado de las diferentes formas de entrada. Si el tipo de entrada no es reconocido,
    #se registra una advertencia en el logger.
    handlers = {
        'Textoplano': (ValidadorDatos.texto, ExtraccionDatos.textoplano),
        'Archivo': (ValidadorDatos.archivo, ExtraccionDatos.archivo),
        'URL': (ValidadorDatos.url, ExtraccionDatos.url),
    }

    #Obtiene la función de validación y extracción correspondiente al tipo de entrada. Si el tipo no es procesable, se registra una advertencia.
    validator_extractor = handlers.get(tipo) 
    if not validator_extractor:
        logger.warning("Tipo de entrada no procesable: %s", tipo)
        return None

    #Ejecuta la función de validación y extracción correspondiente, manejando cualquier excepción que pueda ocurrir durante este proceso
    #y registrando los eventos en el logger.
    validator, extractor = validator_extractor
    try: #bucle try-except para manejar errores durante la validación y extracción de datos, registrando eventos importantes y errores en el logger.

        if validator(valor): #si la validacion es exitosa, se registra la entrada validada en el logger y se procede a extraer los datos utilizando la función correspondiente.
            logger.info("Entrada validada: %s", tipo)
            return extractor(valor)
        
        #si la validación falla, se registra una advertencia en el logger indicando que la entrada no es válida según el validador.
        logger.warning("Entrada no válida según el validador: %s", tipo) 

    except Exception as e: #maneja cualquier excepción que ocurra durante la validación y extracción de datos, registrando el error en el logger.
        logger.error("Error en validación/extracción: %s", e)
    return None

#Procesado de datos
def procesado_datos(datos):
    try: #bucle try-except para manejar errores durante el procesamiento de datos, registrando eventos importantes y errores en el logger.
        Procesado = ProcesadoDatos.procesar_texto(datos) #procesa los datos utilizando la función de procesamiento de texto
        logger.info("Datos procesados")
        return Procesado
    
    except Exception as e: #maneja cualquier excepción que ocurra durante el procesamiento de datos, registrando el error en el logger.
        logger.error("Error procesando datos: %s", e)
        return None

#Conversion de texto a audio
def conversion_texto_audio(datos_procesados):
    try: #bucle try-except para manejar errores durante la conversión de texto a audio, registrando eventos importantes y errores en el logger.

        #aplana la lista de listas de tokens generada por el procesamiento de datos en una sola lista de tokens, que luego se pasa a la función 
        #de conversión de texto a voz. Si la conversión es exitosa, se registra el nombre del archivo de audio generado en el logger. 
        #Si no se genera ningún audio, se registra una advertencia.
        print("Iniciando conversion de texto a audio...")
        tokens = [t for linea in datos_procesados for t in linea] 
        salida = ConvertidorTextoVoz.convertir_texto_voz(tokens)
        if salida:
            logger.info("Audio generado: %s", salida)
            print(f"Conversion finalizada. Archivo listo: {salida}")
            return salida
        logger.warning("No se generó audio del texto procesado")

    except Exception as e: #maneja cualquier excepción que ocurra durante la conversión de texto a audio, registrando el error en el logger.
        logger.error("Error generando audio: %s", e)
    return None

#Funcion principal que combina las tres etapas del proyecto.
@logger_modular(logger)
def main():
    #Solicita al usuario que ingrese un texto, ruta de archivo o URL para convertir a audio.
    texto = input("Ingrese texto, ruta de archivo o URL a convertir: \n")

    #Llama a la función de extracción y validación de texto, pasando el texto ingresado por el usuario. 
    #Si la función devuelve None, se indica que la entrada no es procesable
    datos = extraccion_y_validacion(texto)
    if not datos:
        print("Entrada no procesable. Revisa los logs para más detalles.")
        return
    
    #Llama a la función de procesamiento de datos, pasando los datos extraídos y validados. 
    #Si la función devuelve None, se indica que hubo un error en el procesamiento
    procesado = procesado_datos(datos)
    if not procesado:
        print("Error en el procesado. Revisa los logs.")
        return
    
    #Llama a la función de conversión de texto a audio, pasando los datos procesados. 
    #Si la función devuelve None, se indica que no se generó ningún archivo de audio
    salida = conversion_texto_audio(procesado)
    if not salida:
        #si no se generó ningún archivo de audio, se muestra un mensaje al usuario indicando que no se generó ningún archivo de audio.
        print("No se generó ningún archivo de audio.") 

if __name__ == "__main__":
    main()
