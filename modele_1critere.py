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
nblignes=3
nbcolonnes=3

#Probabilité d'aller effectivement dans la direction voulue
probaTransition=0.5

#Visibilité du futur
gamma = 0.8

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
    g[nblignes-1][nbcolonnes-1]=-1000
    
    return g


#Calcule la loi de probabilité de transition pour une action direction et une position (i, j) données.
#Retourne trans, la loi de probabilité sous la forme d'un dictionnaire
#Note : si une position n'appartient pas au dictionnaire, alors la probabilité d'aller dans cette position est nulle.
def transition(g, direction, i, j):
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


def programmeprimal(grille, gamma):
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
                trans = transition(grille, k, i, j)
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

    return v, m


def politique(valeurs,grille):
    pol = np.zeros((nblignes, nbcolonnes))
    for i in range (nblignes):
        for j in range (nbcolonnes):
            maximum = 0
            for k in range (4):
                temp = grille[j][i]
                trans = transition(grille, k, i, j)
                for t in trans:
                    temp += gamma * trans[t] * valeurs[t[0]*nblignes+t[1]].x
                if ( maximum < temp ):
                    maximum = temp
                    pol[i][j] = k
    return pol



################################################################################
#
#                            PROGRAMME PRINCIPAL
#
################################################################################

"""
##g = defineMaze(10,10)
##print g
g = np.ones((nblignes,nbcolonnes), dtype=np.int)
g[0,1] = 4
g[0,2] = 4
g[2,0] = 4
g[2,1] = 4
print g
(A, b, obj) = programmeprimal(g, gamma)
print "####"
print A
print b
print obj

v, m = resolutionGurobiprimal(A, b, obj)
print v
##for i in range(nblignes):
##        s= []
##        for j in range(nbcolonnes):
##            print v[j].x
##        print s

pol = politique(v, g)
print "pol :"
print pol
"""
