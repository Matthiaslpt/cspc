# Cours hippique
# Version très basique, sans mutex sur l'écran, sans arbitre, sans annoncer le gagnant, ...

# Quelques codes d'échappement (tous ne sont pas utilisés)
CLEARSCR="\x1B[2J\x1B[;H"          #  Clear SCReen
CLEAREOS = "\x1B[J"                #  Clear End Of Screen
CLEARELN = "\x1B[2K"               #  Clear Entire LiNe
CLEARCUP = "\x1B[1J"               #  Clear Curseur UP
GOTOYX   = "\x1B[%.2d;%.2dH"       #  ('H' ou 'f') : Goto at (y,x), voir le code

DELAFCURSOR = "\x1B[K"             #  Effacer après la position du curseur
CRLF  = "\r\n"                     #  Retour à la ligne

# VT100 : Actions sur le curseur
CURSON   = "\x1B[?25h"             #  Curseur visible
CURSOFF  = "\x1B[?25l"             #  Curseur invisible

# VT100 : Actions sur les caractères affichables
NORMAL = "\x1B[0m"                  #  Normal
BOLD = "\x1B[1m"                    #  Gras
UNDERLINE = "\x1B[4m"               #  Souligné

# VT100 : Couleurs : "22" pour normal intensity
CL_BLACK="\033[22;30m"                  #  Noir. NE PAS UTILISER. On ne verra rien !!
CL_RED="\033[22;31m"                    #  Rouge
CL_GREEN="\033[22;32m"                  #  Vert
CL_BROWN = "\033[22;33m"                #  Brun
CL_BLUE="\033[22;34m"                   #  Bleu
CL_MAGENTA="\033[22;35m"                #  Magenta
CL_CYAN="\033[22;36m"                   #  Cyan
CL_GRAY="\033[22;37m"                   #  Gris

# "01" pour quoi ? (bold ?)
CL_DARKGRAY="\033[01;30m"               #  Gris foncé
CL_LIGHTRED="\033[01;31m"               #  Rouge clair
CL_LIGHTGREEN="\033[01;32m"             #  Vert clair
CL_YELLOW="\033[01;33m"                 #  Jaune
CL_LIGHTBLU= "\033[01;34m"              #  Bleu clair
CL_LIGHTMAGENTA="\033[01;35m"           #  Magenta clair
CL_LIGHTCYAN="\033[01;36m"              #  Cyan clair
CL_WHITE="\033[01;37m"                  #  Blanc

#-------------------------------------------------------
import multiprocessing as mp
import os, time, math, random, sys, ctypes, signal

# Une liste de couleurs à affecter aléatoirement aux chevaux
lyst_colors=[CL_WHITE, CL_RED, CL_GREEN, CL_BROWN , CL_BLUE, CL_MAGENTA, CL_CYAN, CL_GRAY,
             CL_DARKGRAY, CL_LIGHTRED, CL_LIGHTGREEN,  CL_LIGHTBLU, CL_YELLOW, CL_LIGHTMAGENTA, CL_LIGHTCYAN]

# Fonction pour effacer l'écran
def effacer_ecran():
    print(CLEARSCR, end='')

# Fonction pour effacer la ligne depuis le début jusqu'au curseur
def erase_line_from_beg_to_curs():
    print("\033[1K", end='')

# Fonction pour rendre le curseur invisible
def curseur_invisible():
    print(CURSOFF, end='')

# Fonction pour rendre le curseur visible
def curseur_visible():
    print(CURSON, end='')

# Fonction pour déplacer le curseur à une position donnée (ligne, colonne)
def move_to(lig, col):
    print("\033[" + str(lig) + ";" + str(col) + "f", end='')

# Fonction pour changer la couleur du texte
def en_couleur(Coul):
    print(Coul, end='')

# Fonction pour changer la couleur du texte en rouge (exemple)
def en_rouge():
    print(CL_RED, end='')

# Fonction pour effacer la ligne entière
def erase_line():
    print(CLEARELN, end='')

# La tâche d'un cheval
def un_cheval(ma_ligne, positions, keep_running, mutex):
    col = 1
    while col < LONGEUR_COURSE and keep_running.value:
        with mutex:
            current_col = positions[ma_ligne]  # Position actuelle du cheval

            # Effacer l'ancien dessin du cheval à la position actuelle
            for i in range(4):
                move_to(ma_ligne * 4 + 1 + i, current_col)
                erase_line()

            # Avancer le cheval
            positions[ma_ligne] += 1
            col = positions[ma_ligne]

            # Dessiner le cheval à la nouvelle position
            move_to(ma_ligne * 4 + 1, col)
            en_couleur(lyst_colors[ma_ligne % len(lyst_colors)])
            print(" _______\\/")
            move_to(ma_ligne * 4 + 2, col)
            print("/−−−− _.\ ")
            move_to(ma_ligne * 4 + 3, col)
            print("/|_____\\")
            move_to(ma_ligne * 4 + 4, col)
            print("/\\  /\\")
        
        # Attendre un temps aléatoire avant de faire avancer le cheval
        time.sleep(0.1 * random.randint(1, 5))

    # Arrêter la course si le cheval a atteint la fin de la course
    if col >= LONGEUR_COURSE:
        keep_running.value = False

