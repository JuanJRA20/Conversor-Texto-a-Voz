#Importacion de las librerias necesarias:

#Librerias internas de python
import re

# Método estático para limpiar una lista de palabras, detectando tokens protegidos por comillas
    # o paréntesis, y clasificando tokens de puntuación.
@staticmethod
def limpiar_palabras(palabras):

    # Manejo de casos donde la entrada no es una lista para evitar errores en el procesamiento de palabras.
    if not isinstance(palabras, list):
        return []
    
    resultado = [] #lista para almacenar los tokens limpios y su tipo, que se devuelve al final del método.

    i = 0 # Variable de índice para iterar sobre la lista de palabras

    # patron regex para validar palabras
    patron = re.compile(r"[A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ_\+\#\-']+") 

    # Bucle para iterar sobre la lista de palabras, aplicando reglas para detectar tokens protegidos por comillas o paréntesis,
    while i < len(palabras): 
        token = palabras[i]

        # Caso en que el token este protegido por comillas normales, simples o parentesis
        if (token.startswith('"') and token.endswith('"') and len(token) > 2) or (token.startswith("'") and token.endswith("'") and len(token) > 2) or (token.startswith('(') and token.endswith(')') and len(token) > 2):
            palabra = token[1:-1]
            if patron.fullmatch(palabra): # Si el token interno es una palabra válida según el patrón, se marca como protegido
                # Normalizar a un único tipo independiente del delimitador
                resultado.append((palabra, 'palabra_protegida'))
                i += 1
                continue

        # Caso en que el token sea el inicio de un token protegido por comillas o paréntesis, pero el cierre no esté pegado al token de apertura
        # siendo el token mas de una palabra
        if token == '(' or token in ('"', "'") or token.startswith('(') or token.startswith('"') or token.startswith("'"):
            # determinar delimitadores (unificado para paréntesis y comillas)
            QUOTE_PAIRS = {'"': '"', "'": "'", '“': '”', '‘': '’', '«': '»'}
            if token.startswith('(') or token == '(':
                apertura = '('
                cierre = ')'
            else:
                apertura = token[0]
                cierre = QUOTE_PAIRS.get(apertura, apertura)

            # preparar lista inner; si el token contiene la parte inicial (p.ej. '"Vox') incluirla
            palabras_internas = []
            primer_segmento = token #cargamos el token completo inicialmente

            # si el token empieza con el delimitador de apertura pero no termina con el de cierre,
            # se considera que es un token protegido que comienza en este punto, y se prepara para buscar el cierre en los tokens siguientes.
            if token.startswith(apertura) and not token.endswith(cierre):
                # token con apertura pegada: añadir el resto sin la apertura
                primer_segmento = token.lstrip(apertura)

                if primer_segmento: # Si el segmento después de quitar el delimitador de apertura no está vacío, se añade a la lista de palabras internas.
                    palabras_internas.append(primer_segmento)

            j = i + 1 # Variable de índice para buscar el cierre del token protegido en los tokens siguientes
            cierre_encontrado = False # Variable para indicar si se ha encontrado el cierre del token protegido

            #bucle para buscar el cierre del token protegido en los tokens siguientes
            while j < len(palabras):
                palabra = palabras[j]

                # si este token es igual al cierre o termina con el cierre
                if palabra == cierre or palabra.endswith(cierre):
                    # limpiamos el token de cierre y lo añadimos a la lista de palabras internas si no queda vacío
                    palabra_limpia = re.sub(r"[\"'\(\)\[\]\{\}]+$", "", palabra)

                    if palabra_limpia: # Si el token después de quitar el delimitador de cierre no está vacío, se añade a la lista de palabras internas.
                        palabras_internas.append(palabra_limpia)
                    cierre_encontrado = True # Se marca que se ha encontrado el cierre del token protegido y se sale del bucle de búsqueda.
                    break

                else: # Si el token no es el cierre, se añade a la lista de palabras internas para seguir construyendo el contenido del token protegido.
                    palabras_internas.append(palabra)
                j += 1

            # si no se consigue el cierre, se pasa y se sigue con el flujo normal
            if not cierre_encontrado:
                pass

            # si se encuentra el cierre, se procesa el contenido interno para determinar si es un token protegido
            # válido o no, aplicando reglas de limpieza y validación de palabras internas.
            else:
                # normalizar inner y contar palabras válidas
                token_limpio = [re.sub(r"^[\"'\(\)\[\]\{\}]+|[\"'\(\)\[\]\{\}]+$", "", palabra) for palabra in palabras_internas]
                palabras_internas = [palabra for palabra in token_limpio if patron.fullmatch(palabra)]

                # Si hay más de 2 palabras internas válidas, se considera un token protegido multi-palabra, y se marca como 
                # 'palabras_protegidas' con el contenido interno unido, manteniendo los delimitadores de apertura y 
                # cierre como marcadores de este token protegido.
                if len(palabras_internas) > 2:
                    # Normalizar múltiples palabras protegidas a un único tipo
                    resultado.append((apertura, 'puntuacion'))
                    resultado.append((" ".join(palabras_internas), 'palabras_protegidas'))
                    resultado.append((cierre, 'puntuacion'))
                    i = j + 1
                    continue
                
                # si hay exactamente 1 palabra interna válida, se considera un token protegido single-word, y se marca como 
                # 'palabra_protegida' con el contenido interno, manteniendo los delimitadores de apertura y cierre como 
                # marcadores de este token protegido.
                if len(palabras_internas) == 1:
                    # Unificar single protected word a 'palabra_protegida'
                    resultado.append((apertura, 'puntuacion'))
                    resultado.append((palabras_internas[0], 'palabra_protegida'))
                    resultado.append((cierre, 'puntuacion'))
                    i = j + 1
                    continue
            # si no encaja, dejar que el flujo normal trate el token

        # conservar tokens de puntuación como marcadores (incluye paréntesis y comillas sueltas)
        if re.fullmatch(r"[\.,;:()\[\]{}'\"]+", token):
            resultado.append((token, 'puntuacion'))
            i += 1
            continue

        # limpiar comillas/paren al inicio/fin
        limpio = re.sub(r"^[\"'\(\)\[\]\{\}]+|[\"'\(\)\[\]\{\}]+$", "", token)
        if not patron.fullmatch(limpio):
            i += 1
            continue

        # separar puntuación final pegada al token
        signo = re.match(r"^(?P<word>[A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ_\+\#\-']+)(?P<punct>[\.,;:]+)$", limpio)
        if signo:
            resultado.append((signo.group('word'), 'palabra'))
            resultado.append((signo.group('punct'), 'puntuacion'))
        else:
            resultado.append((limpio, 'palabra'))
        i += 1

    return resultado

