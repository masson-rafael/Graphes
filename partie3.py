import json
import pandas as pd
import numpy as np
import os
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

poids = np.load('poids.npy')
pred = np.load('pred.npy',allow_pickle=True)

# Creation d'une variable d'indice pour les sommets du graphe
sommets['indice'] = 0
i = 0
for sommet in sommets.index:
    sommets.at[sommet,'indice'] = i
    i+=1


#%% Génération de la carte dans une fenetre graphique

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


dim = (1411,912)
point1 = (43.48478,-1.48768)
point2 = (43.4990,-1.45738)



def affichageBG():
    win = g.GraphWin("Carte de Bayonne", 1411, 912)

    background = g.Image(g.Point(1411/2,912/2), "CaptureOpenStreetMap2024.png")
    background.draw(win)
    return win


def affichagePts(win):
    for point in sommets.index:
        lat = sommets.loc[point, 'lat']
        lon = sommets.loc[point, 'lon']
        x = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
        y = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
        c = g.Circle(g.Point(x,y), 2)
        c.setFill(g.color_rgb(200,200,200))
        c.draw(win)
    return win


def dessinArcs(win):
    
    for sommet in dicsucc:
        
        lat = sommets.loc[int(sommet), 'lat']
        lon = sommets.loc[int(sommet), 'lon']
        x = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
        y = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
        
        for voisin in dicsucc[sommet]:
            
            lat = sommets.loc[int(voisin), 'lat']
            lon = sommets.loc[int(voisin), 'lon']
            x2 = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
            y2 = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
            c = g.Line(g.Point(x,y), g.Point(x2,y2))
            c.setWidth(1)
            c.setFill("blue")
            c.draw(win)

    return win
            
            
          
def dessinPtsDepart(depart,arrivee, win):
    lat = sommets.loc[int(depart), 'lat']
    lon = sommets.loc[int(depart), 'lon']
    x = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
    y = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
    c = g.Circle(g.Point(x,y), 4)
    c.setOutline("red")
    c.setFill("red")
    c.draw(win)
    
    lat = sommets.loc[int(arrivee), 'lat']
    lon = sommets.loc[int(arrivee), 'lon']
    x = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
    y = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
    c = g.Circle(g.Point(x,y), 4)
    c.setOutline("red")
    c.setFill("red")
    c.draw(win)



def dijkstra(depart, arrivee, aff):
    if aff:
        win = dessinArcs(affichagePts(affichageBG()))
        dessinPtsDepart(depart, arrivee, win)
    
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
                if aff:
                    lat = sommets.loc[int(sommet_actuel), 'lat']
                    lon = sommets.loc[int(sommet_actuel), 'lon']
                    x = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
                    y = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
                
                chemin.insert(0,int(sommet_actuel)) #On l'insere en premier (indice 0)
                sommet_actuel = predecesseurs[sommet_actuel]
                
                if sommet_actuel != None:
                    if aff:
                        lat = sommets.loc[int(sommet_actuel), 'lat']
                        lon = sommets.loc[int(sommet_actuel), 'lon']
                        x2 = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
                        y2 = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
                        c = g.Line(g.Point(x,y), g.Point(x2,y2))
                        c.setWidth(5)
                        c.setFill("red")
                        c.draw(win)
            if aff:
                win.getMouse() # Pause to view result
                win.close()    # Close window when done
            return chemin, distances[str(arrivee)]
        
        if aff:
            lat = sommets.loc[int(min_sommet), 'lat']
            lon = sommets.loc[int(min_sommet), 'lon']
            x = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
            y = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
        
        # Explore les voisins du sommet actuel
        for voisin, poids in dicsuccdist[str(min_sommet)]:
            distance = distances[min_sommet] + poids
            
            if aff:
                lat = sommets.loc[int(voisin), 'lat']
                lon = sommets.loc[int(voisin), 'lon']
                x2 = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
                y2 = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
                c = g.Line(g.Point(x,y), g.Point(x2,y2))

                if distance < distances[str(voisin)]:
                    c.setFill("green")
                c.setWidth(1.5)
                c.draw(win)
            
            # Met a jour la distance si la nouvelle distance est plus courte
            if distance < distances[str(voisin)]:
                distances[str(voisin)] = distance
                predecesseurs[str(voisin)] = min_sommet
                # Ajoute le voisin à la file de priorité
                a_traiter.append((distance, str(voisin)))
    
    # Si le sommet de destination n'est pas accessible à partir du sommet de départ, retourne un chemin vide et une distance infinie
    return [], float('inf')


def bellman(depart, arrivee, aff):
    if aff:
        win = dessinArcs(affichagePts(affichageBG()))
        dessinPtsDepart(depart, arrivee, win)
    
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
            
            if aff:
                lat = sommets.loc[int(sommet), 'lat']
                lon = sommets.loc[int(sommet), 'lon']
                x = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
                y = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
            
            for voisin, poids in dicsuccdist[sommet]:
                if distances[str(sommet)] + poids < distances[str(voisin)]:
                    
                    if aff:
                        lat = sommets.loc[int(voisin), 'lat']
                        lon = sommets.loc[int(voisin), 'lon']
                        x2 = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
                        y2 = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
                        c = g.Line(g.Point(x,y), g.Point(x2,y2)) 
                    
                    valeurAChange = True
                    distances[str(voisin)] = distances[str(sommet)] + poids
                    predecesseurs[str(voisin)] = sommet
                    if aff:
                        c.setWidth(2)
                        c.setFill("black")
                        c.draw(win)
                
                
    # Reconstitution et retour du chemin
    chemin = []
    sommet_courant = arrivee
    
    while sommet_courant is not None:
        chemin.insert(0, int(sommet_courant))
        
        if aff:
            lat = sommets.loc[int(sommet_courant), 'lat']
            lon = sommets.loc[int(sommet_courant), 'lon']
            x = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
            y = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))

        sommet_courant = predecesseurs[str(sommet_courant)]
    
        if sommet_courant != None:
            if aff:
                lat = sommets.loc[int(sommet_courant), 'lat']
                lon = sommets.loc[int(sommet_courant), 'lon']
                x2 = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
                y2 = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
                c = g.Line(g.Point(x,y), g.Point(x2,y2))
                c.setWidth(5)
                c.setFill("red")
                c.draw(win)
    
    if aff:
        win.getMouse() # Pause to view result
        win.close()    # Close window when done
    
    return chemin, distances[arrivee]






