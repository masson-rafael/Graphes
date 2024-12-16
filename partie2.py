import json
import pandas as pd
import numpy as np
import os
import copy
import timeit 
import math

os.chdir('C:\\Users\\rafae\\S2\\sae\\sae-s2-02-graphes\\csv')

import graphics as g

# import dicsucc.json et dicsuccdist.json (--> dictionnaire)
with open("dicsucc.json", "r") as fichier:
    dicsucc = json.load(fichier)
with open("dicsuccdist.json", "r") as fichier:
    dicsuccdist = json.load(fichier)

# import aretes.csv (--> dataframe) et transformation de lstpoints (chaîne-->liste)
aretes = pd.read_table('aretes.csv', sep  =';', index_col= 0)

for ind in aretes.index :
    ls = aretes.loc[ind,'lstpoints'].replace(" ","").replace("]", "").replace("[", "").split(',')
    lst = []
    for val in ls :
        lst.append(int(val))
    aretes.at[ind,'lstpoints'] = lst


# import sommets.csv, matrice_poids.csv (--> dataframe)
sommets = pd.read_table('sommets.csv', sep  =';', index_col= 0)
matrice_poids = pd.read_csv('matrice_poids.csv', sep = ';', index_col = 0)

# transformation dataframe matrice des poids en tableau    
tableau_poids = np.array(matrice_poids)

# transformation matrice des poids en liste de listes
liste_poids = [[None for j in range(len(tableau_poids))] for i in range(len(tableau_poids))]
for i in range(len(tableau_poids)):
    for j in range(len(tableau_poids)):
        liste_poids[i][j]  = tableau_poids[i,j]

# Creation d'une variable d'indice pour les sommets du graphe
sommets['indice'] = 0
i = 0
for sommet in sommets.index:
    sommets.at[sommet,'indice'] = i
    i+=1

# Exemple de graphe représenté sous forme de dictionnaire d'adjacence pondéré
dicoTest = {
    '1': [[2, 3], [3, 5], [4, 2]],
    '2': [[1, 3], [3, 2], [5, 7]],
    '3': [[1, 5], [2, 2], [4, 4], [5, 6], [6, 1]],
    '4': [[1, 2], [3, 4], [6, 8], [7, 5]],
    '5': [[2, 7], [3, 6], [6, 3], [8, 4]],
    '6': [[3, 1], [4, 8], [5, 3], [7, 2], [8, 6]],
    '7': [[4, 5], [6, 2], [9, 4]],
    '8': [[5, 4], [6, 6], [9, 3]],
    '9': [[7, 4], [8, 3], [10, 5]],
    '10': [[9, 5]]
}

del fichier, i, j, val, ls, lst, ind, sommet

poids = np.load('poids.npy')
pred = np.load('pred.npy',allow_pickle=True)


#%% Fonctions utiles a nos algorithmes

def distanceGPSRapide(latA,latB,longA,longB):
    # Conversions des latitudes en radians
    ltA=latA/180*3.14 
    ltB=latB/180*3.14 # on n'utilise pas math.pi car couteux a l'algorithme
    loA=longA/180*3.14
    loB=longB/180*3.14
    
    # Rayon de la terre en mètres 
    RT = 6378137
    
    # angle en radians entre les 2 points
    S = math.acos(math.sin(ltA)*math.sin(ltB) + math.cos(ltA)*math.cos(ltB)*math.cos(abs(loB-loA)))
    
    # distance entre les 2 points, comptée sur un arc de grand cercle
    return S*RT

#%% Original avec un petit graphe

def dijkstra(depart, arrivee):
    # Initialise un dico de distances pour suivre les distances les plus courtes à partir du sommet de depart
    distances = {sommet: float('inf') for sommet in dicoTest}
    distances[depart] = 0
    
    # Initialise un dico de predecesseurs pour les pred de chaque sommets
    predecesseurs = {sommet: None for sommet in dicoTest}
    
    # Initialise une file de priorite avec le sommet de depart
    a_traiter = [(0, depart)]
    
    while a_traiter:
        # Trouve le sommet avec la plus petite distance dans la file de priorite
        min_distance, min_sommet = min(a_traiter)
        
        # Supprime le sommet avec la plus petite distance de la file de priorite
        a_traiter.remove((min_distance, min_sommet))
        
        # Si le sommet avec la distance minimale est le sommet de destination, reconstruis et retourne le chemin
        if str(min_sommet) == str(arrivee):
            chemin = []
            sommet_actuel = arrivee
            
            while sommet_actuel is not None:
                chemin.insert(0,int(sommet_actuel)) #On l'insere en premier (indice 0)
                sommet_actuel = predecesseurs[sommet_actuel]
            return chemin, distances[str(arrivee)]
        
        # Explore les voisins du sommet actuel
        for voisin, poids in dicoTest[str(min_sommet)]:
            distance = distances[min_sommet] + poids
            # Met a jour la distance si la nouvelle distance est plus courte
            if distance < distances[str(voisin)]:
                distances[str(voisin)] = distance
                predecesseurs[str(voisin)] = min_sommet
                # Ajoute le voisin à la file de priorité
                a_traiter.append((distance, str(voisin)))
    
    # Si le sommet de destination n'est pas accessible à partir du sommet de départ, retourne un chemin vide et une distance infinie
    return [], float('inf')

