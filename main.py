"""
Archivo python donde se crea el codigo que combina las tres etapas del proyecto:
1. Extraccion y validacion de texto
2. procesado de datos
3. Conversion de texto a audio

Utiliza el logger personalizado para registrar eventos importantes durante el proceso.
"""

# Importacion de librerias necesarias:
from extraccion_validacion.tipo_datos import ClasificadorTipoEntrada
from extraccion_validacion.extraccion_datos import GestorExtractores
from extraccion_validacion.validacion_datos import GestorValidadores

from procesado_datos.procesar_texto import ObtenerTokens, MarcarSilencios
from procesado_datos.limpieza_texto import LimpiarPalabras
from procesado_datos.detectar_idioma import GestorDetectorIdioma

from Convetir_Texto_Audio import ConvertidorTextoVoz
from Logger import Telemetriaindustrial, logger_modular

# Configuracion del logger personalizado
logger = Telemetriaindustrial("Main_Proceso_Texto_Voz").logger


#funcion que combina la extraccion y validacion de texto, utilizando el logger para registrar eventos importantes y errores.
def extraccion_y_validacion(texto):

    clarificador = ClasificadorTipoEntrada(logger=logger)
    extractor = GestorExtractores(logger=logger)
    validador = GestorValidadores(logger=logger)
    
    try: #bucle try-except para manejar errores al determinar el tipo de entrada

        #Determinar tipo de entrada
        tipo, entrada = clarificador.determinar_tipo(texto) #determina el tipo de entrada (texto plano, archivo o URL) y su valor asociado

        if tipo is None:
            logger.error("No se pudo determinar el tipo de entrada: %s", texto[:50])
            return None
        
        logger.info("Tipo de entrada detectado: %s", tipo)
        
        # 2. Validar entrada según tipo
        if not validador.validar_por_tipo(entrada, tipo):
            logger.warning("Validación fallida para %s: %s", tipo, entrada[:50])
            return None
        logger.info("Entrada validada exitosamente")

        # 3. Extraer contenido
        contenido = extractor.extraer(entrada)
        
        if contenido:
            logger.info("Extracción exitosa, contenido obtenido: %d caracteres", len(contenido))
            return contenido
        else:
            logger.error("Extracción falló, no se obtuvo contenido")
            return None
        
    except Exception as e:
        logger.error("Error en extracción y validación: %s", e, exc_info=True)
        return None

#Procesado de datos
def procesado_datos(contenido):
    try:
        # 1. Segmentar en oraciones y tokens
        tokenizer = ObtenerTokens(logger=logger)
        segmentos = tokenizer.procesar(contenido)

        # 2. Limpiar tokens
        limpiador = LimpiarPalabras(logger=logger)
        segmentos_limpios = limpiador.limpiar(segmentos)

        # 3. Marcar silencios
        marcador_silencios = MarcarSilencios(logger=logger)
        segmentos_silencio = marcador_silencios.procesar(segmentos_limpios)

        # 4. Detectar idioma
        detector = GestorDetectorIdioma(logger=logger)
        resultado = detector.detectar_segmentos(segmentos_silencio)

        logger.info("Datos procesados exitosamente. Total líneas: %d", len(resultado))
        return resultado

    except Exception as e:
        logger.error("Error procesando datos: %s", e, exc_info=True)
        return None

#Conversion de texto a audio
def conversion_texto_audio(datos_procesados):
    try: #bucle try-except para manejar errores durante la conversión de texto a audio, registrando eventos importantes y errores en el logger.

        #aplana la lista de listas de tokens generada por el procesamiento de datos en una sola lista de tokens, que luego se pasa a la función 
        #de conversión de texto a voz. Si la conversión es exitosa, se registra el nombre del archivo de audio generado en el logger. 
        #Si no se genera ningún audio, se registra una advertencia.
        print("Iniciando conversion de texto a audio...")
        tokens = [token for linea in datos_procesados for token in linea['tokens_idioma']] 
        tokens_texto = [token['token'] for token in tokens]
        salida = ConvertidorTextoVoz.convertir_texto_voz(tokens_texto)
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
