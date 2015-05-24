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
import plot

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
                    obj[(i*nbC+j)*4+k] = ponderation[l]*minmax_multicritere.valTrans(grille,i,j,k,l)#(grille[i,j,l]) 
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
    return pol,v#,somme

################################################################################
#
#                            TEST
#
################################################################################

        
#prend la matrice V et la met sous forme de tableau plus lisible    
def grilleV(v, nbl,nbc):
    grille=np.zeros((nbl,nbc))
    for i in range(nbl):
        for j in range (nbc):
            grille[i][j]= v[i*nbc+j].x
    return grille


def testSommePondere(g, gamma, probaTransition, nbcri,nbl,nbc,nbiteration):
    pas= 1.0/nbiteration  
    somme=np.zeros((nbiteration,nbcri))
    for it in range (1,nbiteration-1):
        ponderation=[pas*it,1 - (pas*it)]  
        print ponderation
        pol,v,somme1 = resolutionMultiSommePondere(g,ponderation, gamma, probaTransition, nbcri,nbl,nbc)
#        (A, b, obj) = dualSommePondere(g,ponderation, gamma, probaTransition, nbcri)
        print pol
        for l in range (nbcri):
            for i in range(nbl):
                for j in range (nbc):
                    for k in range (4):
                        somme[it][l]+= -1*minmax_multicritere.valTrans(g,i,j,k,l) *pol[i,j,k]
    print somme
    plot.affichePoint(somme)   

def transformeGrilleMultiIntoMono(g,critere):
    nbL=g.shape[0]
    nbC=g.shape[1]
    temp = np.zeros((nbL,nbC))
    for i in range (nbL):
        for j in range (nbC):
            temp[i][j]=g[i,j,critere]
    return temp

    
#prend la grille multicritere (mais avec solution pure) et la transforme en une grille solution monocritere
def createGrilleSoluceMixte(resultPL):
    grille = np.zeros((resultPL.shape[0],resultPL.shape[1]))
    for i in range (resultPL.shape[0]):
        for j in range (resultPL.shape[1]):
            valmax = 0
            indice = 0
            for k in range(resultPL.shape[2]):
                if resultPL[i][j][k] >= valmax:
                    indice = k
                    valmax = resultPL[i][j][k]
            grille[i][j]= indice
    return grille



def coutVs(v, politique ):
    cout = 0
    i = 0
    j = 0
    #cout += grille[i][j]
    #la première case ne coute rien
    while i != v.shape[0]-1 and j != v.shape[1]-1:
        if politique[i][j] == HAUT:
            i -= 1
        elif politique[i][j] == BAS:
            i += 1
        elif politique[i][j] == GAUCHE:
            j -= 1
        else: #politique[i][j] == DROITE
            j += 1
        cout += v[i][j]
    return cout

def gentionIndex (minmax, index):
    if (minmax[index][1] <minmax[index][0]):
        minmax[index][1] =minmax[index][0]
    else :
        minmax[index][0]=minmax[index][1]

def testMinMax( gamma, probaTransition, nbcri,nbl,nbc , nbtest):
    pondere1= np.zeros((nbtest,2))
    pondere2= np.zeros((nbtest,2))
    minmax= np.zeros((nbtest,2))
    for index in range(nbtest):
        
        g = defineMaze(nbl,nbc,nbcri)  
        
        print "CECI EST G"
        print g
        print "PLUS MAINTENANt"
        g0 = transformeGrilleMultiIntoMono(g,0)
        
        g1 = transformeGrilleMultiIntoMono(g,1)
        
        
        
        ponderation=[0.999,0.001]     
        
        print "poderation 1"
                
        pol,v,somme = resolutionMultiSommePondere(g,ponderation, gamma, probaTransition, nbcri,nbl,nbc)
        print "c'est bien mon truc"
        print pol
        print "valeur de l'op ="
        #print somme
        (A, b, obj) = dualSommePondere(g,ponderation, gamma, probaTransition, nbcri)
        #somme = 0
        #for i in range(nbl):
        #    for j in range (nbc):
        #        for k in range (4):
        #            somme+= obj[(i*nbc+j)*4+k] *pol[i,j,k]
        #print somme 
        
        
        
        #calcul des Vs pour les deux critères