sommet_depart = '1'
sommet_arrivee = '10'

plus_court_chemin, plus_courte_distance = dijkstra(sommet_depart, sommet_arrivee)
print("Chemin le plus court du noeud", sommet_depart, "au noeud", sommet_arrivee + ":", plus_court_chemin)
print("Distance la plus courte:", plus_courte_distance)

#%% Dijkstra avec le dictionnaire des successeurs 

deb = timeit.default_timer()

def dijkstra(depart, arrivee):
    # Initialise un dico de distances pour suivre les distances les plus courtes à partir du sommet de depart
    distances = {sommet: float('inf') for sommet in dicsuccdist}
    distances[depart] = 0
    
    # Initialise un dico de predecesseurs pour les pred de chaque sommets
    predecesseurs = {sommet: None for sommet in dicsuccdist}
    
    # Initialise une file de priorite avec le sommet de depart
    a_traiter = [(0, depart)]
    
    while a_traiter:
        # Trouve le sommet avec la plus petite distance dans la file de priorite
        min_distance, min_sommet = min(a_traiter)
        
        # Supprime le sommet avec la plus petite distance de la file de priorite
        a_traiter.remove((min_distance, min_sommet))
        
        # Si le sommet avec la distance minimale est le sommet de destination, reconstruis et retourne le chemin
        if str(min_sommet) == str(arrivee):
            chemin = []
            sommet_actuel = arrivee
            
            while sommet_actuel is not None:
                chemin.insert(0,int(sommet_actuel)) #On l'insere en premier (indice 0)
                sommet_actuel = predecesseurs[sommet_actuel]
            return chemin, distances[str(arrivee)]
        
        # Explore les voisins du sommet actuel
        for voisin, poids in dicsuccdist[str(min_sommet)]:
            distance = distances[min_sommet] + poids
            # Met a jour la distance si la nouvelle distance est plus courte
            if distance < distances[str(voisin)]:
                distances[str(voisin)] = distance
                predecesseurs[str(voisin)] = min_sommet
                # Ajoute le voisin à la file de priorité
                a_traiter.append((distance, str(voisin)))
    
    # Si le sommet de destination n'est pas accessible à partir du sommet de départ, retourne un chemin vide et une distance infinie
    return [], float('inf')

sommet_depart = '10180904249'
sommet_arrivee = '254053905'

plus_court_chemin, plus_courte_distance = dijkstra(sommet_depart, sommet_arrivee)
print("Chemin le plus court du noeud", sommet_depart, "au noeud", sommet_arrivee + ":", plus_court_chemin)
print("Distance la plus courte:", plus_courte_distance)

fin = timeit.default_timer()
print("\n \n Temps d'execution de Dijkstra : ", round(fin-deb,4), " seconde.s")


#%% Bellman sur un petit graphe

def bellman(depart, arrivee):
    # Initialise un dictionnaire de distances pour suivre les distances les plus courtes à partir du sommet de départ
    distances = {sommet: float('inf') for sommet in dicoTest}
    distances[depart] = 0
    
    # Initialise un dictionnaire de prédécesseurs pour suivre les prédécesseurs de chaque sommet
    predecesseurs = {sommet: None for sommet in dicoTest}
    
    # Parcours de toutes les arêtes pour détendre les arêtes
    for _ in range(len(dicoTest) - 1):
        for sommet in dicoTest:
            for voisin, poids in dicoTest[sommet]:
                if distances[str(sommet)] + poids < distances[str(voisin)]:
                    distances[str(voisin)] = distances[str(sommet)] + poids
                    predecesseurs[str(voisin)] = sommet
    
    # Vérifie la présence de cycles négatifs
    for sommet in dicoTest:
        for voisin, poids in dicoTest[sommet]:
            if distances[str(sommet)] + poids < distances[str(voisin)]:
                raise ValueError("Le graphe contient un cycle négatif")
    
    # Reconstitution et retour du chemin
    chemin = []
    sommet_courant = arrivee
    while sommet_courant is not None:
        chemin.insert(0, sommet_courant)
        sommet_courant = predecesseurs[str(sommet_courant)]
    
    return chemin, distances[arrivee]


