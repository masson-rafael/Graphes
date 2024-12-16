"""
@author : Latxague Thibault / Rafael Masson
"""

#importations de bibliotheques
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import math
import timeit

#choix du repertoire par defaut
os.chdir('C:\\Users\\rafae\\S2\\sae\\sae-s2-02-graphes\\csv')

#importation des dataframes
arcs=pd.read_table('arcs.csv',sep=";",encoding='ANSI')
points=pd.read_table('points.csv',index_col=0,sep=";",encoding='ANSI')


#%% Partie création de fonctions


def obtenirLesPoints(chaine):
    
    c = chaine.replace('[','').split(',')
    points = []
    for i in range(len(c)):
        if i != len(c)-1: #Si on n'est pas déjà à la fin de notre liste
            points.append(int(c[i]))
        else:
            points.append(int(c[i].replace(']',''))) #on modifie le dernier elt sans ] 
    return points
        
def obtenirLesPointsExtremes(chaine):
    #Dans cette partie, on décompose notre chaine en chaine de nombres (sans [, ], et ,)
    c = chaine.replace('[','').split(',')
    points = []
    points.append(int(c[0])) #Le premier elt de la liste
    points.append(int(c[-1].replace(']',''))) #Le dernier elt de la liste
    
    return points


def distanceGPS(latA,latB,longA,longB):
    # Conversions des latitudes en radians
    ltA=latA/180*math.pi
    ltB=latB/180*math.pi
    loA=longA/180*math.pi
    loB=longB/180*math.pi
    
    # Rayon de la terre en mètres 
    RT = 6378137
    
    # angle en radians entre les 2 points
    S = math.acos(round(math.sin(ltA)*math.sin(ltB) + math.cos(ltA)*math.cos(ltB)*math.cos(abs(loB-loA)),20))
    
    # distance entre les 2 points, comptée sur un arc de grand cercle
    return S*RT

def poidsArc(chaine):
    latitude = []
    longitude = []
    distanceTotale = 0

    for point in obtenirLesPoints(chaine):
        latitude.append(points.loc[[point], ['lat']].values[0])
        longitude.append(points.loc[[point], ['lon']].values[0])

    for i in range(len(latitude)-1):
        v = distanceGPS(latitude[i], latitude[i+1], longitude[i], longitude[i+1])
        distanceTotale += v
    
    return distanceTotale

#%% 3 - Le graphe / a -- choix du dataframe plutot que du dictionnaire

#On créé notre nouveau dataframe avec une colonne unique nommée sommet
sommetsUniques = pd.DataFrame(columns=['Sommet'])

#Cette partie permet d'ajouter à notre df un sommet, ssi il n'existe pas déjà dans le df
for lstpoint in arcs['lstpoints']:
    for sommetExt in obtenirLesPointsExtremes(lstpoint):
        if not sommetsUniques['Sommet'].isin([sommetExt]).any():
            sommetsUniques.loc[len(sommetsUniques)] = [sommetExt]
            
sommetsUniques.set_index('Sommet',inplace=True)

#On concatène nos df pour avoir toutes les informations des sommets sélectionnés
sommetsUniques = pd.merge(sommetsUniques, points, left_on='Sommet',right_index=True,how="inner")


#%% 3 - Le graphe / b choix du dataframe et du dictionnaire

arcs['pointsInt'] = pd.Series(dtype=object) #On le définit de type objet pour pouvoir stocker les listes d'int
arcs['pointDeb'] = 0
arcs['pointFin'] = 0

for index in range(len(arcs)):
    chemin = arcs.iloc[index]['lstpoints']
    arcs.at[index, 'pointsInt'] = obtenirLesPoints(chemin)

for index in range(len(arcs)):
    debut = arcs.iloc[index]['pointsInt']
    arcs.at[index, 'pointDeb'] = debut[0]
    arcs.at[index, 'pointFin'] = debut[-1]
    