#        polprime = createGrilleSoluceMixte(pol)
#        (A,b,obj)=rechercheVS(polprime,g0,gamma,probaTransition)
#        v,m,t = resolutionGurobirechercheVs(A,b,obj,nbl,nbc)
#        valeur = grilleV(v,nbl,nbc)
#        somme=0
#        for i in range (nbl):
#                for j in range (nbc):
#                    pondere1[index][0] += valeur[i][j]
#        pondere1[index][0]=coutVs(grilleV(v,nbl,nbc), createGrilleSoluceMixte(pol))
       
        
#        (A,b,obj)=rechercheVS(polprime,g1,gamma,probaTransition)
#        v,m,t = resolutionGurobirechercheVs(A,b,obj,nbl,nbc)
#        valeur = grilleV(v,nbl,nbc)
#        
#        somme=0
#        for i in range (nbl):
#                for j in range (nbc):
#                    pondere1[index][1] += valeur[i][j]
#        
        for i in range (nbl):
            for j in range (nbc):
                pondere1[index][0] +=   v[i*nbc+j].x *g[i,j,0]  #minmax_multicritere.valTrans(g,i,j,pol[i][j],0)
        
        for i in range (nbl):
            for j in range (nbc):
                pondere1[index][1] +=  v[i*nbc+j].x *g[i,j,1] #minmax_multicritere.valTrans(g,i,j,pol[i][j],1) *
#
        
        print "ponderation 2"
             
        ponderation=[0.001,0.999] 
        
        pol,v,somme = resolutionMultiSommePondere(g,ponderation, gamma, probaTransition, nbcri,nbl,nbc)
        print "c'est bien mon truc"
        print pol
        print "valeur de l'op ="
        (A, b, obj) = dualSommePondere(g,ponderation, gamma, probaTransition, nbcri)
        
        
        
        #calcul des Vs pour les deux critères
        polprime = createGrilleSoluceMixte(pol)
        (A,b,obj)=rechercheVS(polprime,g0,gamma,probaTransition)
        v,m,t = resolutionGurobirechercheVs(A,b,obj,nbl,nbc)
        valeur = grilleV(v,nbl,nbc)
        somme=0
#        for i in range (nbl):
#                for j in range (nbc):
#                    pondere1[index][0] += valeur[i][j]
        for i in range (nbl):
            for j in range (nbc):
                pondere2[index][0] +=   v[i*nbc+j].x *g[i,j,0]  #minmax_multicritere.valTrans(g,i,j,pol[i][j],0)
        
        for i in range (nbl):
            for j in range (nbc):
                pondere2[index][1] +=  v[i*nbc+j].x *g[i,j,1] #minmax_multicritere.valTrans(g,i,j,pol[i][j],1) *
#
        
#        (A,b,obj)=rechercheVS(polprime,g1,gamma,probaTransition)
#        v,m,t = resolutionGurobirechercheVs(A,b,obj,nbl,nbc)
#        valeur = grilleV(v,nbl,nbc)
#        
#        somme=0
#        for i in range (nbl):
#                for j in range (nbc):
#                    pondere1[index][1] += valeur[i][j]
#        
        pondere2[index][1]=coutVs(grilleV(v,nbl,nbc),createGrilleSoluceMixte(pol))
        
        
        
        
        print "minax"
        pol,v,somme = minmax_multicritere.resolutionMultiMinMax2v2(g, gamma, probaTransition, nbcri,nbl,nbc)
        print "c'est bien mon truc"
        print pol
        
        print "valeur de l'op ="
        (A, b, obj) = minmax_multicritere.dualMinMax2v2(g, gamma, probaTransition, nbcri)

        
