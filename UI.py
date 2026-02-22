from colorama import init, Fore, Style
from tqdm import tqdm

init(autoreset=True)

def mostrar_intro():
    print(Fore.CYAN + Style.BRIGHT + "\n" + "="*44)
    print(Fore.CYAN + Style.BRIGHT + "  Conversor Texto a Voz  ".center(44,"="))
    print("="*44 + Style.RESET_ALL)
    print(
        f"{Fore.YELLOW}Bienvenido al Conversor Texto a Voz.\n"
        "Puedes ingresar:\n"
        f"{Fore.MAGENTA}- Un texto directo{Style.RESET_ALL}\n"
        f"{Fore.MAGENTA}- Una ruta de archivo de texto{Style.RESET_ALL}\n"
        f"{Fore.MAGENTA}- Una URL\n"
        f"{Fore.YELLOW}El programa extraerá el texto, lo procesará y te generará un archivo de audio de calidad natural. "
        "\n\n"
        "Para comenzar, simplemente introduce tus datos abajo.\n"
    )

def pedir_texto():
    print(Fore.GREEN + "\nPor favor, ingresa el texto, ruta de archivo o URL para convertir:")
    return input(Fore.WHITE + Style.NORMAL + "> ")

def mensaje_procesando():
    print(Fore.BLUE + "\nProcesando texto...\n")

def mostrar_progreso(iterable, desc="Progreso"):
    # Usa tqdm sobre el iterable real de tu pipeline (bloques, frases, etc)
    return tqdm(iterable, desc=desc, colour="magenta")

def resultado_final(ruta):
    print(Fore.GREEN + f"\n¡Audio generado exitosamente!")
    print(Fore.YELLOW + f"Archivo guardado en: {Fore.WHITE}{ruta}\n")

def mensaje_error(error):
    print(Fore.RED + f"Error: {error}")

def despedida():
    print(Fore.CYAN + Style.BRIGHT + "Gracias por usar el Conversor Texto a Voz. ¡Hasta pronto!\n")