# Creation d'une variable d'indice pour les sommets utiles au graphe
sommetsUniques['indice'] = 0
i = 0
for sommet in sommetsUniques.index:
    sommetsUniques.at[sommet,'indice'] = i
    i+=1

# Ajout de l'indice aux sommets de depart des arcs
arcs = pd.merge(arcs, sommetsUniques['indice'], left_on='pointDeb',right_index=True,how="left")
# Renommer la colonne indice en indexPointDeb
tmp=list(arcs.columns)
tmp[9]='indicePointDeb'
arcs.columns=tmp

# Ajout de l'indice aux sommets de fin des arcs
arcs = pd.merge(arcs, sommetsUniques['indice'], left_on='pointFin',right_index=True,how="left")
# Renommer la colonne indice en indicePointDeb
tmp=list(arcs.columns)
tmp[10]='indicePointFin'
arcs.columns=tmp



# Initialisation de la matrice d'adjacence avec une liste de listes
matriceAdjLst = [[0 for i in range(len(sommetsUniques))] for j in range(len(sommetsUniques))]
    
# Remplissage de la liste
deb = timeit.default_timer()

for i in arcs.index:
    matriceAdjLst[arcs.loc[i,'indicePointDeb']][arcs.loc[i,'indicePointFin']] = 1
    matriceAdjLst[arcs.loc[i,'indicePointFin']][arcs.loc[i,'indicePointDeb']] = 1
        
fin = timeit.default_timer()
print("Temps d'excution du remplissage de la matrice d'adjacence (liste) matriceAdjLst : ", round(fin-deb,4), " seconde.s")




# Initialisation de la matrice d'adjacence avec un array numpy
matriceAdjArr = np.array([[0 for i in range(len(sommetsUniques))] for j in range(len(sommetsUniques))])
    
# Remplissage de l'array
deb = timeit.default_timer()

for i in arcs.index:
    matriceAdjArr[arcs.loc[i,'indicePointDeb']][arcs.loc[i,'indicePointFin']] = 1
    matriceAdjArr[arcs.loc[i,'indicePointFin']][arcs.loc[i,'indicePointDeb']] = 1
        
fin = timeit.default_timer()
print("Temps d'excution du remplissage de la matrice d'adjacence (array) matriceAdjArr : ", round(fin-deb,4), " seconde.s")




# Initialisation de la matrice d'adjacence avec un DataFrame 
matriceAdjDf = pd.DataFrame(data = int(0), index=sommetsUniques.index, columns=sommetsUniques.index)

# Remplissage du DataFrame
deb = timeit.default_timer()

for i in arcs.index:
    matriceAdjDf.at[arcs.loc[i,'pointDeb'],arcs.loc[i,'pointFin']] = 1
    matriceAdjDf.at[arcs.loc[i,'pointFin'],arcs.loc[i,'pointDeb']] = 1
    
fin = timeit.default_timer()
print("Temps d'excution du remplissage de la matrice d'adjacence (DataFrame) matriceAdjDf : ", round(fin-deb,4), " seconde.s")



# Initialisation du dictionnaire des successeurs reprensentant le graphe
dicoSucc = dict()

for sommet in sommetsUniques.index:
    dicoSucc[sommet] = []
    
# Remplissage du dictionnaire
deb = timeit.default_timer()

for i in range(len(arcs.index)):
    sommetDeb = arcs.loc[i,'pointDeb']
    sommetFin = arcs.loc[i,'pointFin']
    if sommetFin not in dicoSucc[sommetDeb]:
        dicoSucc[sommetDeb].append(sommetFin)
    if sommetDeb not in dicoSucc[sommetFin]:
        dicoSucc[sommetFin].append(sommetDeb)
        
fin = timeit.default_timer()
print("Temps d'excution du remplissage du dictionnaire des successeurs dicoSucc : ", round(fin-deb,4), " seconde.s")


#%% 4 - Le graphe pondere / a - poids des arcs

deb = timeit.default_timer()

arcs['PoidsArc']=0

