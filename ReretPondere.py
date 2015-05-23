# -*- coding: utf-8 -*-
"""
Created on Sat May 23 11:34:32 2015

@author: Yann Ropaul et Margot Calbrix
"""


from modele_1critere import *
from modele_multicritere import *
import minmax_multicritere 
from Tkinter import *
from gurobipy import *
import random
import numpy as np
import math

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


#donne un vecteur lambda de la taille des critere qui donne la valeur alpha/(Vs*-nj) 
#vsetoile est un vecteur de la taille des criteres qui donne la valeurs vs*
def calulLambda(alpha,vsetoile,grille,gamma,proba,nbCritere):
    nbl= grille.shape[0]
    nbc= grille.shape[1]
    Vs = ptNadir(grille,gamma,proba,nbCritere)
    valNadir = np.zeros(nbCritere)
    for k in range (nbCritere):
        for i in range (nbl):
            for j in range (nbc):
                valNadir[k]+= Vs[i,j,k]
    lamb= np.zeros(nbCritere)
    for l in range (nbCritere):
        print "alpha"
        print alpha[l]
        print "valNadir"
        print valNadir[l]
        print "vsetoile"
        print vsetoile[l]
        lamb[l] = alpha[l]/1.00*(valNadir[l]- vsetoile [l])
    return lamb
    
    
def calculVsEtoile(grille,gamma,proba,nbCritere):
    nbl= grille.shape[0]
    nbc= grille.shape[1]
    temp = np.zeros((nbl,nbc))
    vsetoile= np.zeros(nbCritere)
    for l in range (nbCritere):
        for i in range (nbl):
            for j in range (nbc):
                temp[i][j]=grille[i,j,l]
        (A,b,obj)=programmeprimal(temp,gamma,probaTransition)
        v,m,t = resolutionGurobiprimal(A,b,obj,nbl,nbc)
        vstemp = grilleV(v,nbl,nbc)
        for i in range (nbl):
            for j in range (nbc):
                vsetoile[l] += vstemp[i][j]
    return vsetoile
    
    
################################################################################
#
#                            REGRET PONDERE
#
################################################################################


       
        

def dualRegretPondere(grille, gamma, proba, nbcritere,alpha):
    nbl=grille.shape[0]
    nbc=grille.shape[1]
    vsetoile = calculVsEtoile(grille,gamma,proba,nbcritere)
    lamb=calulLambda(alpha,vsetoile,grille,gamma,proba,nbcritere)
    a= np.zeros((nbcritere+ ((nbl*nbc)+1)*(4+1),(nbl*nbc)*4+1+4))
    b= np.zeros(nbcritere+ ((nbl*nbc)+1)*(4+1))
    obj= np.zeros((nbl*nbc)*4+1+4)
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
                    a[l][(i*nbc+j)*4+k]= lamb[l]*1* minmax_multicritere.valTrans(grille,i,j,k,l) #-1* grille[i,j,l]
                    #second memebre a zero
                    b[l]= lamb[l]*vsetoile[l]
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
#                if (i != nbl-1 and j!=nbc -1):
                for t in trans:
                    iprime = t[0]
                    jprime= t[1]
                    ''' if (iprime == nbl-1 and jprime==nbc -1):
                        a[nbcritere+nbc*iprime+jprime][(i*nbc+j)*4+k]=  0 
                    else:'''
                    a[nbcritere+nbc*iprime+jprime][(i*nbc+j)*4+k]= -1* gamma * trans[t] 
    #seul la premiere case a un u(s) a 1                 
    b[nbcritere]=1
    
    for i in range (nbl*nbc-1):
        for k in range (4):
            a[nbcritere+ i][(nbc*nbl-1)*4+k]= 0
    
    #Xsa > 0            
    for i in range ((nbl*nbc)*4):
        a[nbcritere+(nbl*nbc)+i][i]=1
        b[nbcritere+(nbl*nbc)+i]=0
    #Xsa de l'état puits
    for i in range (4):
        a[nbcritere+(nbl*nbc)*(4+1)+i][nbl*nbc*(4)+1+i]=1
        b[nbcritere+(nbl*nbc)*(4+1)+i]=0
    #gestion de l'état puits
    for i in range (4):
        a[nbcritere+ ((nbl*nbc)+1)*(4+1)-1][(nbc*nbl)*4+1+i]= 1-gamma
        a[nbcritere+ ((nbl*nbc)+1)*(4+1)-1][(nbc*nbl-1)*4+i]= -gamma
        
    return (a, b, obj)        
        


def gurobiMultiRegretPondere(a, b, objectif, nblignes, nbcolonnes):
    m = Model("MOPDMeq")
    #déclaration des variables de décision
    v = []
    for i in range(len(objectif)-1-4):
        v.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x%d" % (i+1)))
    v.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="z"))
    for i in range(len(objectif)-4,len(objectif)):
        v.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="p%d" % (i+1)))
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
    for i in range(nblignes*nbcolonnes+nbcriteres, a.shape[0]-1):
        m.addConstr(LinExpr(a[i], v) >= b[i], "Contrainte%d" % i)
    for i in range(a.shape[0]-1, a.shape[0]):
        m.addConstr(LinExpr(a[i], v) == b[i], "Contrainte%d" % i)
    #résolution
    m.optimize()
    #temps de résolution (-0.01 pour compenser le temps d'exécution de la ligne suivante)
    t = m.getAttr(GRB.Attr.Runtime) - 0.01
    


    return v, m, t


def resolutionMultiRegretPondere(alpha,grille, gamma, proba, nbCriteres, nblignes, nbcolonnes):
    (A, b, obj) = dualRegretPondere(grille, gamma, proba, nbCriteres,alpha)
    v, m, t = gurobiMultiRegretPondere(A, b, obj, nblignes, nbcolonnes)
    somme = np.zeros(nbCriteres)
    for k in range(nbCriteres):
        for i in range (nblignes*nbcolonnes*4):
            somme[k] += A[k][i]*v[i].x
    print somme
  
    pol = minmax_multicritere.politique2(v, grille)
    return pol,v,somme    






################################################################################
#
#                            PRINCIPALE
#
################################################################################






nbl=3
nbc=3
nbcri=2     
g = np.zeros((3,3,2))
g[0,0,0]=1
g[0,1,0]=0
g[0,2,0]=0
g[1,0,0]=40
g[1,1,0]=1
g[1,2,0]=0
g[2,0,0]=40
g[2,1,0]=0
g[2,2,0]=1
g[0,0,1]=1
g[0,1,1]=40
g[0,2,1]=40
g[1,0,1]=0
g[1,1,1]=1
g[1,2,1]=40
g[2,0,1]=0
g[2,1,1]=0
g[2,1,0]=40
g[2,2,1]=1


alpha=[1,10]

pt= ptNadir(g,gamma,probaTransition,2)

print pt

pol,v,somme=resolutionMultiRegretPondere(alpha,g, gamma, probaTransition, 2, nbl, nbc)
    
print pol






