import random, time
import multiprocessing as mp


# calculer le nbr de hits dans un cercle unitaire (utilisé par les différentes méthodes)
def frequence_de_hits_pour_n_essais(nb_iteration,tableau,index):
    count = 0
    for i in range(nb_iteration):
        x = random.random()
        y = random.random()
# si le point est dans l’unit circle
        if x * x + y * y <= 1: count += 1
    tableau[index] = count



if __name__ == "__main__" :
    nb_total_iteration = 10000000 # Nombre d’essai pour l’estimation

#TRACE : Valeur estimée Pi par la méthode Mono−Processus : 3.1412604
#Temps du mono-process : 2.922
  
    nb_process = 4  # Définissez le nombre de processus
    nb_iteration_process = nb_total_iteration // nb_process

    # Création d'un tableau partagé pour stocker les résultats
    tableau = mp.Array('i', nb_process)

    # Création de la liste de processus
    processes = []

    depart = time.time()

    # Démarrage de chaque processus
    for i in range(nb_process):
        process = mp.Process(target=frequence_de_hits_pour_n_essais, args=(nb_iteration_process, tableau, i))
        processes.append(process)
        process.start()

    # Attendre que tous les processus se terminent
    for process in processes:
        process.join()

    nb_hits = sum(tableau)
    fin = time.time()
    temps = fin - depart

    print("Valeur estimée Pi par la méthode Multi-Processus : ", 4 * nb_hits / nb_total_iteration)
    print("Temps du calcul : ", temps)