# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 2015

@author: Yann Ropaul & Margot Calbrix
"""

from gurobipy import *
import random
import numpy as np
import time

################################################################################
#
#                        VARIABLES ET CONSTANTES GLOBALES
#
################################################################################


#probabilité d'un mur
pmur = 0.15

#taille de la grille
nblignes=10
nbcolonnes=10

#nombre de critères
nbcriteres=4

#Probabilité d'aller effectivement dans la direction voulue
probaTransition=1

#Visibilité du futur
gamma = 0.5

#poition initiale du robot dans la grille
posX=0
posY=0

#cout de la grille
cost= np.zeros(nbcriteres+1, dtype=np.int)

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

#Parcourt la grille en largeur pour savoir si le but est accessible depuis le point de départ
def estFinissable(grille):
    explores = set()
    aexplorer = [(0,0)]
    while not not aexplorer: #tant que aexplorer n'est pas vide
        case = aexplorer.pop(0)
        explores.add(case)
        for d in range(4):
            trans = transition(grille, d, case[0], case[1], 1, grille.shape[2])
            for t in trans:
                if t == (grille.shape[0]-1, grille.shape[1]-1):
                    return True
                if not (t in explores):
                    aexplorer.append(t)
    return False
    
    

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
    for k in range(nbcriteres):
        g[0,0,k] = random.choice(weight)
        g[nblignes-1,nbcolonnes-1,k] = random.choice(weight)
        
    while not estFinissable(g):
        g= np.zeros((nblignes,nbcolonnes,nbcriteres), dtype=np.int)
        for i in range(nblignes):
            for j in range(nbcolonnes):
                z=np.random.uniform(0,1)
                if z < pmur:
                    g[i,j] = np.zeros(nbcriteres, dtype=np.int)
                if z > pmur:
                    for k in range (nbcriteres):
                        g[i,j,k] = random.choice(weight)
        
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
    nbL=g.shape[0]
    nbC=g.shape[1]
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
                        if i+1 > nbL-1 or np.array_equal(g[i+1,j-1], vzero):
                            trans[i, j-1] = (1 + probaTransition)/2
                            trans[i-1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i, j-1] = probaTransition
                            trans[i-1, j-1] = (1 - probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
        if direction == DROITE and j < nbC-1:
            if not np.array_equal(g[i, j+1], vzero):
                if (i-1 < 0 or np.array_equal(g[i-1, j+1], vzero)) and (i+1 > nbL-1 or np.array_equal(g[i+1, j+1], vzero)):
                    trans[i, j+1] = 1
                else:
                    if i-1 < 0 or np.array_equal(g[i-1,j+1], vzero):
                        trans[i, j+1] = (1 + probaTransition)/2
                        trans[i+1, j+1] = (1 - probaTransition)/2
                    else:
                        if i+1 > nbL-1 or np.array_equal(g[i+1,j+1], vzero):
                            trans[i, j+1] = (1 + probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
                        else:
                            trans[i, j+1] = probaTransition
                            trans[i+1, j+1] = (1 - probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
        if direction == HAUT and i > 0: 
            if not np.array_equal(g[i-1, j], vzero):
                if (j-1 < 0 or np.array_equal(g[i-1, j-1], vzero)) and (j+1 > nbC-1 or np.array_equal(g[i-1, j+1], vzero)):
                    trans[i-1, j] = 1
                else:
                    if j-1 < 0 or np.array_equal(g[i-1, j-1], vzero):
                        trans[i-1, j] = (1 + probaTransition)/2
                        trans[i-1, j+1] = (1 - probaTransition)/2
                    else:
                        if j+1 > nbC-1 or np.array_equal(g[i-1, j+1], vzero):
                            trans[i-1, j] = (1 + probaTransition)/2
                            trans[i-1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i-1, j] = probaTransition
                            trans[i-1, j-1] = (1 - probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
        if direction == BAS and i < nbL-1:
            if not np.array_equal(g[i+1, j], vzero):
                if (j-1 < 0 or np.array_equal(g[i+1, j-1], vzero)) and (j+1 > nbC-1 or np.array_equal(g[i+1, j+1], vzero)):
                    trans[i+1, j] = 1
                else:
                    if j-1 < 0 or np.array_equal(g[i+1, j-1], vzero):
                        trans[i+1, j] = (1 + probaTransition)/2
                        trans[i+1, j+1] = (1 - probaTransition)/2
                    else:
                        if j+1 > nbC-1 or np.array_equal(g[i+1, j+1], vzero):
                            trans[i+1, j] = (1 + probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i+1, j] = probaTransition
                            trans[i+1, j+1] = (1 - probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
    return trans


def politique(valeurs, grille):
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



################################################################################
#
#            FONCTIONS DE RESOLUTION (OBJECTIF = SOMME DES CRITERES)
#
################################################################################

def dualSomme(grille, gamma, proba, nbCriteres):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    #Matrice des contraintes + second membre
    A = np.zeros((nbL*nbC*(4+1), nbL*nbC*4))
    b = np.zeros(nbL*nbC*(4+1))
    for i in range(nbL):
        for j in range(nbC):
            #b[i*nbC+j]=0
            #test
            b[i*nbC+j]=1
            for k in range(4):
                A[i*nbC+j][(i*nbC+j)*4+k] = 1
                A[nbL*nbC+((i*nbC+j)*4+k)][(i*nbC+j)*4+k]=1
                b[nbL*nbC+((i*nbC+j)*4+k)]=0
                #rajoute les -gamma sur les autres lignes
                trans=transition(grille, k, i, j, proba, nbCriteres)
                for t in trans:
                    A[t[0]*nbC+t[1]][(i*nbC+j)*4+k]=-gamma*trans[t]
    #b[0]=1

    #fonction objectif
    obj = np.zeros(nbL*nbC*4)
    for i in range(nbL):
        for j in range(nbC):
            for k in range(4):
                obj[(i*nbC+j)*4+k] = sum(grille[i,j])
    #case d'arrivée
    for k in range(4):
        obj[(nbL*nbC-1)*4+k] = -100000

    return (A, b, obj)
                
                
def gurobiMultiSomme(a, b, objectif, nblignes, nbcolonnes):
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
    m.setObjective(obj,GRB.MINIMIZE)
    #définition des contraintes
    
    for i in range(nblignes*nbcolonnes):
        m.addConstr(quicksum(a[i][j]*v[j] for j in range(a.shape[1])) <= b[i], "Contrainte%d" % i)
    for i in range(nblignes*nbcolonnes,a.shape[0]):
        m.addConstr(quicksum(a[i][j]*v[j] for j in range(a.shape[1])) >= b[i], "Contrainte%d" % i)
        
    #résolution
    
    m.optimize()
    #temps de résolution (-0.01 pour compenser le temps d'exécution de la ligne suivante)
    t = m.getAttr(GRB.Attr.Runtime) - 0.01

    return v, m, t




def resolutionMultiSomme(grille, gamma, proba, nbCriteres, nblignes, nbcolonnes):
    (A, b, obj) = dualSomme(grille, gamma, proba, nbCriteres)
    v, m, t = gurobiMultiSomme(A, b, obj, nblignes, nbcolonnes)
    pol = politique(v, grille)
    return pol



################################################################################
#
#            FONCTIONS DE RESOLUTION (OBJECTIF = CRITERE EQUITABLE)
#
################################################################################

def dualMinMax(grille, gamma, proba, nbCriteres):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    #Matrice des contraintes + second membre
    A = np.zeros((nbL*nbC*(4+1)+nbCriteres, nbL*nbC*4+1))
    b = np.zeros(nbL*nbC*(4+1)+nbCriteres)
    for i in range(nbL):
        for j in range(nbC):
            b[i*nbC+j]=1
            for k in range(4):
                A[i*nbC+j][(i*nbC+j)*4+k] = 1
                A[nbL*nbC+((i*nbC+j)*4+k)][(i*nbC+j)*4+k]=1
                b[nbL*nbC+((i*nbC+j)*4+k)]=0
                #rajoute les -gamma sur les autres lignes
                trans=transition(grille, k, i, j, proba, nbCriteres)
                for t in trans:
                    A[t[0]*nbC+t[1]][(i*nbC+j)*4+k]=-gamma*trans[t]
                for n in range(nbCriteres):
                    if i == nbL-1 and j == nbC-1:
                        A[nbL*nbC*5+n][(i*nbC+j)*4+k]=-100
                    else:
                        A[nbL*nbC*5+n][(i*nbC+j)*4+k]=-grille[i][j][n]
                    #test
                    #A[nbL*nbC*5+n][(i*nbC+j)*4+k]=grille[i][j][n]
    for n in range(nbCriteres):
        A[nbL*nbC*5+n][nbL*nbC*4]=1
        b[nbL*nbC*5+n]=0

    #fonction objectif
    obj = np.zeros(nbL*nbC*4+1)
    obj[nbL*nbC*4]=1
    

    return (A, b, obj)
                
                
def gurobiMultiMinMax(a, b, objectif, nblignes, nbcolonnes):
    m = Model("MOPDMeq")
    #déclaration des variables de décision
    v = []
    for i in range(len(b)-1):
        v.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x%d" % (i+1)))
    v.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="z"))
    #màj du modèle pour intégrer les nouvelles variables
    m.update()
    #définition de l'objectif
    obj = LinExpr()
    obj = 0
    for i in range(len(objectif)):
        obj += objectif[i]*v[i]
    m.setObjective(obj,GRB.MAXIMIZE)
    
    #définition des contraintes
    #CA PREND TROP DE TEMPS!!!!
    t = time.time()
    for i in range(nblignes*nbcolonnes):
        #A VERIFIER : LEQUEL MARCHE MIEUX
        m.addConstr(quicksum(a[i][j]*v[j] for j in range(a.shape[1])) == b[i], "Contrainte%d" % i)
        #m.addConstr(quicksum(a[i][j]*v[j] for j in range(a.shape[1])) <= b[i], "Contrainte%d" % i)
    for i in range(nblignes*nbcolonnes,nblignes*nbcolonnes*5):
        m.addConstr(quicksum(a[i][j]*v[j] for j in range(a.shape[1])) >= b[i], "Contrainte%d" % i)
    for i in range(nblignes*nbcolonnes*5, a.shape[0]):
        m.addConstr(quicksum(a[i][j]*v[j] for j in range(a.shape[1])) <= b[i], "Contrainte%d" % i)
    print "time : " + str(time.time() - t)   
    #résolution
    m.optimize()
    
    #temps de résolution (-0.01 pour compenser le temps d'exécution de la ligne suivante)
    t = m.getAttr(GRB.Attr.Runtime) - 0.01

    return v, m, t


def resolutionMultiMinMax(grille, gamma, proba, nbCriteres, nblignes, nbcolonnes):
    (A, b, obj) = dualMinMax(grille, gamma, proba, nbCriteres)
    v, m, t = gurobiMultiMinMax(A, b, obj, nblignes, nbcolonnes)
    pol = politique(v, grille)
    return pol

            
################################################################################
#
#                            PROGRAMME PRINCIPAL
#
################################################################################


#g=defineMaze(nblignes,nbcolonnes,nbcriteres)
#print g
g = np.zeros((3,3,2))
g[0,0,0]=1
g[0,1,0]=1
g[0,2,0]=1
g[1,0,0]=1
g[1,1,0]=1
g[2,0,0]=1
g[2,2,0]=1
##g[0,1,0]=0
##g[0,1,1]=40
##g[0,2,0]=0
##g[0,2,1]=40
##g[1,0,1]=0
##g[1,0,0]=40
##g[1,2,1]=40
##g[1,2,0]=0
##g[2,0,1]=0
##g[2,0,0]=40
##g[2,1,1]=0
##g[2,1,0]=40
print g
print estFinissable(g)
#pol = resolutionMultiMinMax(g, gamma, probaTransition, nbcriteres, nblignes, nbcolonnes)
#pol = resolutionMultiMinMax(g, gamma, probaTransition, 2,3,3)
#print pol
"""
(A, b, obj) = dualSomme(g, gamma, probaTransition, nbcriteres)
##print A
##print b
##print obj
v, m, t = gurobiMultiSomme(A, b, obj, nblignes, nbcolonnes)
##for i in range(len(v)):
##    print v[i].x
pol = politique(v, g)
print pol"""


##pol = resolutionMultiSomme(g,gamma,probaTransition, nbcriteres, nblignes, nbcolonnes)
##print pol
