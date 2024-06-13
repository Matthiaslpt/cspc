# Cours hippique
# Version avec tableau partagé et arbitre

# Quelques codes d'échappement (tous ne sont pas utilisés)
CLEARSCR = "\x1B[2J\x1B[;H"  # Clear SCReen
CLEAREOS = "\x1B[J"  # Clear End Of Screen
CLEARELN = "\x1B[2K"  # Clear Entire LiNe
CLEARCUP = "\x1B[1J"  # Clear Curseur UP
GOTOYX = "\x1B[%.2d;%.2dH"  # ('H' ou 'f') : Goto at (y,x), voir le code

DELAFCURSOR = "\x1B[K"  # effacer après la position du curseur
CRLF = "\r\n"  # Retour à la ligne

# VT100 : Actions sur le curseur
CURSON = "\x1B[?25h"  # Curseur visible
CURSOFF = "\x1B[?25l"  # Curseur invisible

# VT100 : Actions sur les caractères affichables
NORMAL = "\x1B[0m"  # Normal
BOLD = "\x1B[1m"  # Gras
UNDERLINE = "\x1B[4m"  # Souligné

# VT100 : Couleurs : "22" pour normal intensity
CL_BLACK = "\033[22;30m"  # Noir. NE PAS UTILISER. On verra rien !!
CL_RED = "\033[22;31m"  # Rouge
CL_GREEN = "\033[22;32m"  # Vert
CL_BROWN = "\033[22;33m"  # Brun
CL_BLUE = "\033[22;34m"  # Bleu
CL_MAGENTA = "\033[22;35m"  # Magenta
CL_CYAN = "\033[22;36m"  # Cyan
CL_GRAY = "\033[22;37m"  # Gris

# "01" pour quoi ? (bold ?)
CL_DARKGRAY = "\033[01;30m"  # Gris foncé
CL_LIGHTRED = "\033[01;31m"  # Rouge clair
CL_LIGHTGREEN = "\033[01;32m"  # Vert clair
CL_YELLOW = "\033[01;33m"  # Jaune
CL_LIGHTBLU = "\033[01;34m"  # Bleu clair
CL_LIGHTMAGENTA = "\033[01;35m"  # Magenta clair
CL_LIGHTCYAN = "\033[01;36m"  # Cyan clair
CL_WHITE = "\033[01;37m"  # Blanc

# -------------------------------------------------------
import multiprocessing as mp
import os, time, random, ctypes, signal

# Une liste de couleurs à affecter aléatoirement aux chevaux
lyst_colors = [CL_WHITE, CL_RED, CL_GREEN, CL_BROWN, CL_BLUE, CL_MAGENTA, CL_CYAN, CL_GRAY,
               CL_DARKGRAY, CL_LIGHTRED, CL_LIGHTGREEN, CL_LIGHTBLU, CL_YELLOW, CL_LIGHTMAGENTA, CL_LIGHTCYAN]

def effacer_ecran(): print(CLEARSCR, end='')
def erase_line_from_beg_to_curs(): print("\033[1K", end='')
def curseur_invisible(): print(CURSOFF, end='')
def curseur_visible(): print(CURSON, end='')
def move_to(lig, col): print("\033[" + str(lig) + ";" + str(col) + "f", end='')

def en_couleur(Coul): print(Coul, end='')
def en_rouge(): print(CL_RED, end='')  # Un exemple !
def erase_line(): print(CLEARELN, end='')

# La tâche d'un cheval
def un_cheval(ma_ligne: int, positions, keep_running, lock, longueur_course):  # ma_ligne commence à 0
    col = 1

    while col < longueur_course and keep_running.value:
        with lock:
            effacer_cheval(ma_ligne, col - 1)
            dessiner_cheval(ma_ligne, col)

        col += 1
        positions[ma_ligne] = col
        time.sleep(0.1 * random.randint(1, 5))

    # Le premier arrivé gèle la course !
    keep_running.value = False

def dessiner_cheval(ma_ligne, col):
    cheval = [
        "__________\\/",
        " /−−−− _.\\",
        " /|_____/ ",
        "  /\\ /\\  "
    ]
    for i, ligne in enumerate(cheval):
        move_to(ma_ligne * 5 + i + 1, col)
        print(ligne)

def effacer_cheval(ma_ligne, col):
    cheval = [
        "           ",
        "           ",
        "           ",
        "           "
    ]
    for i, ligne in enumerate(cheval):
        move_to(ma_ligne * 5 + i + 1, col)
        print(ligne)

def arbitre(positions, keep_running, lock, prediction, nb_process):
    while keep_running.value:
        time.sleep(1)
        with lock:
            leader = max(positions)
            last = min(positions)
            leader_horses = [i for i, pos in enumerate(positions) if pos == leader]
            last_horses = [i for i, pos in enumerate(positions) if pos == last]
            move_to(nb_process * 5 + 1, 1)
            erase_line_from_beg_to_curs()
            print("Leader:", ' '.join([chr(ord('A') + h) for h in leader_horses]))
            move_to(nb_process * 5 + 2, 1)
            erase_line_from_beg_to_curs()
            print("Last:", ' '.join([chr(ord('A') + h) for h in last_horses]))
    with lock:
        winner = [i for i, pos in enumerate(positions) if pos == max(positions)]
        move_to(nb_process * 5 + 3, 1)
        erase_line_from_beg_to_curs()
        if prediction in winner:
            print(f"Course terminée. Gagnant: {chr(ord('A') + winner[0])}. Votre prédiction était correcte!")
        else:
            print(f"Course terminée. Gagnant: {chr(ord('A') + winner[0])}. Votre prédiction était incorrecte.")

def detourner_signal(signum, stack_frame):
    move_to(Nb_process * 5 + 5, 1)
    erase_line_from_beg_to_curs()
    move_to(Nb_process * 5 + 5, 1)
    curseur_visible()
    print("La course est interrompue ...")
    exit(0)

# ---------------------------------------------------
# La partie principale :

if __name__ == "__main__":
    import platform
    if platform.system() == "Darwin":
        mp.set_start_method('fork')  # Nécessaire sous macos, OK pour Linux

    LONGEUR_COURSE = 50
    Nb_process = 20
    positions = mp.Array('i', [0] * Nb_process)
    keep_running = mp.Value(ctypes.c_bool, True)
    lock = mp.Lock()

    effacer_ecran()
    curseur_invisible()

    signal.signal(signal.SIGINT, detourner_signal)

    prediction = input("Prédisez le gagnant (A à T) : ").upper()
    while prediction not in [chr(ord('A') + i) for i in range(Nb_process)]:
        prediction = input("Prédiction invalide. Prédisez le gagnant (A à T) : ").upper()

    prediction = ord(prediction) - ord('A')

    mes_process = [mp.Process(target=un_cheval, args=(i, positions, keep_running, lock, LONGEUR_COURSE)) for i in range(Nb_process)]
    arbitre_process = mp.Process(target=arbitre, args=(positions, keep_running, lock, prediction, Nb_process))

    for p in mes_process:
        p.start()
    arbitre_process.start()

    for p in mes_process:
        p.join()
    arbitre_process.join()

    move_to(Nb_process * 5 + 5, 1)
    curseur_visible()
    print("Fini ...", flush=True)
