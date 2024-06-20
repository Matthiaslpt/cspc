import multiprocessing as mp
import os, time, math, random, sys, ctypes, signal
import numpy as np

# Escape codes for terminal control
CLEARSCR = "\x1B[2J\x1B[;H"          # Clear Screen
CLEAREOS = "\x1B[J"                  # Clear End Of Screen
CLEARELN = "\x1B[2K"                 # Clear Entire Line
CLEARCUP = "\x1B[1J"                 # Clear Cursor UP
GOTOYX = "\x1B[%.2d;%.2dH"           # ('H' or 'f') : Goto at (y,x), see code

DELAFCURSOR = "\x1B[K"               # Erase after cursor position
CRLF = "\r\n"                        # Carriage Return and Line Feed

# VT100: Cursor actions
CURSON = "\x1B[?25h"                 # Cursor visible
CURSOFF = "\x1B[?25l"                # Cursor invisible

# VT100: Display actions
NORMAL = "\x1B[0m"                   # Normal
BOLD = "\x1B[1m"                     # Bold
UNDERLINE = "\x1B[4m"                # Underline

CL_WHITE = "\033[01;37m"             # White color
Case = {0: "⬛", 1: "⬜"}

def effacer_ecran():
    print(CLEARSCR, end='')

def erase_line_from_beg_to_curs():
    print("\033[1K", end='')

def curseur_invisible():
    print(CURSOFF, end='')

def curseur_visible():
    print(CURSON, end='')

def move_to(lig, col):
    print("\033[" + str(lig) + ";" + str(col) + "f", end='')

def en_couleur(Coul):
    print(Coul, end='')

def erase_line():
    print(CLEARELN, end='')

def load_nextgen(start, end, size, barriere, shared_cworld_array, shared_nworld_array): #Fonction qui crée les processus permettant de calculer les générations futures
    while True:
        current_world = np.array(shared_cworld_array[:]).reshape(size, size) #Les reshapes me permettent de passer un matrice dans un tableau partagé et inversement
        for i in range(start, end): # Calcul avec les cellules voisines, pour les bords il utilise les cases de l'autre côté pour "simuler" une grille infinie
            for j in range(size): # Somme des cases voisines
                alive = sum([
                    current_world[(i-1) % size, (j-1) % size],
                    current_world[(i-1) % size, j % size],
                    current_world[(i-1) % size, (j+1) % size],
                    current_world[i % size, (j-1) % size],
                    current_world[i % size, (j+1) % size],
                    current_world[(i+1) % size, (j-1) % size],
                    current_world[(i+1) % size, j % size],
                    current_world[(i+1) % size, (j+1) % size],
                ])

                if current_world[i, j] == 1: # Réaction par rapport aux règles du jeu
                    shared_nworld_array[i*size + j] = 1 if alive in [2, 3] else 0
                else:
                    shared_nworld_array[i*size + j] = 1 if alive == 3 else 0

        barriere.wait() # Attente de tout les processus
        if barriere.wait() == 0:  # Mise a jour de la grille par un seul processus pour éviter un bordel
            for idx in range(size*size):
                shared_cworld_array[idx] = shared_nworld_array[idx]
            print_world(shared_cworld_array, size)
            time.sleep(0.1)

        barriere.wait()

def print_world(shared_cworld_array, size): #Fonction qui affiche la grille dans la console en utilisant le move_to 
    effacer_ecran()
    move_to(0, 0)
    current_world = np.array(shared_cworld_array[:]).reshape(size, size)
    for i, row in enumerate(current_world):
        t = 1
        for j, state in enumerate(row):
            move_to(i + 1, j+t)
            t += 1
            print(Case[state], end='')
    sys.stdout.flush()

if __name__ == "__main__":
    size = 40
    # Create the world
    current_world = []
    for x in range(1, size + 1):
        row = []
        for k in range(1, size + 1):
            row.append(0)
        current_world.append(row)

# Pour voir l'évolution de la grille j'ai récuperer un modèle de glider gun du jeu de la vie et j'ai mit les coordonnées ci-dessous
    glider_gun_coords = [
    (1, 25),
    (2, 23), (2, 25),
    (3, 13), (3, 14), (3, 21), (3, 22), (3, 35), (3, 36),
    (4, 12), (4, 16), (4, 21), (4, 22), (4, 35), (4, 36),
    (5, 1), (5, 2), (5, 11), (5, 17), (5, 21), (5, 22),
    (6, 1), (6, 2), (6, 11), (6, 15), (6, 17), (6, 18), (6, 23), (6, 25),
    (7, 11), (7, 17), (7, 25),
    (8, 12), (8, 16),
    (9, 13), (9, 14)
    ]

    for x, y in glider_gun_coords:
        current_world[x][y] = 1

    current_world = np.array(current_world)
    shared_cworld_array = mp.Array('i', current_world.reshape(1, size*size)[0])
    shared_nworld_array = mp.Array('i', size*size)
    print_world(shared_cworld_array, size)

    nb_process = os.cpu_count() #Adapte le nombre de processus en fonction des capacités de la machine
    barriere = mp.Barrier(nb_process + 1)
    processes = []
    rows_per_process = size // nb_process # Permet de répartir un nombre de lignes équivalent entre chaques processus

    for i in range(nb_process): # Et donc création des processus calculateurs
        start = i * rows_per_process
        end = (i + 1) * rows_per_process if i < nb_process - 1 else size
        p = mp.Process(target=load_nextgen, args=(start, end, size, barriere, shared_cworld_array, shared_nworld_array))
        processes.append(p)
        p.start()

    try:
        while True:
            barriere.wait()
            barriere.wait()
            time.sleep(0.1)
    except KeyboardInterrupt:
        for p in processes:
            p.terminate()
        effacer_ecran()
        curseur_visible()
        print("Fin de simulation")
