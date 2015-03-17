# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 10:33:41 2015

@author: teddy & rose-may
"""

# script pion.py
from Tkinter import *
from gurobipy import *
import random
import numpy as np


zoom=4


pblanc=0.15
pverte=0.35
pbleue=0.25
prouge=0.15
pnoire=0.10


#taille de la grille
nblignes=5
nbcolonnes=5

probaTransition = 0.8


#poition initiale du robot la grille
posX=0
poxY = 0

#Position initial du robot dans le dessin
PosX = 20+10*zoom 
PosY = 20+10*zoom

# Creation d'un widget Canvas (pour la grille)
Largeur = zoom*20*nbcolonnes+40
Hauteur = zoom*20*nblignes+40


 
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


# def des couleurs
myred="#D20B18"
mygreen="#25A531"
myblue="#0B79F7"
mygrey="#E8E8EB"
myyellow="#F9FB70"
myblack="#2D2B2B"
mywalls="#5E5E64"
mywhite="#FFFFFF"
color=[mywhite,mygreen,myblue,myred,myblack]


def initialize():
    global cost
# position initiale du robot
    
    for k in range(5):
        cost[k]=0
# cout et affichage
    Canevas.coords(Pion,PosX -9*zoom, PosY -9*zoom, PosX +9*zoom, PosY +9*zoom)
    w.config(text='Cost = '+ str(cost[0]))



def defineMaze(nblignes,nbcolonnes):
    g= np.zeros((nblignes,nbcolonnes), dtype=numpy.int)
    for i in range(nblignes):
        for j in range(nbcolonnes):
            z=np.random.uniform(0,1)
            if z < pblanc+ pverte:
                g[i,j]=1
            else:
                if z < pblanc+ pverte + pbleue:
                    g[i,j]=2
                else:
                    if z< pblanc+ pverte + pbleue +prouge:
                        g[i,j]=3
                    else:
                        g[i,j]=4
                        
    #A REMPLACER PAR UNE FONCTION DE TEST D'INTEGRITE DU LABYRINTHE
    g[0,0]=np.random.random_integers(3)
    g[0,1]=np.random.random_integers(3)
    g[2,0]=np.random.random_integers(3)     
    g[nblignes-1,nbcolonnes-1]=np.random.random_integers(3)
    g[nblignes-2,nbcolonnes-1]=np.random.random_integers(3)
    g[nblignes-1,nbcolonnes-2]=np.random.random_integers(3)
    
    return g

#Définit la grille ET la dessine
def colordraw(nblignes,nbcolonnes):
    g = defineMaze(nblignes,nbcolonnes)
    for i in range(nblignes):
        for j in range(nbcolonnes):          
            y =zoom*20*i+20
            x =zoom*20*j+20
            if g[i,j]>0:            
                Canevas.create_oval(x+zoom*(10-3),y+zoom*(10-3),x+zoom*(10+3),y+zoom*(10+3),width=1,outline=color[g[i,j]],fill=color[g[i,j]])
            else:
                Canevas.create_rectangle(x, y, x+zoom*20, y+zoom*20, fill=myblack)
                Canevas.create_rectangle(x, y, x+zoom*20, y+zoom*20, fill=myblack)

def Clavier(event):
    global PosX,PosY,cost,g
    touche = event.keysym
    cj=(PosX-30)/(20*zoom)
    li=(PosY-30)/(20*zoom)
    #print(li,cj)
    # deplacement vers le haut
    if touche == 'space':
        if (cj+li)%2==0:
            touche = 'm'
        else:
             touche ='q'
    if touche == 'a' and li>0 and g[li-1,cj]>0:
        PosY -= zoom*20
        cost[g[li-1,cj]]+=1        
    # deplacement vers le bas
    if touche == 'q' and li<nblignes-1 and g[li+1,cj]>0:
        PosY += zoom*20
        cost[g[li+1,cj]]+=1
    # deplacement vers la droite
    if touche == 'm' and cj< nbcolonnes-1 and g[li,cj+1]>0:
        PosX += zoom*20
        cost[g[li,cj+1]]+=1
    # deplacement vers la gauche
    if touche == 'l' and cj >0 and g[li,cj-1]>0:
        PosX -= zoom*20
        cost[g[li,cj-1]]+=1
    # on dessine le pion a sa nouvelle position
    Canevas.coords(Pion,PosX -9*zoom, PosY -9*zoom, PosX +9*zoom, PosY +9*zoom)
    cost[0]=0    
    for k in range(4):
        cost[0]+=cost[k+1]*weight[k+1]
    w.config(text='Cost = '+ str(cost[0]))

#retourne laloi de probabilité de transition pour une action direction et une position (posX, posY) données.
def transition(g, direction, posX, posY):
    trans = {}
    if direction == HAUT and posX != 0:
        if g[posX-1, posY] != 0:
            if g[posX-1, posY-1] == 0 and g[posX-1, posY+1]==0 :
                trans[posX-1, posY] = 1
            else:
                if g[posX-1, posY-1] == 0:
                    trans[posX-1, posY] = (1 + probaTransition)/2
                    trans[posX-1, posY+1] = (1 - probaTransition)/2
                else:
                    if g[posX-1, posY+1] == 0:
                        trans[posX-1, posY] = (1 + probaTransition)/2
                        trans[posX-1, posY-1] = (1 - probaTransition)/2
                    else:
                        trans[posX-1, posY] = probaTransition
                        trans[posX-1, posY+1] = (1 - probaTransition)/2
                        trans[posX-1, posY-1] = (1 - probaTransition)/2
    if direction == BAS and posX != nblignes-1:
        if g[posX+1, posY] != 0:
            if g[posX+1, posY-1] == 0 and g[posX+1, posY+1]==0 :
                trans[posX+1, posY] = 1
            else:
                if g[posX+1, posY-1] == 0:
                    trans[posX+1, posY] = (1 + probaTransition)/2
                    trans[posX+1, posY+1] = (1 - probaTransition)/2
                else:
                    if g[posX+1, posY+1] == 0:
                        trans[posX+1, posY] = (1 + probaTransition)/2
                        trans[posX+1, posY-1] = (1 - probaTransition)/2
                    else:
                        trans[posX+1, posY] = probaTransition
                        trans[posX+1, posY+1] = (1 - probaTransition)/2
                        trans[posX+1, posY-1] = (1 - probaTransition)/2
    if direction == GAUCHE and posY != 0:
        if g[posX, posY-1] != 0:
            if g[posX-1, posY-1] == 0 and g[posX+1, posY-1]==0 :
                trans[posX, posY-1] = 1
            else:
                if g[posX-1, posY-1] == 0:
                    trans[posX, posY-1] = (1 + probaTransition)/2
                    trans[posX+1, posY-1] = (1 - probaTransition)/2
                else:
                    if g[posX+1, posY-1] == 0:
                        trans[posX, posY-1] = (1 + probaTransition)/2
                        trans[posX-1, posY-1] = (1 - probaTransition)/2
                    else:
                        trans[posX, posY-1] = probaTransition
                        trans[posX+1, posY-1] = (1 - probaTransition)/2
                        trans[posX-1, posY-1] = (1 - probaTransition)/2
    if direction == DROITE and posY != nbcolonnes-1:
        if g[posX, posY+1] != 0:
            if g[posX-1, posY+1] == 0 and g[posX+1, posY+1]==0 :
                trans[posX, posY+1] = 1
            else:
                if g[posX-1, posY+1] == 0:
                    trans[posX, posY+1] = (1 + probaTransition)/2
                    trans[posX+1, posY+1] = (1 - probaTransition)/2
                else:
                    if g[posX+1, posY+1] == 0:
                        trans[posX, posY+1] = (1 + probaTransition)/2
                        trans[posX-1, posY+1] = (1 - probaTransition)/2
                    else:
                        trans[posX, posY+1] = probaTransition
                        trans[posX+1, posY+1] = (1 - probaTransition)/2
                        trans[posX-1, posY+1] = (1 - probaTransition)/2
    return trans

def programmeprimal(grille, gamma):
    #Matrice des contraintes + second membre
    A = np.zeros((nblignes*nbcolonnes, nblignes*nbcolonnes*4))
    b = np.zeros(nblignes*nbcolonnes*4)
    for i in range(nblignes):
        for j in range(nbcolonnes):
            for k in range (4):
                b[(i*nbcolonnes+j)*4+k]=grille[i][j]
                #Valeur de la case d'arrivée
                if (i == (nblignes - 1) and j == (nbcolonnes -1)):
                    #A changer si on veut maximiser
                    b[(i*nbcolonnes+j)*4+k]=-1000
                A[i*nbcolonnes+j][(i*nbcolonnes+j)*4+k]=1
                trans = transition(grille, k, j, i)
                for t in trans:
                    A[t[1]*nbcolonnes+t[0]][(i*nbcolonnes+j)*4+k]=gamma*trans[t]

    #fonction objectif
    obj = np.zeros(nblignes*nbcolonnes)
    obj[0] = 1

    return (A, b, obj)

def resolutionGurobiprimal(a,b,objectif):
    m = Model("PDM")     
        
    # declaration variables de decision
    v = []
    for i in range(nblignes*nbcolonnes):
        v.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="v%d" % (i+1)))
    
    # maj du modele pour integrer les nouvelles variables
    m.update()

    obj = LinExpr();
    obj =0
    for i in range(len(objectif)):
        obj += objectif[i]*v[i]

    # definition de l'objectif
    m.setObjective(obj,GRB.MAXIMIZE)

    # definition des contraintes
    for i in range(nblignes*nbcolonnes*4):
        m.addConstr(quicksum(a[i][j]*v[j] for j in nblignes*nbcolonnes) <= b[i], "Contrainte%d" % i)

    # Resolution
    m.optimize()

    return v
    
def politique(valeurs,grille):
    pol = np.zeros((nblignes, nbcolonnes))
    for i in range (nblignes):
        for j in range (nbcolonnes):
            minimum = 100000
            for k in range (4):
                temp= grille[j][i] + gamma * transition(grille, k, i,j)*valeurs[i*nblignes+j]
                if ( minimum > temp ):
                    minimum= temp
                    pol[i][j]= k
    return pol

""" GRAPHIQUE
#Creation de la fenetre
Mafenetre = Tk()
Mafenetre.title('MDP')

