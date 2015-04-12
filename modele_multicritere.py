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


#probabilité d'un mur
pmur = 0.15

#taille de la grille
nblignes=5
nbcolonnes=5

#nombre de critères
nbcriteres=4

#Probabilité d'aller effectivement dans la direction voulue
probaTransition=1

#Visibilité du futur
gamma = 0.9

#poition initiale du robot dans la grille
posX=0
posY=0

# valeurs de la grille
weight = range(1,10)

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
#Retourne g, le labyrinthe (sous la forme d'un tableau à trois dimensions)
def defineMaze(nblignes,nbcolonnes,nbcriteres):
    random.seed()
    g= np.zeros((nblignes,nbcolonnes,nbcriteres), dtype=np.int)
    for i in range(nblignes):
        for j in range(nbcolonnes):
            z=np.random.uniform(0,1)
            if z < pmur:
                g[i,j] = np.zeros(nbcriteres, dtype=np.int)
            if z > pmur:
                for k in range (nbcriteres):
                    g[i,j,k] = random.choice(weight)
    
    #AJOUTER UNE FONCTION DE TEST D'INTEGRITE DU LABYRINTHE
    for k in range(nbcriteres):
        g[0,0,k] = random.choice(weight)
        g[nblignes-1,nbcolonnes-1,k] = random.choice(weight)
    
    return g