# Fonction pour demander la prédiction de l'utilisateur sur le cheval gagnant
def demander_prediction():
    while True:
        try:
            lettre = input("Prévoyez le cheval gagnant (A à {}): ".format(chr(ord('A') + Nb_process - 1))).upper()
            if lettre.isalpha() and 'A' <= lettre <= chr(ord('A') + Nb_process - 1):
                return ord(lettre) - ord('A')
            else:
                print("Veuillez entrer une lettre valide entre A et {}.".format(chr(ord('A') + Nb_process - 1)))
        except Exception as e:
            print(f"Erreur: {e}")

# Fonction pour vérifier si la prédiction de l'utilisateur était correcte
def verifier_prediction(prediction_utilisateur, chevaux_gagnants):
    if prediction_utilisateur in chevaux_gagnants:
        print("Vous avez choisi le bon cheval!")
    else:
        print("Dommage! Le cheval que vous avez choisi n'a pas gagné.")

# Fonction pour l'arbitre de la course
def arbitre(positions, keep_running, mutex):
    while True:
        time.sleep(0.5)  # Attendre un certain temps avant de mettre à jour l'affichage
        with mutex:
            current_positions = list(positions)

        # Vérifier les positions actuelles des chevaux et déterminer les premiers et les derniers
        tied_horses = {}
        for i, pos in enumerate(current_positions):
            if pos in tied_horses:
                tied_horses[pos].append(i)
            else:
                tied_horses[pos] = [i]

        premier = max(current_positions)
        dernier = min(current_positions)
        premier_horses = [i for i, pos in enumerate(current_positions) if pos == premier]
        dernier_horses = [i for i, pos in enumerate(current_positions) if pos == dernier]

        # Afficher les positions actuelles des chevaux
        with mutex:
            move_to(Nb_process * 4 + 2, 1)
            erase_line()
            print(f"Premier: {', '.join(chr(ord('A') + i) for i in premier_horses)}")
            move_to(Nb_process * 4 + 3, 1)
            erase_line()
            for pos, horses in tied_horses.items():
                if len(horses) > 1:
                    print(f"Les chevaux à égalité : {', '.join(chr(ord('A') + i) for i in horses)}")
            move_to(Nb_process * 4 + 4, 1)
            erase_line()
            print(f"Dernier: {', '.join(chr(ord('A') + i) for i in dernier_horses)}")

        # Sortir de la boucle si la course est terminée
        if not keep_running.value:
            break

    # Afficher les résultats finaux de la course
    with mutex:
        premier_horses = [i for i, pos in enumerate(current_positions) if pos == premier]
        dernier_horses = [i for i, pos in enumerate(current_positions) if pos == dernier]

        move_to(Nb_process * 4 + 5, 1)
        erase_line()
        print(f"Course terminée! Premier: {', '.join(chr(ord('A') + i) for i in premier_horses)}")
        move_to(Nb_process * 4 + 6, 1)
        erase_line()
        for pos, horses in tied_horses.items():
            if len(horses) > 1:
                print(f"À égalité avec {', '.join(chr(ord('A') + i) for i in horses)}")
        move_to(Nb_process * 4 + 7, 1)
        erase_line()
        print(f"Dernier: {', '.join(chr(ord('A') + i) for i in dernier_horses)}")

# Fonction pour gérer les interruptions par signal (ex. Ctrl+C)
def detourner_signal(signum, stack_frame):
    move_to(Nb_process * 5 + 5, 1)
    erase_line()
    move_to(Nb_process * 5 + 5, 1)
    curseur_visible()
    print("La course est interrompue ...")
    exit(0)

if __name__ == "__main__":
    import platform
    if platform.system() == "Darwin":
        mp.set_start_method('fork')

    LONGEUR_COURSE = 50
    Nb_process = 5

    positions = mp.Array('i', [0] * Nb_process)
    keep_running = mp.Value(ctypes.c_bool, True)
    mutex = mp.Lock()

    mes_process = [0 for _ in range(Nb_process)]
    effacer_ecran()
    curseur_invisible()
    prediction_utilisateur = demander_prediction()

    signal.signal(signal.SIGINT, detourner_signal)

    # Lancer les processus pour chaque cheval
    for i in range(Nb_process):
        mes_process[i] = mp.Process(target=un_cheval, args=(i, positions, keep_running, mutex))
        mes_process[i].start()

    # Lancer le processus pour l'arbitre
    arbitre_process = mp.Process(target=arbitre, args=(positions, keep_running, mutex))
    arbitre_process.start()

    move_to(Nb_process * 4 + 10, 1)
    print("Tous lancés, CTRL-C arrêtera la course ...")

    # Attendre la fin de tous les processus
    for i in range(Nb_process):
        mes_process[i].join()

    arbitre_process.join()

    move_to(Nb_process * 4 + 10, 1)
    with mutex:
        current_positions = list(positions)
    max_position = max(current_positions)
    chevaux_gagnants = [i for i, pos in enumerate(current_positions) if pos == max_position]

    # Vérifier la prédiction de l'utilisateur
    verifier_prediction(prediction_utilisateur, chevaux_gagnants)

    curseur_visible()
    print("Fini ... ", flush=True)
