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


'''        
            
################################################################################
#
#                            PROGRAMME SANS ETAT PUITS
#
################################################################################


                

def dualMinMax2(grille, gamma, proba, nbcritere):
    nbl=grille.shape[0]
    nbc=grille.shape[1]
    a= np.zeros((nbcritere+ ((nbl*nbc))*(4+1),(nbl*nbc)*4+1))
    b= np.zeros(nbcritere+ ((nbl*nbc))*(4+1))
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
                    a[l][(i*nbc+j)*4+k]=1* valTrans(grille,i,j,k,l) #-1* grille[i,j,l]
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
#                    '' if (iprime == nbl-1 and jprime==nbc -1):
#                        a[nbcritere+nbc*iprime+jprime][(i*nbc+j)*4+k]=  0 
#                    else:''
                    a[nbcritere+nbc*iprime+jprime][(i*nbc+j)*4+k]= -1* gamma * trans[t] 
    #seul la premiere case a un u(s) a 1                 
    b[nbcritere]=1
    #Xsa > 0            
    for i in range ((nbl*nbc)*4):
        a[nbcritere+(nbl*nbc)+i][i]=1
        b[nbcritere+(nbl*nbc)+i]=0
        
        
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
    print "*****************************************"
    for i in range (nbl*nbc*4):
        print "x"+str(i/4 +1)+"= "+str(v[i].x)
    print a[0]
    print a[1]
    z1=0
    z2=0
    for i in range((nbl *nbc)*4):
        z1+= a[0][i]*v[i].x
        z2+= a[1][i]*v[i].x
    print "z1"
    print z1
    print "z2"
    print z2
    print "z"
    print v[nbl*nbc*4].x
    print "************************************************"
    
    #temps de résolution (-0.01 pour compenser le temps d'exécution de la ligne suivante)
    t = m.getAttr(GRB.Attr.Runtime) - 0.01
    
    return v, m, t
    



def resolutionMultiMinMax2(grille, gamma, proba, nbCriteres, nblignes, nbcolonnes):
    (A, b, obj) = dualMinMax2(grille, gamma, proba, nbCriteres)
    v, m, t = gurobiMultiMinMax2(A, b, obj, nblignes, nbcolonnes)
    print "v"
    print v
    pol = politique2(v, grille)
    return pol,v




           
################################################################################
#
#                            MIN MAX SANS VARIABLE INUTILE
#
################################################################################
 


def dualMinMaxSB(grille, gamma, proba, nbcritere):
    nbl=grille.shape[0]
    nbc=grille.shape[1]
    #il y a -1 variable par ligne a coter du bard et par colonne a coter du bord
    a= np.zeros((nbcritere+ ((nbl*nbc)+1)*(4+1)-2*(nbl+nbc),(nbl*nbc)*4+1+4)-2*(nbl+nbc))
    b= np.zeros(nbcritere+ ((nbl*nbc)+1)*(4+1)-2*(nbl+nbc))
    obj= np.zeros((nbl*nbc)*4+1+4 -2*(nbl+nbc))
    #on maximize z (le dernier critere)
    obj[(nbl*nbc)*4+1-1 -2*(nbl+nbc)]=1
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
                if (i != nbl-1 and j!=nbc -1):
                    for t in trans:
                        iprime = t[0]
                        jprime= t[1]
#                        '' if (iprime == nbl-1 and jprime==nbc -1):
#                            a[nbcritere+nbc*iprime+jprime][(i*nbc+j)*4+k]=  0 
#                        else:''
                        a[nbcritere+nbc*iprime+jprime][(i*nbc+j)*4+k]= -1* gamma * trans[t] 
    #seul la premiere case a un u(s) a 1                 
    b[nbcritere]=1
    #Xsa > 0            
    for i in range ((nbl*nbc)*4-2*(nbl+nbc)):
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
        


def gurobiMultiMinMaxSB(a, b, objectif, nblignes, nbcolonnes):
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


def resolutionMultiMinMaxSB(grille, gamma, proba, nbCriteres, nblignes, nbcolonnes):
    (A, b, obj) = dualMinMax2v2(grille, gamma, proba, nbCriteres)
    v, m, t = gurobiMultiMinMax2v2(A, b, obj, nblignes, nbcolonnes)
    print "v"
    print v
    pol = politique2(v, grille)
    return pol,v

 
 
################################################################################
#
#                            REGRET MINIMUM
#
################################################################################

    
            
def minMaxRegret(A,objectif,b,grille,gamma,proba,indiceCritere,indiceXsa,nbcri):
    nbl= grille.shape[0]
    nbc=grille.shape[1]
    valMax = np.zeros((nbl,nbc,nbcri))
    #grille temporaire pour le monocritère
    grilletemp =np.zeros((nbl,nbc))
    #taille de la matrice de contrainte
    la = A.shape[0]
    ca = A.shape[1]
    #nouvelle matrice de contrainte
    Aprime =np.zeros((la+1,ca+nbl*nbc))
    for i in range (nbcri):
        #isole un critere dans une grille
        for j in range(nbl):
            for k in range (nbc):
                grilletemp[j][k] = grille[j,k,i]
        #résout le primal pour un critère et récupère les Vs*
        (A, b, obj) = programmeprimal(grilletemp, gamma, proba)
        v, m, t = resolutionGurobiprimal(A, b, obj,nbl,nbc)
        #copie les Vs*
        for j in range(nbl):
            for k in range (nbc):
                valMax[j][k][i]= v[j*nbc+k].x
                #rajoute les contraintes dû au regret
                Aprime[indiceCritere+i][ca+j*nbc+k]= valMax[j][k][i]
    #copie ce qui ne change pas de la matrice de contrainte             
    for i in range (la):
        for j in range(ca):
            Aprime[i][j] = A[i][j]
    #ajoute la contrainte des Zs
    for i in range(nbl*nbc):
        Aprime[indiceXsa+ i][ca+i]=-1
        #somme des Zs <1
        Aprime[la][ca+i]=1
        
    #nouveau second membre
    bprime = np.zeros(la+1)
    for i in range (la):
        bprime[i]= b[i]
    bprime[la]=1
    
    #nouveau objectif
    objprime= np.zeros(ca+nbl*nbc)
    for i in range (ca):
        objprime[i]=objectif[i]
    return Aprime,bprime, objprime 
            
        
                
                

def gurobiMultiMinMaxRegret(a, b, objectif, nblignes, nbcolonnes):
    m = Model("MOPDMeq")
    #déclaration des variables de décision
    v = []
    for i in range(len(objectif)-1-4-nblignes*nbclonnes):
        v.append(m.addVar(vtype=GRB.SEMICONT, lb=0, name="x%d" % (i+1)))
    v.append(m.addVar(vtype=GRB.SEMICONT, lb=0, name="z"))
    for i in range(len(objectif)-4-nblignes*nbclonnes,len(objectif)-nblignes*nbclonnes):
        v.append(m.addVar(vtype=GRB.SEMICONT, lb=0, name="p%d" % (i+1)))
    for i in range (len(objectif)-nblignes*nbclonnes,len(objectif)):
        v.append(m.addVar(vtype=GRB.SEMICONT, lb=0, name="p%d" % (i+1)))
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
    for i in range(nblignes*nbcolonnes+nbcriteres, a.shape[0]-1-1):
        m.addConstr(LinExpr(a[i], v) >= b[i], "Contrainte%d" % i)
    for i in range(a.shape[0]-1-1, a.shape[0]-1):
        m.addConstr(LinExpr(a[i], v) == b[i], "Contrainte%d" % i)
    m.addConstr(LinExpr(a[len(b)-1], v) <= b[len(b)-1], "Contrainte%d" % i)
    #résolution
    m.optimize()
    
    #temps de résolution (-0.01 pour compenser le temps d'exécution de la ligne suivante)
    t = m.getAttr(GRB.Attr.Runtime) - 0.01
    
    return v, m, t    
    
    
    
       

def resolutionMultiMinMaxRegret(grille, gamma, proba, nbCriteres, nblignes, nbcolonnes):
    (A, b, obj) = dualMinMax2v2(grille, gamma, proba, nbCriteres)
    (A, b, obj) = regretminimum(A, b, obj,grille ,gamma,proba,0,nbCriteres,nbCriteres)
    v, m, t = gurobiMultiMinMaxRegret(A, b, obj, nblignes, nbcolonnes)
    print "v"
    print v
    pol = politique2(v, grille)
    return pol,v        

################################################################################
#
#                            TEST
#
################################################################################

def testNadir(g,gamma,probaTransition,nbcri):
    print "***********************************************************************"
    print ptNadir(g,gamma,probaTransition,nbcri)
    print "************************************************************************"
    temp=np.zeros((nbl,nbc))
    for i in range (nbl):
        for j in range (nbc):
            temp[i][j]=g[i,j,0]
    (A, b, obj) = modele_1critere.programmeprimal(temp, gamma,probaTransition)
    v, m, t = modele_1critere.resolutionGurobiprimal(A, b, obj,nbl,nbc)
    print "**************************************************************************"
    print "grille critere 1"
    print grilleV(v,nbl,nbc)
    print "***************************************************************************"
    for i in range (nbl):
        for j in range (nbc):
            temp[i][j]=g[i,j,1]
    (A, b, obj) = modele_1critere.programmeprimal(temp, gamma,probaTransition)
    v, m, t = modele_1critere.resolutionGurobiprimal(A, b, obj,nbl,nbc)
    print "****************************************************************************"
    print "grille critere 2"
    print grilleV(v,nbl,nbc)
    
    
    

    
'''            
################################################################################
#
#                            PROGRAMME AVEC ETAT PUITS
#
################################################################################
        
        
        
        

def dualMinMax2(grille, gamma, proba, nbcritere):
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
        


def gurobiMultiMinMax2(a, b, objectif, nblignes, nbcolonnes):
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
    
    print v

    return v, m, t


def resolutionMultiMinMax2(grille, gamma, proba, nbCriteres, nblignes, nbcolonnes):
    (A, b, obj) = dualMinMax2(grille, gamma, proba, nbCriteres)
    v, m, t = gurobiMultiMinMax2(A, b, obj, grille.shape[0],grille.shape[1] )
    pol = politique(v, grille)
#    somme = np.zeros(nbCriteres)
#    for k in range(nbCriteres):
#        for i in range (nblignes*nbcolonnes*4):
#            somme[k] += A[k][i]*v[i].x
#    print somme
  
   
    return pol,v#,somme    
    
    
            
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
     