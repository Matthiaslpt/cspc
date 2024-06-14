import time
import random
import multiprocessing as mp
import signal
import sys

# Fonction pour gérer l'interruption (Ctrl+C)
def interrupt(signal, frame):
    print("Fin du programme")
    for process in mp.active_children():
        process.terminate()  # Termine tous les processus enfants actifs
    sys.exit(0)

# Fonction pour les demandeurs
def demandeur(queue_d, queue_a, lock_d, lock_a):
    try:
        while True:
            opd1 = random.randint(1, 10)
            opd2 = random.randint(1, 10)
            operateur = random.choice(["+", "-", "*", "/"])
            str_commande = f"{opd1}{operateur}{opd2}"
            
            # Ajoute la commande dans la queue_d avec verrou
            with lock_d:
                queue_d.put((str_commande, mp.current_process().pid))
            
            print(f"Le demandeur {mp.current_process().pid} va demander à faire : {str_commande}")
            
            while True:
                temp = []
                res = None
                # Recherche de la réponse correspondante dans la queue_a avec verrou
                with lock_a:
                    while not queue_a.empty():
                        res = queue_a.get()
                        if res[1] == mp.current_process().pid:
                            break
                        else:
                            temp.append(res)
                    for item in temp:
                        queue_a.put(item)
                
                if res and res[1] == mp.current_process().pid:
                    print(f"Le demandeur {mp.current_process().pid} a reçu : {res[0]}")
                    break
                time.sleep(1)
    except KeyboardInterrupt:
        return

# Fonction pour les fils calculette
def fils_calculette(queue_d, queue_a, lock_d, lock_a):
    print(f"Bonjour du Fils {mp.current_process().pid}")
    try:
        while True:
            # Récupère une commande de la queue_d avec verrou
            with lock_d:
                if not queue_d.empty():
                    cmd, demandeur_id = queue_d.get()
                    print(f"Le fils {mp.current_process().pid} a reçu : {cmd}")
                    
                    try:
                        res = eval(cmd)  # Attention: eval peut être dangereux
                    except Exception as e:
                        res = f"Erreur: {e}"
                    
                    print(f"Dans fils {mp.current_process().pid}, le résultat = {res}")
                    
                    # Met le résultat dans la queue_a avec verrou
                    with lock_a:
                        queue_a.put((res, demandeur_id))
                    
                    print(f"Le fils {mp.current_process().pid} a envoyé : {res}")
            time.sleep(1)
    except KeyboardInterrupt:
        return

# Programme principal
if __name__ == "__main__":
    m = 2  # Nombre de demandeurs
    n = 4  # Nombre de fils calculette
    queue_d = mp.Queue()
    queue_a = mp.Queue()
    
    lock_d = mp.Lock()
    lock_a = mp.Lock()
    
    processes_d = [mp.Process(target=demandeur, args=(queue_d, queue_a, lock_d, lock_a)) for _ in range(m)]
    processes_c = [mp.Process(target=fils_calculette, args=(queue_d, queue_a, lock_d, lock_a)) for _ in range(n)]

    signal.signal(signal.SIGINT, interrupt)  # Gère les interruptions clavier

    for p in processes_c:
        p.start()
    for p in processes_d:
        p.start()

    try:
        for p in processes_d + processes_c:
            p.join()  # Attend la fin de tous les processus
    except KeyboardInterrupt:
        interrupt(None, None)  # Gère les interruptions pendant l'attente
