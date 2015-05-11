# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 09:54:03 2015

@author: teddy
"""
#
from modele_multicritere import *
from Tkinter import *
from gurobipy import *
import random
import numpy as np
import math


#donne la valeur Rsa pour une transition direction a la case (i,j)
def valTrans(g,i,j,direction,critere):
    nbl=g.shape[0]
    nbc=g.shape[1]
    #si en haut
    if (direction == 0 ):
        if(i <=0 ):
            return 0
        else :
            if (i-1 == nbl-1 and j==nbc -1):
                return valBut(nbl,nbc)
            else :
                return g[i-1,j,critere]
    #si en bas
    if (direction == 1 ):
        if(i >= nbl-1 ):
            return 0
        else :
            if (i +1== nbl -1 and j==nbc -1):
                return valBut(nbl,nbc)
            else :
                return g[i+1,j,critere]
    #si a gauche
    if (direction == 2 ):
        if(j <=0 ):
            return 0
        else :
            if (i == nbl -1 and j-1==nbc -1):
                return valBut(nbl,nbc)
            else :
                return g[i,j-1,critere]
    #si en haut
    if (direction == 3 ):
        if(j >= nbc -1 ):
            return 0
        else :
            if (i == nbl -1 and j+1==nbc -1):
                return valBut(nbl,nbc)
            else :
                return g[i,j+1,critere]
    
    
def valBut(nblignes, nbcolonnes):
    return nblignes*nbcolonnes*50

def dualMinMax2(grille, gamma, proba, nbcritere):
    nbl=grille.shape[0]
    nbc=grille.shape[1]
    a= np.zeros((nbcritere+ ((nbl*nbc)+1)*(4+1),(nbl*nbc)*4+1))
    b= np.zeros(nbcritere+ ((nbl*nbc)+1)*(4+1))
    obj= np.zeros((nbl*nbc)*4+1)
    #on maximize z (le dernier critere)
    obj[(nbl*nbc)*4+1-1]=1
    # z >sum(sum(R(s,a)Xsa))
    for l in range(nbcritere) :
        #on met le coef de z a 1
        a[l][(nbl*nbc)*4]=1
        for i in range(nbl):
            for j in range(nbc):
                for k in range (4):
                    #les premieres lignes des contrainte , une contrainte par critere (d'ou le l)
                    a[l][(i*nbc+j)*4+k]=-1* valTrans(grille,i,j,k,l) #-1* grille[i,j,l]
                    #second memebre a zero
                    b[l]= 0
    #la contrainte principale
    
    for i in range(nbl):
        for j in range(nbc):
            #intintialisation du second membre
            b[nbcritere+nbc*i+j]=0
            for k in range(4):
                #rajoute la sum(Xsa)
                a[nbcritere+nbc*i+j][(i*nbc+j)*4+k]=1
                if (i == nbl-1 and j==nbc -1):
                     a[nbcritere+nbc*i+j][(i*nbc+j)*4+k]=01
                #rajoute les -gamma sur les autres lignes
                trans=transition(grille, k, i, j, proba, nbcriteres)
                for t in trans:
                    iprime = t[0]
                    jprime= t[1]
                    ''' if (iprime == nbl-1 and jprime==nbc -1):
                        a[nbcritere+nbc*iprime+jprime][(i*nbc+j)*4+k]=  0 
                    else:'''
                    a[nbcritere+nbc*iprime+jprime][(i*nbc+j)*4+k]= -1* gamma * trans[t] 
    #seul la premiere case a un u(s) a 1                 
    b[nbcritere]=1
    #Xsa > 0            
    for i in range (nbl*nbc*4):
        a[nbcritere+(nbl*nbc)+i][i]=1
        b[nbcritere+(nbl*nbc)+i]=0
        
    #gestion de l'état puits
    for i in range (4):
        a[(nbcritere+ ((nbl*nbc)+1)*(4+1)-5+i][(nbc*nbl)*4+i]= 1
        a[(nbcritere+ ((nbl*nbc)+1)*(4+1)-5+i][nbc*(nbl-1)+i]= -gamma
        
    return (a, b, obj)
                
                
                
def gurobiMultiMinMax2(a, b, objectif, nblignes, nbcolonnes):
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
    for i in range(len(objectif)):
        obj += objectif[i]*v[i]
    m.setObjective(obj,GRB.MAXIMIZE)

    #définition des contraintes
    #TEST : plus de problème de temps
    t = time.time()
#    for i in range(a.shape[0]):
#        #A VERIFIER : LEQUEL MARCHE MIEUX
#        m.addConstr(LinExpr(a[i], v) <= b[i], "Contrainte%d" % i)
    for i in range(nbcriteres):
        #A VERIFIER : LEQUEL MARCHE MIEUX
        m.addConstr(LinExpr(a[i], v) <= b[i], "Contrainte%d" % i)
        #m.addConstr(LinExpr(a[i],v) <= b[i], "Contrainte%d" % i)
    for i in range(nbcriteres,nblignes*nbcolonnes+nbcriteres):
        m.addConstr(LinExpr(a[i], v) == b[i], "Contrainte%d" % i)
    for i in range(nblignes*nbcolonnes+nbcriteres, a.shape[0]):
        m.addConstr(LinExpr(a[i], v) >= b[i], "Contrainte%d" % i)
    #résolution
    m.optimize()
    
    #temps de résolution (-0.01 pour compenser le temps d'exécution de la ligne suivante)
    t = m.getAttr(GRB.Attr.Runtime) - 0.01
    
    return v, m, t




def resolutionMultiMinMax2(grille, gamma, proba, nbCriteres, nblignes, nbcolonnes):
    (A, b, obj) = dualMinMax2(grille, gamma, proba, nbCriteres)
    v, m, t = gurobiMultiMinMax2(A, b, obj, nblignes, nbcolonnes)
    print "v"
    print v
    pol = politique2(v, grille)
    return pol
        

def politique2(valeurs, grille):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    print grille.shape
    print len(valeurs)
    pol = np.zeros((nbL,nbC,4))
    for i in range(nbL):
        for j in range(nbC):
            for k in range(4):
                pol[i][j][k] = valeurs[(i*nbC+j)*4+k].x * 1.0
            somme = sum(pol[i][j])
            if somme != 0 :
                for k in range(4):
                    pol[i][j][k] /= somme
    return pol        
   
     
g = np.zeros((3,3,2))
g[0,0,0]=1
g[0,1,0]=1
g[0,2,0]=1
g[1,0,0]=1
g[1,1,0]=1
g[2,0,0]=1
g[2,2,0]=1
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
g[2,1,0]=40
print g
##print estFinissable(g)
#pol = resolutionMultiMinMax(g, gamma, probaTransition, nbcriteres, nblignes, nbcolonnes)
gamma= 0.9
probaTransition=0.5
pol = resolutionMultiMinMax2(g, gamma, probaTransition, 2,3,3)
print "c'est bien mon truc"
print pol
#(A, b, obj) = dualMinMax2(g, gamma, probaTransition, 2)
#for i in range (A.shape[0]):
#    print A[i]
        
#print "b"  
#print b     
     