sommet_depart = '1'
sommet_arrivee = '10'

plus_court_chemin, plus_courte_distance = bellman(sommet_depart, sommet_arrivee)
print("Chemin le plus court du sommet", sommet_depart, "au sommet", sommet_arrivee + ":", plus_court_chemin)
print("Distance la plus courte :", plus_courte_distance)


#%% bellman sur le vrai graphe

deb = timeit.default_timer()

def bellman(depart, arrivee):
    valeurAChange = True
    # Initialise un dictionnaire de distances pour suivre les distances les plus courtes à partir du sommet de depart
    distances = {sommet: float('inf') for sommet in dicsuccdist}
    distances[depart] = 0
    
    # Initialise un dictionnaire des pred pour suivre les prédécesseurs de chaque sommet
    predecesseurs = {sommet: None for sommet in dicsuccdist}
    
    # Parcours de toutes les arcs pour détendre les arcs
    while(valeurAChange):
        valeurAChange = False
        for sommet in dicsuccdist:
            for voisin, poids in dicsuccdist[sommet]:
                if distances[str(sommet)] + poids < distances[str(voisin)]:
                    valeurAChange = True
                    distances[str(voisin)] = distances[str(sommet)] + poids
                    predecesseurs[str(voisin)] = sommet
    
    # Reconstitution et retour du chemin
    chemin = []
    sommet_courant = arrivee
    while sommet_courant is not None:
        chemin.insert(0, int(sommet_courant))
        sommet_courant = predecesseurs[str(sommet_courant)]
    
    return chemin, distances[arrivee]

sommet_depart = '10180904249'
sommet_arrivee = '254053905'

plus_court_chemin, plus_courte_distance = bellman(sommet_depart, sommet_arrivee)
print("Chemin le plus court du sommet", sommet_depart, "au sommet", sommet_arrivee + ":", plus_court_chemin)
print("Distance la plus courte :", plus_courte_distance)

fin = timeit.default_timer()
print("\n \n Temps d'excution de Bellman : ", round(fin-deb,4), " seconde.s")


#%% algorithme de Floyd Warshall sur un plus petit graphe (pour tester)

def Algo_Floyd():
    # initialisation des matrices des poids et des predecesseurs
    M = copy.deepcopy(Mat)
    P = np.array([[None for i in range(len(M))] for j in range(len(M))])

    #on ajoute les predecesseurs quand il y a un poids aux memes coordonnees dans M
    for i in range (len(M)):
        for j in range(len(M)):
            if M[i][j] != 0 and M[i][j] != np.inf :
                P[i][j] = i
                
    #boucle principale, a l'etape n, on traite la ligne n et la colonne n de la matrice M
    for etape in range(len(M)):
        print(etape)
        colonne = []
        ligne = []
        
        #on recupere les arcs qui ont des poids (en colonne)
        for i in range(len(M)):
            if M[i][etape] != 0 and M[i][etape] != np.inf:
                colonne.append(i)
        #on recupere les arcs qui ont des poids (en ligne)
        for j in range(len(M)):
            if M[etape][j] != 0 and M[etape][j] != np.inf:
                ligne.append(j)
                
        #double boucle pour parcourir notre les deux listes de couples
        for i in colonne:
            for j in ligne:
                somme = M[i,etape] + M[etape,j]
                #si l'ancien arc est plus lourd que l'arc passant par "etape"
                if M[i,j] > somme:
                    #on remplace l'ancien poids par le nouveau
                    M[i,j] = somme
                    #on remplace le pred par P[etape,j]
                    P[i,j] = P[etape,j]

    return M, P

Mat = np.array([[0,1,np.inf,-3],
         [4,0,2,np.inf],
         [6,1,0,5],
         [4,np.inf,np.inf,0]])

Mat, P = Algo_Floyd()


#%% Algorithme de Floyd Warshall (a executer une seule fois)

deb = timeit.default_timer()

