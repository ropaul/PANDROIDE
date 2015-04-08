# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 22:28:41 2015

@author: Yann Ropaul & Margot Calbrix
"""

from gurobipy import *
import random
import numpy as np

################################################################################
#
#                        VARIABLES ET CONSTANTES GLOBALES
#
################################################################################


#Loi de probabilité du coût d'une case
pblanc=0.15
pverte=0.35
pbleue=0.25
prouge=0.15
pnoire=0.10

#taille de la grille
nblignes=5
nbcolonnes=5

#Probabilité d'aller effectivement dans la direction voulue
probaTransition=1

#Visibilité du futur
gamma = 0.9

#poition initiale du robot dans la grille
posX=0
posY=0

# valeurs de la grille
cost= np.zeros(5, dtype=np.int)
weight= np.zeros(5, dtype=np.int)
weight[1] = 1
weight[2] = 2
weight[3] = 3
weight[4] = 4

#directions
HAUT = 0
BAS = 1
GAUCHE = 2
DROITE = 3



################################################################################
#
#                           FONCTIONS DE DEFINITION DU PROBLEME
#
################################################################################

#Définit un labyrinthe de nblignes lignes et nbcolonnes colonnes
#Retourne g, le labyrinthe (sous la forme d'un tableau à deux dimensions)
def defineMaze(nblignes,nbcolonnes):
    g= np.zeros((nblignes,nbcolonnes), dtype=np.int)
    for i in range(nblignes):
        for j in range(nbcolonnes):
            z=np.random.uniform(0,1)
            if z < pblanc:
                g[i,j]=0
            else:
                if z < pblanc + pverte:
                    g[i,j]=weight[1]
                else:
                    if z < pblanc + pverte + pbleue:
                        g[i,j]=weight[2]
                    else:
                        if z< pblanc + pverte + pbleue + prouge:
                            g[i,j]=weight[3]
                        else:
                            g[i,j]=weight[4]
    
    #A REMPLACER PAR UNE FONCTION DE TEST D'INTEGRITE DU LABYRINTHE
    g[0,0]=np.random.random_integers(3)
    g[0,1]=np.random.random_integers(3)
    g[2,0]=np.random.random_integers(3)     
    g[nblignes-1,nbcolonnes-1]=np.random.random_integers(3)
    g[nblignes-2,nbcolonnes-1]=np.random.random_integers(3)
    g[nblignes-1,nbcolonnes-2]=np.random.random_integers(3)

    #Case but
    #g[nblignes-1][nbcolonnes-1]=-1000
    
    return g


#Calcule la loi de probabilité de transition pour une action direction et une position (i, j) données.
#Retourne trans, la loi de probabilité sous la forme d'un dictionnaire
#Note : si une position n'appartient pas au dictionnaire, alors la probabilité d'aller dans cette position est nulle.
def transition(g, direction, i, j, probaTransition):
    trans = {}
    if g[i,j] != 0:
        if direction == GAUCHE and j > 0:
            if g[i, j-1] != 0:
                if (i-1 < 0 or g[i-1, j-1] == 0) and (i+1 > nblignes-1 or g[i+1, j-1]==0)  :
                    trans[i, j-1] = 1
                else:
                    if i-1 < 0 or g[i-1,j-1] == 0:
                        trans[i, j-1] = (1 + probaTransition)/2
                        trans[i+1, j-1] = (1 - probaTransition)/2
                    else:
                        if i+1 > nblignes-1 or g[i+1,j-1] == 0:
                            trans[i, j-1] = (1 + probaTransition)/2
                            trans[i-1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i, j-1] = probaTransition
                            trans[i-1, j-1] = (1 - probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
        if direction == DROITE and j < nbcolonnes-1:
            if g[i, j+1] != 0:
                if (i-1 < 0 or g[i-1, j+1] == 0) and (i+1 > nblignes-1 or g[i+1, j+1]==0):
                    trans[i, j+1] = 1
                else:
                    if i-1 < 0 or g[i-1,j+1] == 0:
                        trans[i, j+1] = (1 + probaTransition)/2
                        trans[i+1, j+1] = (1 - probaTransition)/2
                    else:
                        if i+1 > nblignes-1 or g[i+1,j+1] == 0:
                            trans[i, j+1] = (1 + probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
                        else:
                            trans[i, j+1] = probaTransition
                            trans[i+1, j+1] = (1 - probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
        if direction == HAUT and i > 0: 
            if g[i-1, j] != 0:
                if (j-1 < 0 or g[i-1, j-1] == 0) and (j+1 > nbcolonnes-1 or g[i-1, j+1] == 0):
                    trans[i-1, j] = 1
                else:
                    if j-1 < 0 or g[i-1, j-1] == 0:
                        trans[i-1, j] = (1 + probaTransition)/2
                        trans[i-1, j+1] = (1 - probaTransition)/2
                    else:
                        if j+1 > nbcolonnes-1 or g[i-1, j+1] == 0:
                            trans[i-1, j] = (1 + probaTransition)/2
                            trans[i-1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i-1, j] = probaTransition
                            trans[i-1, j-1] = (1 - probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
        if direction == BAS and i < nblignes-1:
            if g[i+1, j] != 0:
                if (j-1 < 0 or g[i+1, j-1] == 0) and (j+1 > nbcolonnes-1 or g[i+1, j+1] == 0)  :
                    trans[i+1, j] = 1
                else:
                    if j-1 < 0 or g[i+1, j-1] == 0:
                        trans[i+1, j] = (1 + probaTransition)/2
                        trans[i+1, j+1] = (1 - probaTransition)/2
                    else:
                        if j+1 > nbcolonnes-1 or g[i+1, j+1] == 0:
                            trans[i+1, j] = (1 + probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i+1, j] = probaTransition
                            trans[i+1, j+1] = (1 - probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
    return trans



################################################################################
#
#                            FONCTIONS DE RESOLUTION (INTERFACE GUROBI)
#
################################################################################


def programmeprimal(grille, gamma, proba):
    #Matrice des contraintes + second membre
    A = np.zeros((nblignes*nbcolonnes*4, nblignes*nbcolonnes))
    b = np.zeros(nblignes*nbcolonnes*4)
    for i in range(nblignes):
        for j in range(nbcolonnes):
            for k in range (4):
                b[(i*nbcolonnes+j)*4+k]=-grille[i][j]
                #Valeur de la case d'arrivée
                if (i == (nblignes - 1) and j == (nbcolonnes -1)):
                    #A changer si on veut maximiser
                    b[(i*nbcolonnes+j)*4+k]=1000
                A[(i*nbcolonnes+j)*4+k][i*nbcolonnes+j]=1
                trans = transition(grille, k, i, j, proba)
                for t in trans:
                    A[(i*nbcolonnes+j)*4+k][t[0]*nbcolonnes+t[1]]=-gamma*trans[t]

    #fonction objectif
    obj = np.zeros(nblignes*nbcolonnes)
    obj[0] = 1

    return (A, b, obj)


def resolutionGurobiprimal(a,b,objectif):
    m = Model("PDM")     
        
    # declaration variables de decision
    v = []
    for i in range(nblignes*nbcolonnes):
        v.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="v%d" % (i+1)))
    
    # maj du modele pour integrer les nouvelles variables
    m.update()

    obj = LinExpr();
    obj =0
    for i in range(len(objectif)):
        obj += objectif[i]*v[i]

    # definition de l'objectif
    m.setObjective(obj,GRB.MINIMIZE)

    # definition des contraintes
    for i in range(nblignes*nbcolonnes*4):
        m.addConstr(quicksum(a[i][j]*v[j] for j in range(nblignes*nbcolonnes)) >= b[i], "Contrainte%d" % i)

    # Resolution
    m.optimize()
    #tempsde résolution (-0.01 pour compenser le temps d'exécution de la ligne suivante)
    t = m.getAttr(GRB.Attr.Runtime) - 0.01
    
    return v, m, t


def politique(valeurs, grille, proba, gamma):
    pol = np.zeros((nblignes, nbcolonnes))
    for i in range (nblignes):
        for j in range (nbcolonnes):
            maximum = 0
            for k in range (4):
                temp = grille[j][i]
                trans = transition(grille, k, i, j, proba)
                for t in trans:
                    temp += gamma * trans[t] * valeurs[t[0]*nblignes+t[1]].x
                if ( maximum < temp ):
                    maximum = temp
                    pol[i][j] = k
    return pol

def resolution(grille, gamma, proba):
    (A, b, obj) = programmeprimal(grille, gamma, proba)
    v, m, t = resolutionGurobiprimal(A, b, obj)
    pol = politique(v, grille, proba, gamma)
    return pol


################################################################################
#
#                            FONCTIONS DE TESTS
#
################################################################################

def coutChemin(grille, politique):
    cout = 0
    i = 0
    j = 0
    #cout += grille[i][j]
    #la première case ne coute rien
    while i != grille.shape[0]-1 and j != grille.shape[1]-1:
        if politique[i][j] == HAUT:
            i -= 1
        elif politique[i][j] == BAS:
            i += 1
        elif politique[i][j] == GAUCHE:
            j -= 1
        else: #politique[i][j] == DROITE
            j += 1
        cout += grille[i][j]
    return cout

#Teste la perte de capacité de l'algorithme à trouver une solution optimale
#avec la probabilité de transition proba au lieu de 1 (plus court chemin trouvé)
def comparePerformanceProba(nblignes, nbcolonnes, gamma, proba, nbIter):
    moyDiff = 0
    moyRatio = 0
    for i in range(nbIter):
        g = defineMaze(nblignes, nbcolonnes)
        cout = coutChemin(g, resolution(g, gamma, proba))
        coutObj = coutChemin(g, resolution(g, gamma, 1))
        moyDiff += cout - coutObj
        moyRatio += cout/float(coutObj)
    moyDiff = moyDiff / float(nbIter)
    moyRatio = moyRatio / float(nbIter)
    return moyDiff, moyRatio

#Compare la qualité des solutions trouvées en fonction de gamma
def comparePerformanceGamma(nblignes, nbcolonnes, nbIter, pas, proba):
    moy = [0 for i in np.arange(0, 1.001, pas)]
    tmp = gamma
    for i in range(nbIter):
        g = defineMaze(nblignes, nbcolonnes)
        for j in range(len(moy)):
            gamma = j*pas
            cout = coutChemin(g, resolution(g, gamma, proba))
            moy[j] += cout
    for i in range(len(moy)):
        moy[i] /= nbIter
    return moy
            



################################################################################
#
#                            PROGRAMME PRINCIPAL
#
################################################################################


g = defineMaze(nblignes, nbcolonnes)
print g

##(A, b, obj) = programmeprimal(g, gamma)
##v, m, t = resolutionGurobiprimal(A, b, obj)
##print "runtime"
##print t
##print "nbIter"
##print m.getAttr(GRB.Attr.IterCount)
##pol = politique(v, g)
##print "pol :"
##print pol
"""
pol = resolution(g, gamma)
print pol
cout = coutChemin(g, pol)
print "cout 1"
print cout
probaTransition = 0.1
pol = resolution(g, gamma)
print pol
cout = coutChemin(g, pol)
print "cout 2"
print cout"""


#Test fonction de test
moyD, moyR = comparePerformanceProba(nblignes, nbcolonnes, gamma, 0.1, 10)
print moyD
print moyR