#        #calcul des Vs pour les deux critères
#        polprime = createGrilleSoluceMixte(pol)
#        (A,b,obj)=rechercheVS(polprime,g0,gamma,probaTransition)
#        v,m,t = resolutionGurobirechercheVs(A,b,obj,nbl,nbc)
#        valeur = grilleV(v,nbl,nbc)
#        somme=0
        
        
        minmax[index][0]= somme[0]#coutVs(grilleV(v,nbl,nbc),createGrilleSoluceMixte(pol))
       
        
#        (A,b,obj)=rechercheVS(polprime,g1,gamma,probaTransition)
#        v,m,t = resolutionGurobirechercheVs(A,b,obj,nbl,nbc)
#        valeur = grilleV(v,nbl,nbc)
#        
##        somme=0
##        for i in range (nbl):
##                for j in range (nbc):
##                    pondere1[index][1] += valeur[i][j]
#        
        minmax[index][1]=somme[1]#coutVs(grilleV(v,nbl,nbc),createGrilleSoluceMixte(pol))
        
    return pondere1,pondere2,minmax



















def testMinMax2( gamma, probaTransition, nbcri,nbl,nbc , nbtest):
    pondere1= np.zeros((nbtest,2))
    pondere2= np.zeros((nbtest,2))
    minmax= np.zeros((nbtest,2))
    for index in range(nbtest):
        
#        g = defineMaze(nbl,nbc,nbcri)  
        
        print "CECI EST G"
        print g
        print "PLUS MAINTENANt"
        g0 = transformeGrilleMultiIntoMono(g,0)
        print "CECI EST G0"
        print g0
        print "PLUS MAINTENANt"
        g1 = transformeGrilleMultiIntoMono(g,1)
        print "CECI EST G1"
        print g1
        print "PLUS MAINTENANt"
        
        
        ponderation=[0.999,0.001]     
        
        print "poderation 1"
                
        
        (A, b, obj) = programmedual(g0, gamma,probaTransition)
        v, m,t = resolutionGurobidual(A, b, obj,nbl,nbc)
        print "v"
        print v 
        
        pol = modele_1critere.politique(v, g0,probaTransition,gamma)
        print "pol :"
        print pol
    
         #calcul des Vs pour les deux critères
#        polprime = createGrilleSoluceMixte(pol)
#        (A,b,obj)=rechercheVS(pol,g0,gamma,probaTransition)
#        v,m,t = resolutionGurobirechercheVs(A,b,obj,nbl,nbc)
#        valeur = grilleV(v,nbl,nbc)
#        somme=0

        for i in range (nbl):
                for j in range (nbc):
                    pondere1[index][0] +=   v[i*nbc+j].x *g[i,j,0]  #minmax_multicritere.valTrans(g,i,j,pol[i][j],0)
        
        for i in range (nbl):
                for j in range (nbc):
                    pondere1[index][1] +=  v[i*nbc+j].x *g[i,j,1] #minmax_multicritere.valTrans(g,i,j,pol[i][j],1) *
#        pondere1[index][0]=coutVs(grilleV(v,nbl,nbc), pol)
#       
#        
#        (A,b,obj)=rechercheVS(pol,g1,gamma,probaTransition)
#        v,m,t = resolutionGurobirechercheVs(A,b,obj,nbl,nbc)
#        valeur = grilleV(v,nbl,nbc)
        
#        somme=0
#        for i in range (nbl):
#                for j in range (nbc):
#                    pondere1[index][1] += valeur[i][j]
##        
#        pondere1[index][1]=coutVs(grilleV(v,nbl,nbc),pol)
#        
        
        
        
        print "poderation2"
                
        
        (A, b, obj) = programmedual(g1, gamma,probaTransition)
        v, m,t = resolutionGurobidual(A, b, obj,nbl,nbc)
        print "v"
        print v
        
        pol = modele_1critere.politique(v, g1,probaTransition,gamma)
        print "pol :"
        print pol
    
    
    
    

        for i in range (nbl):
            for j in range (nbc):
                pondere2[index][0] +=   v[i*nbc+j].x *g[i,j,0]  #minmax_multicritere.valTrans(g,i,j,pol[i][j],0)
        
        for i in range (nbl):
            for j in range (nbc):
                pondere2[index][1] +=  v[i*nbc+j].x *g[i,j,1] #minmax_multicritere.valTrans(g,i,
