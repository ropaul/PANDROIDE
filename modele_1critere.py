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
probaTransition=0.8

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

#Parcourt la grille en largeur pour savoir si le but est accessible depuis le point de départ
def estFinissable(grille):
    explores = set()
    aexplorer = [(0,0)]
    explores.add((0,0))
    while aexplorer: #tant que aexplorer n'est pas vide
        case = aexplorer.pop(0)
        for d in range(4):
            trans = transition(grille, d, case[0], case[1], 1)
            for t in trans:
                if t == (grille.shape[0]-1, grille.shape[1]-1):
                    return True
                if not (t in explores):
                    aexplorer.append(t)
                    explores.add(t)
    return False

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
    g[0,0]=random.choice(weight[1:])    
    g[nblignes-1,nbcolonnes-1]=random.choice(weight[1:])

    while not estFinissable(g):
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
        g[0,0]=random.choice(weight[1:])    
        g[nblignes-1,nbcolonnes-1]=random.choice(weight[1:])
    
    return g


#Calcule la loi de probabilité de transition pour une action direction et une position (i, j) données.
#Retourne trans, la loi de probabilité sous la forme d'un dictionnaire
#Note : si une position n'appartient pas au dictionnaire, alors la probabilité d'aller dans cette position est nulle.
def transition(g, direction, i, j, probaTransition):
    nbl=g.shape[0]
    nbc=g.shape[1]
    trans = {}
    if g[i,j] != 0:
        if direction == GAUCHE and j > 0:
            if g[i, j-1] != 0:
                if (i-1 < 0 or g[i-1, j-1] == 0) and (i+1 > nbl-1 or g[i+1, j-1]==0)  :
                    trans[i, j-1] = 1
                else:
                    if i-1 < 0 or g[i-1,j-1] == 0:
                        trans[i, j-1] = (1 + probaTransition)/2
                        trans[i+1, j-1] = (1 - probaTransition)/2
                    else:
                        if i+1 > nbl-1 or g[i+1,j-1] == 0:
                            trans[i, j-1] = (1 + probaTransition)/2
                            trans[i-1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i, j-1] = probaTransition
                            trans[i-1, j-1] = (1 - probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
        if direction == DROITE and j < nbc-1:
            if g[i, j+1] != 0:
                if (i-1 < 0 or g[i-1, j+1] == 0) and (i+1 > nbl-1 or g[i+1, j+1]==0):
                    trans[i, j+1] = 1
                else:
                    if i-1 < 0 or g[i-1,j+1] == 0:
                        trans[i, j+1] = (1 + probaTransition)/2
                        trans[i+1, j+1] = (1 - probaTransition)/2
                    else:
                        if i+1 > nbl-1 or g[i+1,j+1] == 0:
                            trans[i, j+1] = (1 + probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
                        else:
                            trans[i, j+1] = probaTransition
                            trans[i+1, j+1] = (1 - probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
        if direction == HAUT and i > 0: 
            if g[i-1, j] != 0:
                if (j-1 < 0 or g[i-1, j-1] == 0) and (j+1 > nbc-1 or g[i-1, j+1] == 0):
                    trans[i-1, j] = 1
                else:
                    if j-1 < 0 or g[i-1, j-1] == 0:
                        trans[i-1, j] = (1 + probaTransition)/2
                        trans[i-1, j+1] = (1 - probaTransition)/2
                    else:
                        if j+1 > nbc-1 or g[i-1, j+1] == 0:
                            trans[i-1, j] = (1 + probaTransition)/2
                            trans[i-1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i-1, j] = probaTransition
                            trans[i-1, j-1] = (1 - probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
        if direction == BAS and i < nbl-1:
            if g[i+1, j] != 0:
                if (j-1 < 0 or g[i+1, j-1] == 0) and (j+1 > nbc-1 or g[i+1, j+1] == 0)  :
                    trans[i+1, j] = 1
                else:
                    if j-1 < 0 or g[i+1, j-1] == 0:
                        trans[i+1, j] = (1 + probaTransition)/2
                        trans[i+1, j+1] = (1 - probaTransition)/2
                    else:
                        if j+1 > nbc-1 or g[i+1, j+1] == 0:
                            trans[i+1, j] = (1 + probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i+1, j] = probaTransition
                            trans[i+1, j+1] = (1 - probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
    return trans

def valBut(nblignes, nbcolonnes):
    return nblignes*nbcolonnes*20

################################################################################
#
#                            FONCTIONS DE RESOLUTION (INTERFACE GUROBI)
#
################################################################################

def programmeprimal(grille, gamma, proba):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    #Matrice des contraintes + second membre
    A = np.zeros(((nbL*nbC+1)*4, nbL*nbC+1))
    b = np.zeros((nbL*nbC+1)*4)
    for i in range(nbL):
        for j in range(nbC):
            for k in range(4):
                b[(i*nbC+j)*4+k] = -grille[i][j]
                A[(i*nbC+j)*4+k][i*nbC+j] = 1
                #Case d'arrivée
                if (i == (nbL-1) and j == (nbC-1)):
                    #A changer si on veut maximiser
                    b[(i*nbC+j)*4+k] = valBut(nbL, nbC)
                    A[(i*nbC+j)*4+k][nbL*nbC] = -gamma
                else: #Autres cases
                    trans = transition(grille, k, i, j, proba)
                    for t in trans:
                        A[(i*nbC+j)*4+k][t[0]*nbC+t[1]]=-gamma*trans[t]

    #État puits
    for i in range(4):
        A[nbL*nbC*4+i][nbL*nbC] = 1-gamma

    #fonction objectif
    obj = np.zeros(nbL*nbC+1)
    obj[0] = 1

    return (A, b, obj)


def programmedual(grille, gamma, proba):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    #Matrice des contraintes + second membre
    A = np.zeros(((nbL*nbC+1)*(4+1), (nbL*nbC+1)*4))
    b = np.zeros((nbL*nbC+1)*(4+1))
    b[0] = 1
    #fonction objectif
    obj = np.zeros((nbL*nbC+1)*4)
    for i in range(nbL):
        for j in range(nbC):
            for k in range(4):
                A[i*nbC+j][(i*nbC+j)*4+k] = 1
                A[nbC*nbL+1+(i*nbC+j)*4+k][(i*nbC+j)*4+k] = 1
                if i != (nbL-1) or j != (nbC-1):
                    obj[(i*nbC+j)*4+k] = grille[i][j]
                    trans = transition(grille, k, i, j, proba)
                    for t in trans:
                        A[t[0]*nbC+t[1]][(i*nbC+j)*4+k] = -gamma*trans[t]
                else:
                    obj[(i*nbC+j)*4+k] = valBut(nbL, nbC)

    #État puits
    for i in range(4):
        A[nbC*nbL][nbC*nbL*4+i] = 1-gamma
        A[nbL*nbC][(nbL*nbC-1)*4+i]=-gamma
        A[nbC*nbL*5+i][nbC*nbL*4+i] = 1

    return (A, b, obj)


def resolutionGurobiprimal(a,b,objectif,nbL,nbC):
    #global nblignes , nbcolonnnes
    m = Model("PDM")     
    
    # declaration variables de decision
    v = []
    for i in range(nbL*nbC+1):
        v.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="v%d" % (i+1)))
    
    # maj du modele pour integrer les nouvelles variables
    m.update()

    obj = LinExpr(objectif, v)

    # definition de l'objectif
    m.setObjective(obj,GRB.MINIMIZE)

    # definition des contraintes
    for i in range((nbL*nbC+1)*4):
        m.addConstr(LinExpr(a[i], v) >= b[i], "Contrainte%d" % i)
        
    # Resolution
    m.optimize()
    #temps de résolution (-0.01 pour compenser le temps d'exécution de la ligne suivante)
    t = m.getAttr(GRB.Attr.Runtime) - 0.01
    
    return v, m, t

def resolutionGurobidual(A, b, objectif, nbL, nbC):
    m = Model("PDM")

    #déclaration variables de décision
    v = []
    for i in range((nbC*nbL+1)*4):
        v.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x%d" % (i+1)))
    m.update()

    #définition de l'objectif
    obj = LinExpr(objectif, v)
    m.setObjective(obj, GRB.MAXIMIZE)

    #définition des contraintes
    for i in range(nbC*nbL+1):
        m.addConstr(LinExpr(a[i], v) == b[i], "contrainte %d" % i)
    for i in range(nbC*nbL+1, (nbC*nbL+1)*5):
        m.addConstr(LinExpr(a[i], v] >= 0, "contrainte %d" % i)

    #résolution
    m.optimize()
    t = m.getAttr(GRB.Attr.Runtime) - 0.01

    return v, m, t

'''
#Sans puits = moins bons résultats qu'avec.
def programmeprimal(grille, gamma, proba):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    #Matrice des contraintes + second membre
    A = np.zeros((nbL*nbC*4, nbL*nbC))
    b = np.zeros(nbL*nbC*4)
    for i in range(nbL):
        for j in range(nbC):
            for k in range (4):
                b[(i*nbC+j)*4+k]=-grille[i][j]
                #Valeur de la case d'arrivée
                if (i == (nbL - 1) and j == (nbC -1)):
                    #A changer si on veut maximiser
                    b[(i*nbC+j)*4+k]= valBut(nbL, nbC)
                A[(i*nbC+j)*4+k][i*nbC+j]=1
                trans = transition(grille, k, i, j, proba)
                for t in trans:
                    A[(i*nbC+j)*4+k][t[0]*nbC+t[1]]=-gamma*trans[t]

    #fonction objectif
    obj = np.zeros(nbL*nbC)
    obj[0] = 1
    #test
    #obj = np.ones(nbL*nbC)

    return (A, b, obj)

#Sans puits
def resolutionGurobiprimal(a,b,objectif,nbL,nbC):
    global nblignes , nbcolonnnes
    m = Model("PDM")     
    
    # declaration variables de decision
    v = []
    for i in range(nbL*nbC):
        v.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="v%d" % (i+1)))
    
    # maj du modele pour integrer les nouvelles variables
    m.update()

    obj = LinExpr(objectif, v)

    # definition de l'objectif
    m.setObjective(obj,GRB.MINIMIZE)

    # definition des contraintes
    for i in range(nbL*nbC*4):
        m.addConstr(LinExpr(a[i], v) >= b[i], "Contrainte%d" % i)
        
    # Resolution
    m.optimize()
    #temps de résolution (-0.01 pour compenser le temps d'exécution de la ligne suivante)
    t = m.getAttr(GRB.Attr.Runtime) - 0.01
    
    return v, m, t'''

#À partir du résultat du PL, calcule une politique
#/!\ donne des puits des fois, quand plusieurs cases adjacentes ont la même valeur
def politique(valeurs, grille, proba, gamma):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    pol = np.zeros((nbL,nbC))
    for i in range(nbL):
        for j in range(nbC):
            maximum = 0
            for k in range(4):
                temp = grille[i][j]
                trans = transition(grille, k, i, j, proba)
                for t in trans:
                    temp += gamma * trans[t] * valeurs[t[0]*nbC+t[1]].x
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
""" Exemple de grille avec puits
g=np.ones((nblignes, nbcolonnes), dtype=int)
g[0,1]=2
g[0,2]=2
g[0,3]=0
g[0,4]=2
g[1,1]=3
g[1,2]=4
g[1,3]=4
g[2,0]=3
g[2,3]=2
g[3,0]=2
g[3,1]=2
g[3,2]=3
g[3,4]=2
g[4,1]=4
g[4,3]=3"""
print g
(A, b, obj) = programmeprimal(g, gamma,probaTransition)
v, m, t = resolutionGurobiprimal(A, b, obj,nblignes,nbcolonnes)
pol = politique(v, g,probaTransition,gamma)
print "pol sans puits :"
print pol

(A, b, obj) = programmeprimalpuits(g, gamma,probaTransition)
v, m, t = resolutionGurobiprimalpuits(A, b, obj,nblignes,nbcolonnes)
pol = politique(v, g,probaTransition,gamma)
print "pol avec puits :"
print pol

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

"""
#Test fonction de test
moyD, moyR = comparePerformanceProba(nblignes, nbcolonnes, gamma, 0.1, 10)
print moyD
print moyR
"""

"""
nblignes = 8
nbcolonnes =5

g = defineMaze(nblignes, nbcolonnes)
(A, b, obj) = programmeprimal(g, gamma,probaTransition)
v, m,t = resolutionGurobiprimal(A, b, obj,nblignes,nbcolonnes)
print "v"
print v

pol = politique(v, g,probaTransition,gamma)
print "pol :"
print pol

"""

