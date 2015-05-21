# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 2015

@author: Yann Ropaul & Margot Calbrix
"""

from gurobipy import *
import random
import numpy as np
import time
import modele_1critere
import matplotlib.pyplot as pl

################################################################################
#
#                        VARIABLES ET CONSTANTES GLOBALES
#
################################################################################


#probabilité d'un mur
pmur = 0.15

#taille de la grille
nblignes=20
nbcolonnes=20

#nombre de critères
nbcriteres=4

#Probabilité d'aller effectivement dans la direction voulue
probaTransition=0.9

#Visibilité du futur
gamma = 0.9

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

#fonction d'optimisation
MINMAX = 0
REGRET = 1
RPOND = 2

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
    while not not aexplorer: #tant que aexplorer n'est pas vide
        case = aexplorer.pop(0)
        for d in range(4):
            trans = transition(grille, d, case[0], case[1], 1, grille.shape[2])
            for t in trans:
                if t == (grille.shape[0]-1, grille.shape[1]-1):
                    return True
                if not (t in explores):
                    aexplorer.append(t)
                    explores.add(t)
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

def valBut(nblignes, nbcolonnes):
    return nblignes*nbcolonnes*100
    

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
        obj[(nbL*nbC-1)*4+k] = -valBut(nbL,nbC)

    return (A, b, obj)
                
                
def gurobiMultiSomme(a, b, objectif, nblignes, nbcolonnes):
    m = Model("MOPDM")
    #déclaration des variables de décision
    v = []
    for i in range(len(objectif)):
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
        m.addConstr(LinExpr(a[i], v) <= b[i], "Contrainte%d" % i)
    for i in range(nblignes*nbcolonnes,a.shape[0]):
        m.addConstr(LinExpr(a[i], v) >= b[i], "Contrainte%d" % i)
    
    #résolution
    
    m.optimize()
    #temps de résolution (-0.01 pour compenser le temps d'exécution de la ligne suivante)
    t = m.getAttr(GRB.Attr.Runtime) - 0.01

    return v, m, t




def resolutionMultiSomme(grille, gamma, proba, nbCriteres, nblignes, nbcolonnes):
    (A, b, obj) = dualSomme(grille, gamma, proba, nbCriteres)
    v, m, t = gurobiMultiSomme(A, b, obj, nblignes, nbcolonnes)
    pol = politique(v, grille)
    return pol,v



################################################################################
#
#            FONCTIONS DE RESOLUTION (OBJECTIF = CRITERE EQUITABLE)
#
################################################################################

# Définition du PL dual de l'approche égalitariste
# contraintes (1) : sum(Xsa pourtout a) - gamma*sum(sum(T(s',a,s)*Xsa pourtout a) pourtout s') = µ(s) pourtout s
# contraintes (2) : Xsa >= 0 pourtout s, pourtout a
# contraintes (3) : z - sum(sum(Ri(s,a)*Xsa pourtout a) pourtout s) <= 0 pourtout i
def dualMinMax(grille, gamma, proba, nbCriteres):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    #Matrice des contraintes + second membre
    A = np.zeros(((nbL*nbC+1)*(4+1)+nbCriteres, nbL*nbC*4+1+4))
    b = np.zeros((nbL*nbC+1)*(4+1)+nbCriteres)
    b[0]=1 #µ((0,0)) = 1
    for i in range(nbL):
        for j in range(nbC):
            #b[i*nbC+j]=1./(nbL*nbC)
            for k in range(4):
                A[i*nbC+j][(i*nbC+j)*4+k] = 1 #contraintes (1) : sum(Xsa pourtout a)
                A[nbL*nbC+1+((i*nbC+j)*4+k)][(i*nbC+j)*4+k]=1 #contraintes (2)
                if i != nbL-1 or j != nbC-1:
                    #rajoute les -gamma sur les autres lignes
                    trans=transition(grille, k, i, j, proba, nbCriteres)
                    for t in trans:
                        A[t[0]*nbC+t[1]][(i*nbC+j)*4+k]=-gamma*trans[t] #contraintes (1) : - gamma*sum(sum(T(s',a,s)*Xsa pourtout a) pourtout s')
                for n in range(nbCriteres):
                    if i == nbL-1 and j == nbC-1:
                        A[(nbL*nbC+1)*5+n][(i*nbC+j)*4+k]=-valBut(nbL,nbC) #contraintes (3) : sum(sum(Ri(s,a)*Xsa pourtout a) pourtout s) pour l'état but
                    else:
                        trans=transition(grille, k, i, j, proba, nbCriteres)
                        if not trans: # si trans est vide
                            A[(nbL*nbC+1)*5+n][(i*nbC+j)*4+k]=0
                        else:
                            A[(nbL*nbC+1)*5+n][(i*nbC+j)*4+k]=grille[i][j][n] #contraintes (3) : sum(sum(Ri(s,a)*Xsa pourtout a) pourtout s)
    #contraintes sur l'état puits
    for i in range(4):
        A[nbL*nbC][nbL*nbC*4+i]=1-gamma #contraintes (1)
        A[nbL*nbC][(nbL*nbC-1)*4+i]=-gamma #contraintes (1)
        A[nbL*nbC+1+nbL*nbC*4+i][nbL*nbC*4+i]=1 #contraintes (2)
    for n in range(nbCriteres):
        A[(nbL*nbC+1)*5+n][(nbL*nbC+1)*4]=1 #contraintes (3)

    #fonction objectif
    # max z (dernière variable)
    obj = np.zeros(nbL*nbC*4+1+4)
    obj[nbL*nbC*4+4]=1
    
    return (A, b, obj)

""" Vielle version (sans état puits à la fin)
def dualMinMax(grille, gamma, proba, nbCriteres):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    #Matrice des contraintes + second membre
    A = np.zeros((nbL*nbC*(4+1)+nbCriteres, nbL*nbC*4+1))
    b = np.zeros(nbL*nbC*(4+1)+nbCriteres)
    b[0]=1
    for i in range(nbL):
        for j in range(nbC):
            #b[i*nbC+j]=1
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
                        A[nbL*nbC*5+n][(i*nbC+j)*4+k]=-1000
                    else:
                        if not trans: # si trans est vide
                            A[nbL*nbC*5+n][(i*nbC+j)*4+k]=0
                        else:
                            A[nbL*nbC*5+n][(i*nbC+j)*4+k]=-grille[i][j][n]
    for n in range(nbCriteres):
        A[nbL*nbC*5+n][nbL*nbC*4]=1
        b[nbL*nbC*5+n]=0
    #fonction objectif
    obj = np.zeros(nbL*nbC*4+1)
    obj[nbL*nbC*4]=1
    return (A, b, obj)"""
                
                
def gurobiMultiMinMax(a, b, objectif, nblignes, nbcolonnes):
    m = Model("MOPDMeq")
    #déclaration des variables de décision
    v = []
    for i in range(len(objectif)-1):
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
    """
    #définition des contraintes SANS ETAT PUITS
    for i in range(nblignes*nbcolonnes):
        #A VERIFIER : LEQUEL MARCHE MIEUX
        m.addConstr(LinExpr(a[i], v) == b[i], "Contrainte%d" % i)
        #m.addConstr(LinExpr(a[i],v) <= b[i], "Contrainte%d" % i)
    for i in range(nblignes*nbcolonnes,nblignes*nbcolonnes*5):
        m.addConstr(LinExpr(a[i], v) >= b[i], "Contrainte%d" % i)
    for i in range(nblignes*nbcolonnes*5, a.shape[0]):
        m.addConstr(LinExpr(a[i], v) <= b[i], "Contrainte%d" % i)"""
    #définition des contraintes
    for i in range(nblignes*nbcolonnes+1):
        #A VERIFIER : LEQUEL MARCHE MIEUX
        m.addConstr(LinExpr(a[i], v) == b[i], "Contrainte%d" % i)
        #m.addConstr(LinExpr(a[i],v) <= b[i], "Contrainte%d" % i)
    for i in range(nblignes*nbcolonnes+1,(nblignes*nbcolonnes+1)*5):
        m.addConstr(LinExpr(a[i], v) >= b[i], "Contrainte%d" % i)
    for i in range((nblignes*nbcolonnes+1)*5, a.shape[0]):
        m.addConstr(LinExpr(a[i], v) <= b[i], "Contrainte%d" % i)
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
#            FONCTIONS DE RESOLUTION (OBJECTIF = REGRET MINMAX)
#
################################################################################


def toMonocritere(grille, ncrit):
    res = np.zeros((grille.shape[0], grille.shape[1]), dtype=int)
    for i in range(grille.shape[0]):
        for j in range(grille.shape[1]):
            res[i][j] = grille[i][j][ncrit]
    return res

def Vstar(grille, gamma, proba, nbCriteres):
    nbL = grille.shape[0]
    nbC = grille.shape[1]
    res = np.zeros(nbCriteres)
    g = toMonocritere(grille, i)
    (a, b, obj) = modele_1critere.programmedual(g, gamma, proba)
    m = Model("PDM")     
    # declaration variables de decision
    v = []
    for i in range((nbL*nbC+1)*4):
        v.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x%d" % (i+1)))
    # maj du modele pour integrer les nouvelles variables
    m.update()
    # definition des contraintes
    for i in range(nbC*nbL+1):
        m.addConstr(LinExpr(a[i], v) == b[i], "contrainte %d" % i)
    for i in range(nbC*nbL+1, (nbC*nbL+1)*5):
        m.addConstr(LinExpr(a[i], v) >= 0, "contrainte %d" % i)
        
    for c in range(nbCriteres):
        objectif = LinExpr(obj, v)
        # definition de l'objectif
        m.setObjective(obj,GRB.MINIMIZE)
        m.update()
        # Resolution
        m.optimize()
        res[c] = m.getAttr(GRB.Attr.ObjVal)

        if c < nbCriteres-1:
            g = toMonocritere(grille, c+1)
            obj = np.zeros(len(obj), dtype=int)
            for i in range(nbL):
                for j in range(nbC):
                    for k in range(4):
                        if i != (nbL-1) or j != (nbC-1):
                            obj[(i*nbC+j)*4+k] = g[i][j]
                        else:
                            obj[(i*nbC+j)*4+k] = -valBut(g.shape[0], g.shape[1])
    return res

# Définition du PL dual de l'approche regret minmax
# contraintes (1) : sum(Xsa pourtout a) - gamma*sum(sum(T(s',a,s)*Xsa pourtout a) pourtout s') = µ(s) pourtout s
# contraintes (2) : Xsa >= 0 pourtout s, pourtout a
# contraintes (3) : z + sum(sum(Ri(s,a)*Xsa pourtout a) pourtout s) <= V*i pourtout i
def dualRegretMinMax(grille, gamma, proba, nbCriteres):
    vstar = Vstar(grille, gamma, proba, nbCriteres)
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    #Matrice des contraintes + second membre
    A = np.zeros(((nbL*nbC+1)*(4+1)+nbCriteres, nbL*nbC*4+1+4))
    b = np.zeros((nbL*nbC+1)*(4+1)+nbCriteres)
    b[0]=1 #µ((0,0)) = 1
    for i in range(nbL):
        for j in range(nbC):
            #b[i*nbC+j]=1./(nbL*nbC)
            for k in range(4):
                A[i*nbC+j][(i*nbC+j)*4+k] = 1 #contraintes (1) : sum(Xsa pourtout a)
                A[nbL*nbC+1+((i*nbC+j)*4+k)][(i*nbC+j)*4+k]=1 #contraintes (2)
                if i != nbL-1 or j != nbC-1:
                    #rajoute les -gamma sur les autres lignes
                    trans=transition(grille, k, i, j, proba, nbCriteres)
                    for t in trans:
                        A[t[0]*nbC+t[1]][(i*nbC+j)*4+k]=-gamma*trans[t] #contraintes (1) : - gamma*sum(sum(T(s',a,s)*Xsa pourtout a) pourtout s')
                for n in range(nbCriteres):
                    if i == nbL-1 and j == nbC-1:
                        A[(nbL*nbC+1)*5+n][(i*nbC+j)*4+k]=valBut(nbL,nbC) #contraintes (3) : sum(sum(Ri(s,a)*Xsa pourtout a) pourtout s) pour l'état but
                    else:
                        trans=transition(grille, k, i, j, proba, nbCriteres)
                        if not trans: # si trans est vide
                            A[(nbL*nbC+1)*5+n][(i*nbC+j)*4+k]=0
                        else:
                            A[(nbL*nbC+1)*5+n][(i*nbC+j)*4+k]=-grille[i][j][n] #contraintes (3) : sum(sum(Ri(s,a)*Xsa pourtout a) pourtout s)
    #contraintes sur l'état puits
    for i in range(4):
        A[nbL*nbC][nbL*nbC*4+i]=1-gamma #contraintes (1)
        A[nbL*nbC][(nbL*nbC-1)*4+i]=-gamma #contraintes (1)
        A[nbL*nbC+1+nbL*nbC*4+i][nbL*nbC*4+i]=1 #contraintes (2)
    for n in range(nbCriteres):
        A[(nbL*nbC+1)*5+n][(nbL*nbC+1)*4]=1 #contraintes (3)
        b[(nbL*nbC+1)*5+n] = vstar[n]

    #fonction objectif
    # max z (dernière variable)
    obj = np.zeros(nbL*nbC*4+1+4)
    obj[nbL*nbC*4+4]=1
    
    return (A, b, obj)


################################################################################
#
#                            POINT NADIR
#
################################################################################

#donne pour une position (i,j) la va laeur de (i',j') pour une direction donné 
def indiceSuivant(i,j,direction):
    if (direction == 0):
        return i+1 , j
    if (direction == 1):
        return i-1 , j
    if (direction == 2):
        return i , j+1
    if (direction == 3):
        return i , j-1
        
#prend la matrice V et la met sous forme de tableau plus lisible    
def grilleV(v, nbl,nbc):
    grille=np.zeros((nbl,nbc))
    for i in range(nbl):
        for j in range (nbc):
            grille[i][j]= v[i*nbc+j].x
    return grille
    
   

def rechercheVS(politique,grille, gamma, proba):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    #Matrice des contraintes + second membre
    A = np.zeros(((nbL*nbC+1)*4, nbL*nbC+1))
    b = np.zeros((nbL*nbC+1)*4)
    for i in range(nbL):
        for j in range(nbC):
            for k in range(4):
                if (k == politique[i][j] ):
                    b[(i*nbC+j)*4+k] = -grille[i][j]
                else :
                    b[(i*nbC+j)*4+k] = 0
                A[(i*nbC+j)*4+k][i*nbC+j] = 1
                #Case d'arrivée
                
                if (i == (nbL-1) and j == (nbC-1)):
                    #A changer si on veut maximiser
                    b[(i*nbC+j)*4+k] = valBut(nbL, nbC)
                    A[(i*nbC+j)*4+k][nbL*nbC] = -gamma
                else: #Autres cases
                    trans = modele_1critere.transition(grille, k, i, j, proba)
                    for t in trans:
                        A[(i*nbC+j)*4+k][t[0]*nbC+t[1]]=-gamma*trans[t]
    #État puits
    for i in range(4):
        A[nbL*nbC*4+i][nbL*nbC] = 1-gamma
    #fonction objectif
    obj = np.zeros(nbL*nbC+1)
    obj[0] = 1
    return (A, b, obj)
    
    

def resolutionGurobirechercheVs(a,b,objectif,nbL,nbC):
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

#donne les différente valeur de pt nadir pour chaque case pour chaque critère
def ptNadir(grille,gamma,proba,nbCritere):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    Vs =np.zeros((nbL,nbC,nbCritere))
    temp =np.zeros((nbL,nbC))
    #on fai le calcul pour chaque critère
    for k in range (nbCritere):
        #on isole un citère pour calculer la politique max de ce critère
        for i in range (nbL):
            for j in range (nbC):
                temp[i][j]=grille[i,j,k]
        (A, b, obj) = modele_1critere.programmeprimal(temp, gamma,probaTransition)
        v, m, t = modele_1critere.resolutionGurobiprimal(A, b, obj,nbL,nbC)
        pol = modele_1critere.politique(v, temp,probaTransition,gamma)
        #pour chaque critère on calcul sa valeur pour la politque précédente et on garde la valeur la plus grande
        for l in range (nbCritere):
            for i in range (nbL):
                for j in range (nbC):
                    temp[i][j]=grille[i,j,l]
            (A,b,obj)=rechercheVS(pol,temp,gamma,probaTransition)
            v,m,t = resolutionGurobirechercheVs(A,b,obj,nbL,nbC)
            vstemp = grilleV(v,nbL,nbC)
            print "**************************"
            print "vstemp"
            print vstemp
            print "**************************"
            for i in range (nbL):
                for j in range (nbC):
                    if Vs[i,j,l] <= vstemp[i][j] :
                        Vs[i,j,l] = vstemp[i][j]
    return Vs


        
################################################################################
#
#                                   TESTS
#
################################################################################


def executionPol(grille, pol, proba):
    nbL, nbC, nbCrit = grille.shape
    pos = (0, 0)
    couts = np.zeros(nbCrit, dtype=int)
    while pos != (nbL-1, nbC-1):
        z=np.random.uniform(0,1)
        dir = 0
        p = pol[pos[0]][pos[1]]
        if z < p[0]:
            dir = HAUT
        else:
            if z < p[0]+p[1]:
                dir = BAS
            else:
                if z < p[0]+p[1]+p[2]:
                    dir = GAUCHE
                else:
                    dir = DROITE
        trans = transition(grille, dir, pos[0], pos[1], proba, nbCrit)
        z=np.random.uniform(0,1)
        tmp=0
        for t in trans:
            tmp+=trans[t]
            if z < tmp:
                if pos != (0,0):
                    for i in range(nbCrit):
                        couts[i]+=grille[pos[0]][pos[1]][i]
                pos = t
                break
    return couts

def testPol(grille, pol, proba, nbIter):
    execs= np.zeros((grille.shape[2], nbIter), dtype=int)
    for i in range(nbIter):
        couts = executionPol(grille, pol, proba)
        for j in range(len(couts)):
            execs[j][i]=couts[j]
    return execs

def plotPols(execsSomme, execsSocial, fonc):
    pl.figure()
    pl.plot(execsSomme[0], execsSomme[1], '.', label="Somme ponderee")
    lab=''
    if fonc == MINMAX:
        lab='Fonction egalitaire'
    if fonc == REGRET:
        lab='Regret minmax'
    if fonc == RPOND:
        lab='Regret pondere'
    pl.plot(execsSocial[0], execsSocial[1], 'wo', label=lab)
    pl.legend(loc=0)
    pl.show()
            
################################################################################
#
#                            PROGRAMME PRINCIPAL
#
################################################################################

g=defineMaze(nblignes,nbcolonnes,nbcriteres)
#print g
'''
g = np.zeros((3,3,2))
g[0,0,0]=1
g[0,0,1]=1
g[0,1,0]=1
g[0,2,0]=1
g[1,0,0]=1
g[1,1,0]=1
g[1,1,1]=1
g[2,0,0]=1
g[2,2,0]=1
g[2,2,1]=1
g[0,1,0]=0
g[0,1,1]=40
g[0,2,0]=0
g[0,2,1]=40
g[1,0,1]=0
g[1,0,0]=40
g[1,2,1]=40
g[1,2,0]=0
g[2,0,1]=0
g[2,0,0]=40
g[2,1,1]=0
g[2,1,0]=40'''
#g = np.ones((2,2,2))
#g[0,1,0]=0
#g[1,0,1]=0
print g
'''
#Test plotPols
pol1, v1 = resolutionMultiSomme(g, gamma, probaTransition, nbcriteres, nblignes, nbcolonnes)
print pol1
pol2 = resolutionMultiMinMax(g, gamma, probaTransition, nbcriteres, nblignes, nbcolonnes)
print pol2
ex1=testPol(g, pol1, probaTransition, 200)
ex2=testPol(g, pol2, probaTransition, 200)
plotPols(ex1, ex2, MINMAX)'''

"""
#Test PL
g = np.ones((2,2,2))
g[0,1,0]=0
g[1,0,1]=0
print g
A, b, obj = dualMinMax(g, gamma, probaTransition, 2)
print A
print b
print obj
v, m, t = gurobiMultiMinMax(A, b, obj, 2, 2)
print v
pol = politique(v, g)
#pol = resolutionMultiMinMax(g, gamma, probaTransition, 2,2,2)
print pol"""


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
