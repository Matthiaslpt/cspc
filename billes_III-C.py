import multiprocessing as mp
import os, sys, time, signal
import random as r

def Controleur(max_billes, SC, tableau_p):
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

def Travailleur(k_bills, s, Lock, SC, id):
    m = 2
    for i in range(m):
        print("Je suis le processus ",id," je demande: ",k_bills)
        Demander(k_bills, Lock, s, SC,id)
        print("Je suis le processus ",id," j'utilise: ",k_bills," il en reste donc :", nbr_disponible_billes.value)
        time.sleep(k_bills)
        rendre(k_bills, s)
        print("Je suis le processus ",id," j'ai rendu: ",k_bills," il y a donc  :", nbr_disponible_billes.value," disponibles")

def rendre(k_bills, s):
    with nbr_disponible_billes.get_lock():
        nbr_disponible_billes.value += k_bills
    s.release()

def Demander(k_bills, Lock, s, SC,id):
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

if __name__ == "__main__":
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

    for pr in process:
        pr.join()
        tableau_p[i] = pr.pid if pr else 0

    c.terminate()
    c.join()
