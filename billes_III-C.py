import multiprocessing as mp
import os, sys, time, signal
import random as r


# Fonction pour gérer l'interruption
def interrupt():
    print("Fin du programme")
    for process in mp.active_children():
        process.terminate()  # Termine tous les processus enfants actifs
    sys.exit(0)


def Controleur(max_billes, SC, tableau_p): #Vérifie que le nombre de billes total ne dépasse jamais le nombre initial
    while True:
        with SC:
            if not 0 <= nbr_disponible_billes.value <= max_billes:
                for pid in tableau_p:
                    if pid != 0:  # s'assurer qu'on a des pids valides
                        try:
                            os.kill(pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
        time.sleep(1)

def Travailleur(k_bills, s, Lock, SC, id): #fonction qui permet de créer les processus travailleur
    m = 2
    for i in range(m):
        print("Je suis le processus ",id," je demande: ",k_bills)
        Demander(k_bills, Lock, s, SC,id)
        print("Je suis le processus ",id," j'utilise: ",k_bills," il en reste donc :", nbr_disponible_billes.value)
        time.sleep(k_bills)
        rendre(k_bills, s)
        print("Je suis le processus ",id," j'ai rendu: ",k_bills," il y a donc  :", nbr_disponible_billes.value," disponibles")

def rendre(k_bills, s): #Fonction utilisé par les processus pour rendre les billes utilisés au processus père
    with nbr_disponible_billes.get_lock():
        nbr_disponible_billes.value += k_bills
    s.release()

def Demander(k_bills, Lock, s, SC,id): #Fonction utilisé par les processus pour demander des billes tant qu'ils n'y en a pas assez pour satisfaire cette demande
    wait = False
    with Lock:
        with SC:
            while nbr_disponible_billes.value < k_bills:
                if not wait:
                    print("Je suis le processus ",id," je me met en attente")
                    wait = True
                SC.release()
                Lock.release()
                s.acquire()
                Lock.acquire()
                SC.acquire()
        if wait:
            print("Je suis le processus ",id," j'ai fini d'attendre")
        nbr_disponible_billes.value -= k_bills

if __name__ == "__main__": # Programme principal avec l'initialisation des variables et le lancement des processus
    nbr_disponible_billes = mp.Value('i', 9, lock=True)
    Lock = mp.Lock()
    SC = mp.Semaphore(1)
    s_wait = mp.Semaphore(0)
    N = 4
    process = []
    tableau_p = mp.Array('i', N)
    
    for i in range(N):
        k_bills = r.randint(1, 8)
        p = mp.Process(target=Travailleur, args=(k_bills, s_wait, Lock, SC,i+1))
        process.append(p)
        

    for pr in process:
        pr.start()

    c = mp.Process(target=Controleur, args=(9, SC, tableau_p))
    c.start()

    

    try:
        for pr in process:
            pr.join()
            tableau_p[i] = pr.pid if pr else 0
    except KeyboardInterrupt:
        interrupt()  # Gère les interruptions pendant l'attente

    c.terminate()
    c.join()