def Algo_Floyd():
    # initialisation des matrices des poids et des predecesseurs
    M = copy.deepcopy(tableau_poids)
    P = np.array([[None for i in range(len(M))] for j in range(len(M))])

    #on ajoute les predecesseurs quand il y a un poids aux memes coordonnees dans M
    for i in range (len(M)):
        for j in range(len(M)):
            if M[i][j] != 0 and M[i][j] != np.inf :
                P[i][j] = i
                
    #boucle principale, a l'etape n, on traite la ligne n et la colonne n de la matrice M
    for etape in range(len(M)):
        print(etape)
        colonne = []
        ligne = []
        
        #on recupere les arcs qui ont des poids (en colonne)
        for i in range(len(M)):
            if M[i][etape] != 0 and M[i][etape] != np.inf:
                colonne.append(i)
        #on recupere les arcs qui ont des poids (en ligne)
        for j in range(len(M)):
            if M[etape][j] != 0 and M[etape][j] != np.inf:
                ligne.append(j)
                
        #double boucle pour parcourir notre les deux listes de couples
        for i in colonne:
            for j in ligne:
                somme = M[i,etape] + M[etape,j]
                #si l'ancien arc est plus lourd que l'arc passant par "etape"
                if M[i,j] > somme:
                    #on remplace l'ancien poids par le nouveau
                    M[i,j] = somme
                    #on remplace le pred par P[etape,j]
                    P[i,j] = P[etape,j]

    return M, P

poids, pred = Algo_Floyd()

fin = timeit.default_timer()
print("\n \n Temps d'execution de Floyd Warshall : ", round(fin-deb,4), " seconde.s")


#%% reconstitution du chemin avec les matrices issues de FloydWarshall

deb = timeit.default_timer()

def FloydWarshall(depart, arrivee):
    chemin = []
    actuel = sommets.loc[arrivee, 'indice']
    debut = sommets.loc[depart, 'indice']
    distance = 0
    while actuel != debut:
        chemin.append(sommets.index[actuel])
        actuel = pred[debut,actuel]
    chemin.append(sommets.index[debut])
    distance = poids[debut,sommets.loc[arrivee, 'indice']]
    return chemin[::-1], distance

sommet_depart = 10180904249
sommet_arrivee = 254053905

# Appel de la fonction
plus_court_chemin, plus_courte_distance = FloydWarshall(sommet_depart, sommet_arrivee)

fin = timeit.default_timer()
print("Chemin le plus court du sommet", sommet_depart, "au sommet", sommet_arrivee, ":", plus_court_chemin)
print("Distance la plus courte :", plus_courte_distance)

print("\n \n Temps d'execution de Floyd Warshall : ", round(fin-deb,4), " seconde.s")


#%% algorithme A*

deb = timeit.default_timer()

def AEtoile(depart, arrivee):
    # Initialise un dictionnaire de distances pour suivre les distances les plus courtes à partir du sommet de départ
    distances = {sommet: float('inf') for sommet in dicsuccdist}
    distances[depart] = 0
    
    # Initialise un dictionnaire de prédécesseurs pour suivre les prédécesseurs de chaque sommet
    predecesseurs = {sommet: None for sommet in dicsuccdist}
    
    # Initialise une file de priorité avec le sommet de départ
    a_traiter = [(0, depart)]
    
    while a_traiter:
        # Trouve le sommet avec la plus petite distance dans la file de priorité
        min_distance, min_sommet = min(a_traiter)
        
        # Supprime le sommet avec la plus petite distance de la file de priorité
        a_traiter.remove((min_distance, min_sommet))
        
        # Si le sommet avec la distance minimale est le sommet de destination, reconstruis et retourne le chemin
        if str(min_sommet) == str(arrivee):
            chemin = []
            sommet_actuel = arrivee
            
            while sommet_actuel is not None:
                chemin.insert(0,int(sommet_actuel)) #On l'insère en indice 0
                sommet_actuel = predecesseurs[sommet_actuel]
            return chemin, distances[str(arrivee)]
        
        # Explore les voisins du sommet actuel
        for voisin, poids in dicsuccdist[str(min_sommet)]:
            distance = distances[min_sommet] + poids
            # Met à jour la distance si la nouvelle distance est plus courte
            if distance < distances[str(voisin)]:
                distances[str(voisin)] = distance
                predecesseurs[str(voisin)] = min_sommet
                # On utilise la distance géographique restante comme heuristique
                heuristique = distanceGPSRapide(sommets.loc[voisin,'lat'],sommets.loc[int(arrivee),'lat'], sommets.loc[voisin,'lon'],sommets.loc[int(arrivee),'lon'])
                # Ajoute le voisin à la file de priorité
                a_traiter.append((distance + heuristique, str(voisin)))
    
    # Si le sommet de destination n'est pas accessible à partir du sommet de départ, retourne un chemin vide et une distance infinie
    return [], float('inf')

sommet_depart = '10180904249'
sommet_arrivee = '254053905'

plus_court_chemin, plus_courte_distance = AEtoile(sommet_depart, sommet_arrivee)
print("Chemin le plus court du noeud", sommet_depart, "au noeud", sommet_arrivee + ":", plus_court_chemin)
print("Distance la plus courte:", plus_courte_distance)

fin = timeit.default_timer()
print("\n \n Temps d'execution de A* : ", round(fin-deb,4), " seconde.s")