#        #calcul des Vs pour les deux critères
##        polprime = createGrilleSoluceMixte(pol)
#        (A,b,obj)=rechercheVS(pol,g0,gamma,probaTransition)
#        v,m,t = resolutionGurobirechercheVs(A,b,obj,nbl,nbc)
#        valeur = grilleV(v,nbl,nbc)
#        somme=0
##        for i in range (nbl):
##                for j in range (nbc):
##                    pondere1[index][0] += valeur[i][j]
#        pondere2[index][0]=coutVs(grilleV(v,nbl,nbc), pol)
#       
#        
#        (A,b,obj)=rechercheVS(pol,g1,gamma,probaTransition)
#        v,m,t = resolutionGurobirechercheVs(A,b,obj,nbl,nbc)
#        valeur = grilleV(v,nbl,nbc)
#        
#        somme=0
#        for i in range (nbl):
#                for j in range (nbc):
#                    pondere1[index][1] += valeur[i][j]
#        
#        pondere2[index][1]=coutVs(grilleV(v,nbl,nbc),pol)
        
        print "minax"
        pol,v,somme = minmax_multicritere.resolutionMultiMinMax2v2(g, gamma, probaTransition, nbcri,nbl,nbc)
#        v= grilleV(v)
        print "c'est bien mon truc"
        print pol
        
       
       
        polprime= createGrilleSoluceMixte(pol)
        for i in range (nbl):
                for j in range (nbc):
                    minmax[index][0] += somme[0]#minmax_multicritere.valTrans(g,i,j,polprime[i][j],0) * v[i*nbc+j]

        for i in range (nbl):
                for j in range (nbc):
                    minmax[index][1] += somme[1]#minmax_multicritere.valTrans(g,i,j,polprime[i][j],1) * v[i*nbc+j]
#       
       
#        #calcul des Vs pour les deux critères
#        polprime = createGrilleSoluceMixte(pol)
#        (A,b,obj)=rechercheVS(polprime,g1,gamma,probaTransition)
#        v,m,t = resolutionGurobirechercheVs(A,b,obj,nbl,nbc)
#        valeur = grilleV(v,nbl,nbc)
#
#        minmax[index][0]=coutVs(grilleV(v,nbl,nbc), createGrilleSoluceMixte(pol))
#        print "politique"
#        print createGrilleSoluceMixte(pol)
#        
#        (A,b,obj)=rechercheVS(polprime,g1,gamma,probaTransition)
#        v,m,t = resolutionGurobirechercheVs(A,b,obj,nbl,nbc)
#        valeur = grilleV(v,nbl,nbc)
        
#        
#        minmax[index][1]=coutVs(grilleV(v,nbl,nbc),createGrilleSoluceMixte(pol));gentionIndex (minmax, index)
    return pondere1,pondere2,minmax
           
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
#
#     
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
#g[2,1,0]=1
#g[2,2,0]=1
#g[2,3,0]=40
#g[3,0,0]=0
#g[3,1,0]=0
#g[3,2,0]=0
#g[3,3,0]=1
#g[0,0,1]=1
#g[0,1,1]=0
#g[0,2,1]=0
#g[0,3,1]=0
#g[1,0,1]=40
#g[1,1,1]=1
#g[1,2,1]=1
#g[1,3,1]=0
#g[2,0,1]=40
#g[2,1,1]=1
#g[2,2,1]=1
#g[2,3,1]=0
#g[3,0,1]=40
#g[3,1,1]=40
#g[3,2,1]=40
#g[3,3,1]=1