for index in range(len(arcs)):
    chemin = arcs.iloc[index]['lstpoints']
    arcs.at[index, 'PoidsArc'] = poidsArc(chemin)
    
fin = timeit.default_timer()
print("Temps d'excution du calcul du poids des arcs (arcs['PoidsArc']) : ", round(fin-deb,4), " seconde.s")

#%% 4 - Le graphe pondere / b - representation du graphe pondere


# Initialisation de la matrice des poids avec une liste de listes
matricePoidsLst = [[0 for i in range(len(sommetsUniques))] for j in range(len(sommetsUniques))]
    
# Remplissage de la liste
deb = timeit.default_timer()

for i in arcs.index:
    matricePoidsLst[arcs.loc[i,'indicePointDeb']][arcs.loc[i,'indicePointFin']] = arcs.loc[i,'PoidsArc']
    matricePoidsLst[arcs.loc[i,'indicePointFin']][arcs.loc[i,'indicePointDeb']] = arcs.loc[i,'PoidsArc']
        
fin = timeit.default_timer()
print("Temps d'excution du remplissage de la matrice des poids (liste) matricePoidsLst : ", round(fin-deb,4), " seconde.s")




# Initialisation de la matrice des poids avec un array numpy
matricePoidsArr = np.array([[0 for i in range(len(sommetsUniques))] for j in range(len(sommetsUniques))],dtype=np.float64)
    
# Remplissage de l'array
deb = timeit.default_timer()

for i in arcs.index:
    matricePoidsArr[arcs.loc[i,'indicePointDeb']][arcs.loc[i,'indicePointFin']] = arcs.loc[i,'PoidsArc']
    matricePoidsArr[arcs.loc[i,'indicePointFin']][arcs.loc[i,'indicePointDeb']] = arcs.loc[i,'PoidsArc']
        
fin = timeit.default_timer()
print("Temps d'excution du remplissage de la matrice des poids (array) matricePoidsArr : ", round(fin-deb,4), " seconde.s")




# Initialisation de la matrice des poids avec un DataFrame 
matricePoidsDf = pd.DataFrame(data = float(0), index=sommetsUniques.index, columns=sommetsUniques.index)

# Remplissage de la matrice des poids
deb = timeit.default_timer()

for i in arcs.index:
    matricePoidsDf.at[arcs.loc[i,'pointDeb'],arcs.loc[i,'pointFin']] = arcs.loc[i,'PoidsArc']
    matricePoidsDf.at[arcs.loc[i,'pointFin'],arcs.loc[i,'pointDeb']] = arcs.loc[i,'PoidsArc']
    
fin = timeit.default_timer()
print("Temps d'excution du remplissage de la matrice des poids (DataFrame) matricePoidsDf : ", round(fin-deb,4), " seconde.s")




# Initialisation du dictionnaire des successeurs pondere
dicoPoids = dict()

for sommet in sommetsUniques.index:
    dicoPoids[sommet] = []
    
# Remplissage du dictionnaire
deb = timeit.default_timer()

for i in range(len(arcs.index)):
    sommetDeb = arcs.loc[i,'pointDeb']
    sommetFin = arcs.loc[i,'pointFin']
    poidsArc = arcs.loc[i,'PoidsArc']
    
    test = False
    for couple in dicoPoids[sommetDeb]:
        if sommetFin == couple[0]:
            test = True
    if test == False:
        coupleSomVal = (sommetFin,poidsArc)
        dicoPoids[sommetDeb].append(coupleSomVal)
        
    test = False
    for couple in dicoPoids[sommetFin]:
        if sommetDeb == couple[0]:
            test = True
    if test == False:
        coupleSomVal = (sommetDeb,poidsArc)
        dicoPoids[sommetFin].append(coupleSomVal)
        
fin = timeit.default_timer()
print("Temps d'excution du remplissage du dictionnaire des successeurs pondere dicoPoids : ", round(fin-deb,4), " seconde.s")
