import time,os,random
import multiprocessing as mp
import signal, sys

def interupt(signal, frame):
    print("Fin du programme")
    for process in mp.active_children():
        process.terminate()
        process.join()

def filtrage(queue, id):
    temp = []
    while True: # Filtrage de la queue
        if not queue.empty():
            msg = queue.get()
            if msg[1] == id:
                break
            else:
                temp.append(msg) # On stocke les messages non utilisés
        time.sleep(1)
    for item in temp:
        queue.put(item) # On remet les messages qui ne sont pas destinés à ce calculateur dans la queue
    return msg



def demandeur(queue_d, queue_a):
    while True:
        # Le demandeur envoie au fils un calcul aléatoire à faire et récupère le résultat
        opd1 = random.randint(1,10)
        opd2 = random.randint(1,10)
        operateur = random.choice(["+", "-", "*", "/"])
        str_commande = str(opd1) + operateur + str(opd2)
        queue_d.put([str_commande, mp.current_process().pid])
        print(f"Le demandeur {mp.current_process().pid} va demander à faire : ", str_commande)
        while queue_a.empty():
            time.sleep(1)
        res = filtrage(queue_a, mp.current_process().pid)
        print(f"Le demandeur {mp.current_process().pid} a recu ", res[0])
        time.sleep(1)

def fils_calculette(queue_d, queue_a):
    print("Bonjour du Fils ", mp.current_process()) 
    
    while True:
        if not queue_d.empty():
            msg = queue_d.get()
            cmd = msg[0]
            print(f"Le fils {mp.current_process().pid} a recu ", cmd)
            res=eval(cmd)
            print(f"Dans fils {mp.current_process().pid}, le résultat =", res)
            queue_a.put([res, msg[1]])
            print(f"Le fils {mp.current_process().pid} a envoyé", res)

        time.sleep(1)
    os._exit(0)

    
if __name__ == "__main__":
    m = 2
    n = 4
    processes_d = []
    processes_c = []
    queue_d = mp.Queue()
    queue_a = mp.Queue()
    for i in range(m):
        p = mp.Process(target=demandeur, args=(queue_d, queue_a))
        
        processes_d.append(p)

    for i in range(n):
        p = mp.Process(target=fils_calculette, args=(queue_d, queue_a))
        processes_c.append(p)


    for p in processes_c:
        p.start()
        
    for p in processes_d:
        p.start()
    
 

    signal.signal(signal.SIGINT, interupt)



            