#nbl=5
#nbc=5
#nbcri=2     
#g = np.zeros((5,5,2))
#g[0,0,0]=1
#g[0,1,0]=40
#g[0,2,0]=40
#g[0,3,0]=40
#g[0,4,0]=40
#g[1,0,0]=0
#g[1,1,0]=1
#g[1,2,0]=1
#g[1,3,0]=1
#g[1,4,0]=40
#g[2,0,0]=0
#g[2,1,0]=1
#g[2,2,0]=1
#g[2,3,0]=40
#g[2,4,0]=40
#g[3,0,0]=0
#g[3,1,0]=1
#g[3,2,0]=1
#g[3,3,0]=1
#g[3,4,0]=40
#g[4,0,0]=0
#g[4,1,0]=0
#g[4,2,0]=0
#g[4,3,0]=0
#g[4,4,0]=1
#g[0,0,1]=1
#g[0,1,1]=0
#g[0,2,1]=0
#g[0,3,1]=0
#g[0,4,1]=0
#g[1,0,1]=40
#g[1,1,1]=1
#g[1,2,1]=1
#g[1,3,1]=0
#g[1,4,1]=0
#g[2,0,1]=40
#g[2,1,1]=1
#g[2,2,1]=1
#g[2,3,1]=0
#g[2,4,1]=0
#g[3,0,1]=40
#g[3,1,1]=40
#g[3,2,1]=40
#g[3,3,1]=40
#g[3,4,1]=40
#g[4,0,1]=40
#g[4,1,1]=40
#g[4,2,1]=40
#g[4,3,1]=40
#g[4,4,1]=1
#




     
"""
#g= defineMaze(nbl,nbc,nbcri)
print g

g0 = transformeGrilleMultiIntoMono(g,0)

g1 = transformeGrilleMultiIntoMono(g,1)


gamma= 0.8
probaTransition=0.8

        
#print somme 


pondere1,pondere2,minmax=testMinMax( gamma, probaTransition, nbcri,nbl,nbc , 5)

print "pondere1"
print pondere1

print "pondere2"
print pondere2

print "minmax"
print minmax
"""




#g0 = transformeGrilleMultiIntoMono(g,0)
#
#g1 = transformeGrilleMultiIntoMono(g,1)
#
#
##
##ponderation=[0.0001,0.9999]  
#ponderation=[1000,0.0001]   
#
#print "poderation 1"
#(A, b, obj) = dualSommePondere(g,ponderation, gamma, probaTransition, nbcri)
#print obj        
#ponderation=[0.0000,100000]   
#
#print "poderation 1"
#(A, b, obj) = dualSommePondere(g,ponderation, gamma, probaTransition, nbcri)
#print obj        
#pol,v,somme = resolutionMultiSommePondere(g,ponderation, gamma, probaTransition, nbcri,nbl,nbc)
#print "c'est bien mon truc"
#print pol


#(A, b, obj) = programmeprimal(g0, gamma,probaTransition)
#v1, m,t = resolutionGurobiprimal(A, b, obj,nbl,nbc)
#
#
#pol = modele_1critere.politique(v1, g0,probaTransition,gamma)
#print "pol :"
#print pol
#
#print "v **********************************************************************"
#print coutVs(grilleV(v1,nbl,nbc),pol)
#
#
##calcul des Vs pour les deux critères
#(A,b,obj)=rechercheVS(pol,g1,gamma,probaTransition)
#v,m,t = resolutionGurobirechercheVs(A,b,obj,nbl,nbc)
#valeur = grilleV(v,nbl,nbc)
#print "cherche vs"
#print coutVs(grilleV(v,nbl,nbc),pol)
#   

#(A,b,obj)=rechercheVS(pol,g1,gamma,probaTransition)
#v,m,t = resolutionGurobirechercheVs(A,b,obj,nbl,nbc)
#valeur = grilleV(v,nbl,nbc)
#
#print valeur
#
