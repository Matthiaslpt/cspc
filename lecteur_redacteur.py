import multiprocessing as mp
import time
import random
import signal
import sys

def lecteur(lecteurs, redacteurs, demandes_de_redaction, mutex): # Fonction lecteur qui crée les processus lecteurs n'ayant pas la priorité sur les rédacteurs
    while True:
        try:
            with mutex:
                while demandes_de_redaction.value > 0: # Personne n'écrit actuellement
                    mutex.release()
                    time.sleep(0.1)
                    mutex.acquire()
                lecteurs.value += 1
        except KeyboardInterrupt:
            print(f"Lecteur {mp.current_process().pid} interrompu")
            break

        print(f"Lecteur {mp.current_process().pid} lit les données")
        time.sleep(random.uniform(0.1, 0.5))

        with mutex:
            lecteurs.value -= 1
            if lecteurs.value == 0 and demandes_de_redaction.value == 0:
                redacteurs.release()
        
        print(f"Lecteur {mp.current_process().pid} a fini de lire les données")
        time.sleep(random.uniform(0.1, 0.5))

def redacteur(lecteurs, redacteurs, demandes_de_redaction, mutex): # Fonction rédacteur qui crée les processus rédacteurs
    while True:
        try:
            with mutex:
                demandes_de_redaction.value += 1
                while lecteurs.value > 0 or redacteurs.get_value() == 0: #On attend que les conditions soient validées pour lancer l'écriture du rédacteur
                    mutex.release()
                    time.sleep(0.1)
                    mutex.acquire()
                redacteurs.acquire() # "Autorisation d'écrire"
        except KeyboardInterrupt:
            print(f"Rédacteur {mp.current_process().pid} interrompu")
            break

        print(f"Rédacteur {mp.current_process().pid} écrit les données")
        time.sleep(random.uniform(0.1, 0.5))

        with mutex:
            redacteurs.release()
            demandes_de_redaction.value -= 1
            if demandes_de_redaction.value == 0:
                redacteurs.release()
        
        print(f"Rédacteur {mp.current_process().pid} a fini d'écrire les données")
        time.sleep(random.uniform(0.1, 0.5))

def handle_sigint(signum, frame):
    print("\nArrêt du programme")
    sys.exit(0)

if __name__ == "__main__": # Programme principal qui initialise les variables, crée/lance les processus et gère les interruptions
    signal.signal(signal.SIGINT, handle_sigint)
    
    nb_lecteurs = 3
    nb_redacteurs = 2

    lecteurs = mp.Value('i', 0)
    redacteurs = mp.Semaphore(1)
    demandes_de_redaction = mp.Value('i', 0)
    mutex = mp.Lock()

    processus = []
    for i in range(nb_lecteurs):
        p = mp.Process(target=lecteur, args=(lecteurs, redacteurs, demandes_de_redaction, mutex))
        processus.append(p)
    for i in range(nb_redacteurs):
        p = mp.Process(target=redacteur, args=(lecteurs, redacteurs, demandes_de_redaction, mutex))
        processus.append(p)

    try:
        for p in processus:
            p.start()
        for p in processus:
            p.join()
    except KeyboardInterrupt:
        print("\nArrêt du programme")
        for p in processus:
            p.terminate()
        for p in processus:
            p.join()