def AEtoile(depart, arrivee, aff):
    
    if aff:
        win = dessinArcs(affichagePts(affichageBG()))
        dessinPtsDepart(depart, arrivee, win)
    
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
                
                if aff:
                    lat = sommets.loc[int(sommet_actuel), 'lat']
                    lon = sommets.loc[int(sommet_actuel), 'lon']
                    x = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
                    y = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
                
                chemin.insert(0,int(sommet_actuel)) #On l'insere en premier (indice 0)
                sommet_actuel = predecesseurs[sommet_actuel]
                
                if sommet_actuel != None:
                    if aff:
                        lat = sommets.loc[int(sommet_actuel), 'lat']
                        lon = sommets.loc[int(sommet_actuel), 'lon']
                        x2 = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
                        y2 = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
                        c = g.Line(g.Point(x,y), g.Point(x2,y2))
                        c.setWidth(5)
                        c.setFill("red")
                        c.draw(win)
            
            if aff:
                win.getMouse() # Pause to view result
                win.close()    # Close window when done
            return chemin, distances[str(arrivee)]
        
        if aff:
            lat = sommets.loc[int(min_sommet), 'lat']
            lon = sommets.loc[int(min_sommet), 'lon']
            x = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
            y = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
        
        # Explore les voisins du sommet actuel
        for voisin, poids in dicsuccdist[str(min_sommet)]:
            distance = distances[min_sommet] + poids
            
            if aff:
                lat = sommets.loc[int(voisin), 'lat']
                lon = sommets.loc[int(voisin), 'lon']
                x2 = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
                y2 = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
                c = g.Line(g.Point(x,y), g.Point(x2,y2))

            if aff:
                if distance < distances[str(voisin)]:
                    c.setFill("green")
                c.setWidth(1.5)
                c.draw(win)
            
            # Met a jour la distance si la nouvelle distance est plus courte
            if distance < distances[str(voisin)]:
                distances[str(voisin)] = distance
                predecesseurs[str(voisin)] = min_sommet
                # On utilise la distance géographique restante comme heuristique
                heuristique = distanceGPSRapide(sommets.loc[voisin,'lat'],sommets.loc[int(arrivee),'lat'], sommets.loc[voisin,'lon'],sommets.loc[int(arrivee),'lon'])
                # Ajoute le voisin à la file de priorité
                a_traiter.append((distance + heuristique*20, str(voisin)))
                
    # Si le sommet de destination n'est pas accessible à partir du sommet de départ, retourne un chemin vide et une distance infinie
    return [], float('inf')


def main():
    affichageGraphique = True
    while(True):
        print(affichageGraphique)
        choix = input("Faites un choix : \n 0 - Afficher points de départ et arrivee \n 1 - Dijkstra \n 2 - Bellman \n 3 - A* \n 4 - Afficher les points et arcs \n 5 - Quitter \n 6 - Activer / Désactiver le mode graphique (Defaut = oui) \n")
        print("\n")
        
        depart = '10180904249'
        arrivee = '254053905'
        
        match choix:
            case '0':
                if affichageGraphique:
                    win = affichagePts(affichageBG())
                    dessinPtsDepart(depart, arrivee, win)
                    win.getMouse() # Pause to view result
                    win.close()    # Close window when done
                else:
                    print("Veuillez activer le mode graphique")
            case '1' :
                if affichageGraphique:
                    dijkstra(depart, arrivee, affichageGraphique)
                plus_court_chemin, plus_courte_distance = dijkstra(depart, arrivee, False)
                print("Chemin le plus court du sommet", depart, "au sommet", arrivee + ":", plus_court_chemin)
                print("Distance la plus courte :", plus_courte_distance)
            case '2':
                if affichageGraphique:
                    bellman(depart, arrivee, affichageGraphique)
                plus_court_chemin, plus_courte_distance = bellman(depart, arrivee, False)
                print("Chemin le plus court du sommet", depart, "au sommet", arrivee + ":", plus_court_chemin)
                print("Distance la plus courte :", plus_courte_distance)
            case '3':
                if affichageGraphique:
                    AEtoile(depart, arrivee, affichageGraphique)
                plus_court_chemin, plus_courte_distance = AEtoile(depart, arrivee, False)
                print("Chemin le plus court du sommet", depart, "au sommet", arrivee + ":", plus_court_chemin)
                print("Distance la plus courte :", plus_courte_distance)
            case '4':
                if affichageGraphique:
                    win = dessinArcs(affichagePts(affichageBG()))
                    dessinPtsDepart(depart, arrivee, win)
                    win.getMouse() # Pause to view result
                    win.close()    # Close window when done
                else:
                    print("Veuillez activer le mode graphique")
            case '5':
                break
            case '6':
                if affichageGraphique:
                    affichageGraphique = False
                    print("Affichage graphique desactive")
                else:
                    affichageGraphique = True
                    print("Affichage graphique active")
            
    return 0

main()






#%%

del fichier, i, j, val, ls, lst, ind 