# ecriture du quadrillage et coloration
Canevas = Canvas(Mafenetre, width = Largeur, height =Hauteur, bg =mywhite)
for i in range(nblignes+1):
    ni=zoom*20*i+20
    Canevas.create_line(20, ni, Largeur-20,ni)
for j in range(nbcolonnes+1):
    nj=zoom*20*j+20
    Canevas.create_line(nj, 20, nj, Hauteur-20)
colordraw(g,nblignes,nbcolonnes)

 
Canevas.focus_set()
Canevas.bind('<Key>',Clavier)
Canevas.pack(padx =5, pady =5)

PosX = 20+10*zoom
PosY = 20+10*zoom

# Creation d'un widget Button (bouton Quitter)
Button(Mafenetre, text ='Restart', command = initialize).pack(side=LEFT,padx=5,pady=5)
Button(Mafenetre, text ='Quit', command = Mafenetre.destroy).pack(side=LEFT,padx=5,pady=5)

w = Label(Mafenetre, text='Cost = '+str(cost[0]),fg=myblack,font = "Verdana 14 bold")
w.pack() 

Pion = Canevas.create_oval(PosX-10,PosY-10,PosX+10,PosY+10,width=2,outline='black',fill=myyellow)

initialize()



Mafenetre.mainloop()
"""

