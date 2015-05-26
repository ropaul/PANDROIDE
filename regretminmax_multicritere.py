# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 09:54:03 2015

@author: teddy
"""
#
from modele_1critere import *
from modele_multicritere import *
from gurobipy import *
import random
import numpy as np
import math
#import RegretPondere


            
################################################################################
#
#                            fonction utile
#
################################################################################


#donne la valeur Rsa pour une transition direction a la case (i,j)
def valTrans(g,i,j,direction,critere):
    nbl=g.shape[0]
    nbc=g.shape[1]
#    if (i == nbl-1 and j==nbc -1):
#        return 0
    #si en haut
    if (direction == 0 ):
        if(i <=0 ):
            return 1000
        else :
            if (i-1 == nbl-1 and j==nbc -1):
                return valBut(nbl,nbc)
            else :
                return g[i-1,j,critere]
    #si en bas
    if (direction == 1 ):
        if(i >= nbl-1 ):
            return 1000
        else :
            if (i +1== nbl -1 and j==nbc -1):
                return valBut(nbl,nbc)
            else :
                return g[i+1,j,critere]
    #si a gauche
    if (direction == 2 ):
        if(j <=0 ):
            return 1000
        else :
            if (i == nbl -1 and j-1==nbc -1):
                return valBut(nbl,nbc)
            else :
                return g[i,j-1,critere]
    #si en haut
    if (direction == 3 ):
        if(j >= nbc -1 ):
            return 1000
        else :
            if (i == nbl -1 and j+1==nbc -1):
                return valBut(nbl,nbc)
            else :
                return g[i,j+1,critere]
    
    
def valBut(nblignes, nbcolonnes):
    return -1*nblignes*nbcolonnes*100
    



def politique2(valeurs, grille):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
#    print grille.shape
#    print len(valeurs)
    pol = np.zeros((nbL,nbC,4))
    for i in range(nbL):
        for j in range(nbC):
            for k in range(4):
                pol[i][j][k] = valeurs[(i*nbC+j)*4+k].x
            somme = sum(pol[i][j])
            if somme != 0 :
                for k in range(4):
                    pol[i][j][k] /= somme
    return pol        



    
            
################################################################################
#
#                            REGRET MIN MAX
#
################################################################################
        
# Définition du PL dual de l'approche regret minmax
# contraintes (1) : sum(Xsa pourtout a) - gamma*sum(sum(T(s',a,s)*Xsa pourtout a) pourtout s') = µ(s) pourtout s
# contraintes (2) : Xsa >= 0 pourtout s, pourtout a
# contraintes (3) : z + sum(sum(Ri(s,a)*Xsa pourtout a) pourtout s) <= V*i pourtout i
def dualRegretMinMax2(grille, gamma, proba, nbCriteres):
    #vstar = Vstar(grille, gamma, proba, nbCriteres)
    vstar= calculVsEtoile(grille,gamma,proba,nbCriteres)
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


def resolutionMultiRegretMinMax2(grille, gamma, proba, nbCriteres, nblignes, nbcolonnes):
    (A, b, obj) = dualRegretMinMax2(grille, gamma, proba, nbCriteres)
    v, m, t = gurobiMultiMinMax(A, b, obj, nblignes, nbcolonnes)
    pol = politique(v, grille)
    return pol        
        
        

def dualRegret2(grille, gamma, proba, nbcritere):
    nbl=grille.shape[0]
    nbc=grille.shape[1]
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
                    a[l][(i*nbc+j)*4+k]=1* valTrans(grille,i,j,k,l) #-1* grille[i,j,l]
        #second memebre a zero
        tempG = np.zeros((nbl,nbc))
        for i in range (nbl):
            for j in range (nbc):
                tempG[i][j]=grille[i,j,l]
        (A0, b0, obj0) = modele_1critere.programmeprimal(tempG, gamma,probaTransition)
        v, m, t = modele_1critere.resolutionGurobiprimal(A0, b0, obj0,nbl,nbc)
        vs = grilleV(v,nbl,nbc)
        somme= 0
        for i in range (nbl):
            for j in range (nbc):
                somme += vs[i][j]
        print "*****************************************************"
        print "somme" +str(somme)
        b[l]= somme
        print "****************************************************"
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
#                    '' if (iprime == nbl-1 and jprime==nbc -1):
#                        a[nbcritere+nbc*iprime+jprime][(i*nbc+j)*4+k]=  0 
#                    else:''
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
        


def resolutionMultiRegret2(grille, gamma, proba, nbCriteres, nblignes, nbcolonnes):
    (A, b, obj) = dualRegret2(grille, gamma, proba, nbCriteres)
    v, m, t = gurobiMultiMinMax(A, b, obj, nblignes, nbcolonnes)
    
    pol = politique(v, grille)
    return pol,v   
           
################################################################################
#
#                            PROGRAMME PRINCIPAL
#
################################################################################
 
#nbl=2
#nbc=2
#nbcri=2     
#g = np.ones((2,2,2))
#g[1,0,0]=0
#g[0,1,1]=0

#nbl=2
#nbc=2
#nbcri=2 
#g = np.ones((2,2,2))
#g[0,1,0]=0
#g[1,0,1]=0


#nbl=3
#nbc=3
#nbcri=2     
#g = np.zeros((3,3,2))
#g[0,0,0]=1
#g[0,1,0]=0
#g[0,2,0]=0
#g[1,0,0]=40
#g[1,1,0]=1
#g[1,2,0]=0
#g[2,0,0]=40
#g[2,1,0]=0
#g[2,2,0]=1
#g[0,0,1]=1
#g[0,1,1]=40
#g[0,2,1]=40
#g[1,0,1]=0
#g[1,1,1]=1
#g[1,2,1]=40
#g[2,0,1]=0
#g[2,1,1]=0
#g[2,1,0]=40
#g[2,2,1]=1

     
#nbl=4
#nbc=4
#nbcri=2     
#g = np.zeros((4,4,2))
#g[0,0,0]=1
#g[0,1,0]=40
#g[0,2,0]=40
#g[0,3,0]=40
#g[1,0,0]=0
#g[1,1,0]=1
#g[1,2,0]=1
#g[1,3,0]=40
#g[2,0,0]=0
#g[2,1,0]=100
#g[2,2,0]=100
#g[2,3,0]=40
#g[3,0,0]=0
#g[3,1,0]=0
#g[3,2,0]=0
#g[3,3,0]=100
#g[0,0,1]=100
#g[0,1,1]=0
#g[0,2,1]=0
#g[0,3,1]=0
#g[1,0,1]=40
#g[1,1,1]=100
#g[1,2,1]=100
#g[1,3,1]=0
#g[2,0,1]=40
#g[2,1,1]=100
#g[2,2,1]=100
#g[2,3,1]=0
#g[3,0,1]=40
#g[3,1,1]=40
#g[3,2,1]=40
#g[3,3,1]=1
"""
nbl=15
nbc=15
nbcri=4
     

g= defineMaze(nbl,nbc,nbcri)





print g

gamma= 0.8
probaTransition=0.8
pol =   resolutionMultiRegretMinMax2(g, gamma, probaTransition, nbcri,nbl,nbc)
print "c'est bien mon truc"
print pol
"""
#temp = np.zeros((nbl,nbc))
#for i in range (nbl):
#    for j in range (nbc):
#        temp[i][j]=g[i,j,0]
#
#pol = resolution(temp, gamma, probaTransition)
#print "c'est bien mon truc"
#print pol







#z1=0
#z2=0
#for i in range((nbl *nbc)*4):
#    z1+= A[0]*v[i].x
#    z2+= A[1]*v[i].x
#print "z1"
#print z1
#print "z2"
#print z2
        
#print "b"  
#print b     
     