#Calcule la loi de probabilité de transition pour une action direction et une position (i, j) données.
#Retourne trans, la loi de probabilité sous la forme d'un dictionnaire
#Note : si une position n'appartient pas au dictionnaire, alors la probabilité d'aller dans cette position est nulle.
def transition(g, direction, i, j, probaTransition, nbcriteres):
    trans = {}
    vzero = np.zeros(nbcriteres, dtype=np.int)
    if not np.array_equal(g[i,j], vzero):
        if direction == GAUCHE and j > 0:
            if  not np.array_equal(g[i, j-1], vzero):
                if (i-1 < 0 or np.array_equal(g[i-1, j-1], vzero)) and (i+1 > nblignes-1 or np.array_equal(g[i+1, j-1], vzero)):
                    trans[i, j-1] = 1
                else:
                    if i-1 < 0 or np.array_equal(g[i-1,j-1], vzero):
                        trans[i, j-1] = (1 + probaTransition)/2
                        trans[i+1, j-1] = (1 - probaTransition)/2
                    else:
                        if i+1 > nblignes-1 or np.array_equal(g[i+1,j-1], vzero):
                            trans[i, j-1] = (1 + probaTransition)/2
                            trans[i-1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i, j-1] = probaTransition
                            trans[i-1, j-1] = (1 - probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
        if direction == DROITE and j < nbcolonnes-1:
            if not np.array_equal(g[i, j+1], vzero):
                if (i-1 < 0 or np.array_equal(g[i-1, j+1], vzero)) and (i+1 > nblignes-1 or np.array_equal(g[i+1, j+1], vzero)):
                    trans[i, j+1] = 1
                else:
                    if i-1 < 0 or np.array_equal(g[i-1,j+1], vzero):
                        trans[i, j+1] = (1 + probaTransition)/2
                        trans[i+1, j+1] = (1 - probaTransition)/2
                    else:
                        if i+1 > nblignes-1 or np.array_equal(g[i+1,j+1], vzero):
                            trans[i, j+1] = (1 + probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
                        else:
                            trans[i, j+1] = probaTransition
                            trans[i+1, j+1] = (1 - probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
        if direction == HAUT and i > 0: 
            if not np.array_equal(g[i-1, j], vzero):
                if (j-1 < 0 or np.array_equal(g[i-1, j-1], vzero)) and (j+1 > nbcolonnes-1 or np.array_equal(g[i-1, j+1], vzero)):
                    trans[i-1, j] = 1
                else:
                    if j-1 < 0 or np.array_equal(g[i-1, j-1], vzero):
                        trans[i-1, j] = (1 + probaTransition)/2
                        trans[i-1, j+1] = (1 - probaTransition)/2
                    else:
                        if j+1 > nbcolonnes-1 or np.array_equal(g[i-1, j+1], vzero):
                            trans[i-1, j] = (1 + probaTransition)/2
                            trans[i-1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i-1, j] = probaTransition
                            trans[i-1, j-1] = (1 - probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
        if direction == BAS and i < nblignes-1:
            if not np.array_equal(g[i+1, j], vzero):
                if (j-1 < 0 or np.array_equal(g[i+1, j-1], vzero)) and (j+1 > nbcolonnes-1 or np.array_equal(g[i+1, j+1], vzero)):
                    trans[i+1, j] = 1
                else:
                    if j-1 < 0 or np.array_equal(g[i+1, j-1], vzero):
                        trans[i+1, j] = (1 + probaTransition)/2
                        trans[i+1, j+1] = (1 - probaTransition)/2
                    else:
                        if j+1 > nbcolonnes-1 or np.array_equal(g[i+1, j+1], vzero):
                            trans[i+1, j] = (1 + probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i+1, j] = probaTransition
                            trans[i+1, j+1] = (1 - probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
    return trans



################################################################################
#
#            FONCTIONS DE RESOLUTION (OBJECTIF = SOMME DES CRITERES)
#
################################################################################

def dualSomme(grille, gamma, proba):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    #Matrice des contraintes + second membre
    A = np.zeros((nbL*nbC*(4+1), nbL*nbC*4))
    b = np.zeros(nbL*nbC*(4+1))
    for i in range(nbL):
        for j in range(nbC):
            b[i*nbC+j]=0
            for k in range(4):
                A[i*nbC+j][(i*nbC+j)*4+k] = 1
                A[(nbL*nbC+(i*nbC+j))*4+k][(i*nbC+j)*4+k]=1
                b[(nbL*nbC+(i*nbC+j))*4+k]=0
                #rajoute les -gamma sur les autres lignes
                trans=transition(grille, k, i, j, proba)
                for t in trans:
                    A[t[0]*nbC+t[1]][(i*nbC+j)*4+k]=-gamma*trans[t]
    b[0]=1

    #fonction objectif
    obj = np.zeros(nbL*nbC*4)
    for i in range(nbL):
        for j in range(nbC):
            for k in range(4):
                obj[(i*nbC+j)*4+k] = sum(grille[i,j])

    return (A, b, obj)
                
                
def gurobiMultiSomme(a, b, objectif):
    m = Model("MOPDM")
    #déclaration des variables de décision
    v = []
    for i in range(len(b)):
        v.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x%d" % (i+1)))
    #màj du modèle pour intégrer les nouvelles variables
    m.update()
    #définition de l'objectif
    obj = LinExpr()
    obj = 0
    for i in range(len(objectif)):
        obj += objectif[i]*v[i]
    m.setObjective(obj,GRB.MAXIMIZE)
    #définition des contraintes
    for i in range(a.shape[0]):
        m.addConstr(quicksum(a[i][j]*v[j] for j in range(a.shape[1])) <= b[i], "Contrainte%d" % i)
    #résolution
    m.optimize()
    #temps de résolution (-0.01 pour compenser le temps d'exécution de la ligne suivante)
    t = m.getAttr(GRB.Attr.Runtime) - 0.01

    return v, m, t


def politiqueSomme(valeurs, grille):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    pol = np.zeros((nbL,nbC,4))
    for i in range(nbL):
        for j in range(nbC):
            for k in range(4):
                pol[i][j][k] = valeurs[(i*nbC+j)*4+k].x
            somme = sum(pol[i][j])
            for k in range(4):
                pol[i][j][k] /= somme
    return pol

def resolutionMultiSomme(grille, gamma, proba):
    (A, b, obj) = dualSomme(grille, gamma, proba)
    v, m, t = gurobiMultiSomme(A, b, obj)
    pol = politiqueSomme(v, grille)
    return pol


            
################################################################################
#
#                            PROGRAMME PRINCIPAL
#
################################################################################


g=defineMaze(3,3,2)
print g
t = transition(g, BAS, 1,1, probaTransition, 2)
print t
