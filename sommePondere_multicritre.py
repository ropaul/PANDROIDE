# -*- coding: utf-8 -*-
"""
Created on Tue May 19 13:57:46 2015

@author: teddy
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
#            FONCTIONS DE RESOLUTION (OBJECTIF = SOMME DES CRITERES)
#
################################################################################


#donne la solution lorsque l'on pondère un critère plutot qu'un autre. Il faut que pondération soit de la taille de nbCritre
def dualSommePondere(grille,ponderation, gamma, proba, nbCriteres):
    nbL=grille.shape[0]
    nbC=grille.shape[1]
    #Matrice des contraintes + second membre
    A = np.zeros((nbL*nbC*(4+1), nbL*nbC*4))
    b = np.zeros(nbL*nbC*(4+1))
    for i in range(nbL):
        for j in range(nbC):
#            b[i*nbC+j]=0
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
#    b[0]=1
    #fonction objectif
    obj = np.zeros(nbL*nbC*4)
    for i in range(nbL):
        for j in range(nbC):
            for k in range(4):
#                obj[(i*nbC+j)*4+k] = sum(grille[i,j])
                for l in range (nbCriteres):
                    obj[(i*nbC+j)*4+k] = ponderation[l]*(grille[i,j,l])
    #case d'arrivée
    for k in range(4):
        obj[(nbL*nbC-1)*4+k] = -valBut(nbL,nbC)
    return (A, b, obj)
                



def resolutionMultiSommePondere(grille,ponderation, gamma, proba, nbCriteres, nblignes, nbcolonnes):
    (A, b, obj) = dualSommePondere(grille,ponderation, gamma, proba, nbCriteres)
    v, m, t = gurobiMultiSomme(A, b, obj, nblignes, nbcolonnes)
    pol = politique(v, grille)
    debut =0
    fin = len(v)
    somme =0
    for i in range (debut,fin):
        somme += obj[i]*v[i].x
    print somme
    return pol,v,somme,



           
################################################################################
#
#                            PROGRAMME PRINCIPAL
#
################################################################################
 
#donne la valeur de l'optimisation pour un critère 
#debut et fin definit le debut des critrere de v qui sont les variable Xsa
#obj est le vecteur d'optimisation
def valV(obj,v,debut,fin):
    somme =0
    for i in range (debut,fin):
        print v[i].x
#        somme += obj[i]*v[i].x
    return somme



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


def testSommePondere(g, gamma, probaTransition, nbcri,nbl,nbc,pas):
    nbiteration= 1/pas    
    for i in range (1,nbitearation-1):
        ponderation=[pas*i,1 - (pas*i)]     
        pol,v,somme = resolutionMultiSommePondere(g,ponderation, gamma, probaTransition, nbcri,nbl,nbc)
        (A, b, obj) = dualSommePondere(g,ponderation, gamma, probaTransition, nbcri)
        somme = np.zeros(nbcri)
        for l in range (nbcri):
            for i in range(nbl):
                for j in range (nbc):
                    for k in range (4):
                        somme[l+= g[i,j,0] *pol[i,j,k]
            print somme   







print "poderation 1"
     
ponderation=[0.99,0.01]     

#g= defineMaze(nbl,nbc,nbcri)
print g

gamma= 0.8
probaTransition=0.8
pol,v,somme = resolutionMultiSommePondere(g,ponderation, gamma, probaTransition, nbcri,nbl,nbc)
print "c'est bien mon truc"
print pol
print "valeur de l'op ="
#print somme
(A, b, obj) = dualSommePondere(g,ponderation, gamma, probaTransition, nbcri)
somme = 0
for i in range(nbl):
    for j in range (nbc):
        for k in range (4):
            somme+= obj[(i*nbc+j)*4+k] *pol[i,j,k]
print somme 


print "ponderation 2"
     
ponderation=[0.01,0.99] 

pol,v,somme = resolutionMultiSommePondere(g,ponderation, gamma, probaTransition, nbcri,nbl,nbc)
print "c'est bien mon truc"
print pol
print "valeur de l'op ="
(A, b, obj) = dualSommePondere(g,ponderation, gamma, probaTransition, nbcri)
somme = 0
for i in range(nbl):
    for j in range (nbc):
        for k in range (4):
            somme+= obj[(i*nbc+j)*4+k] *pol[i,j,k]
print somme 


print "minax"
pol,v,somme = minmax_multicritere.resolutionMultiMinMax2v2(g, gamma, probaTransition, nbcri,nbl,nbc)
print "c'est bien mon truc"
print pol

print "valeur de l'op ="
(A, b, obj) = minmax_multicritere.dualMinMax2v2(g, gamma, probaTransition, nbcri)

somme = 0
for i in range(nbl):
    for j in range (nbc):
        for k in range (4):
            somme+= A[0][(i*nbc+j)*4+k] *pol[i,j,k]
print somme 



somme = 0
for i in range(nbl):
    for j in range (nbc):
        for k in range (4):
            somme+= A[1][(i*nbc+j)*4+k] *pol[i,j,k]
print somme 




