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

################################################################################
#
#                        VARIABLES ET CONSTANTES GLOBALES
#
################################################################################

zoom=4

#Loi de probabilité du coût d'une case
pblanc=0.15
pverte=0.35
pbleue=0.25
prouge=0.15
pnoire=0.10

#taille de la grille
nblignes=3
nbcolonnes=3

#Probabilité d'aller effectivement dans la direction voulue
probaTransition=0.8

#Visibilité du futur
gamma = 0.8

#poition initiale du robot dans la grille
posX=0
posY=0

#Position initiale du robot dans le dessin
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

################################################################################
#
#                           FONCTIONS DE DEFINITION DU PROBLEME
#
################################################################################

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
    
    #A REMPLACER PAR UNE FONCTION DE TEST D'INTEGRITE DU LABYRINTHE
    g[0,0]=np.random.random_integers(3)
    g[0,1]=np.random.random_integers(3)
    g[2,0]=np.random.random_integers(3)     
    g[nblignes-1,nbcolonnes-1]=np.random.random_integers(3)
    g[nblignes-2,nbcolonnes-1]=np.random.random_integers(3)
    g[nblignes-1,nbcolonnes-2]=np.random.random_integers(3)

    #Case but
    g[nblignes-1][nbcolonnes-1]=-1000
    
    return g


#Calcule la loi de probabilité de transition pour une action direction et une position (i, j) données.
#Retourne trans, la loi de probabilité sous la forme d'un dictionnaire
#Note : si une position n'appartient pas au dictionnaire, alors la probabilité d'aller dans cette position est nulle.
def transition(g, direction, i, j):
    trans = {}
    if g[i,j] != 0:
        if direction == GAUCHE and j > 0:
            if g[i, j-1] != 0:
                if (i-1 < 0 or g[i-1, j-1] == 0) and (i+1 > nblignes-1 or g[i+1, j-1]==0)  :
                    trans[i, j-1] = 1
                else:
                    if i-1 < 0 or g[i-1,j-1] == 0:
                        trans[i, j-1] = (1 + probaTransition)/2
                        trans[i+1, j-1] = (1 - probaTransition)/2
                    else:
                        if i+1 > nblignes-1 or g[i+1,j-1] == 0:
                            trans[i, j-1] = (1 + probaTransition)/2
                            trans[i-1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i, j-1] = probaTransition
                            trans[i-1, j-1] = (1 - probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
        if direction == DROITE and j < nbcolonnes-1:
            if g[i, j+1] != 0:
                if (i-1 < 0 or g[i-1, j+1] == 0) and (i+1 > nblignes-1 or g[i+1, j+1]==0):
                    trans[i, j+1] = 1
                else:
                    if i-1 < 0 or g[i-1,j+1] == 0:
                        trans[i, j+1] = (1 + probaTransition)/2
                        trans[i+1, j+1] = (1 - probaTransition)/2
                    else:
                        if i+1 > nblignes-1 or g[i+1,j+1] == 0:
                            trans[i, j+1] = (1 + probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
                        else:
                            trans[i, j+1] = probaTransition
                            trans[i+1, j+1] = (1 - probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
        if direction == HAUT and i > 0: 
            if g[i-1, j] != 0:
                if (j-1 < 0 or g[i-1, j-1] == 0) and (j+1 > nbcolonnes-1 or g[i-1, j+1] == 0):
                    trans[i-1, j] = 1
                else:
                    if j-1 < 0 or g[i-1, j-1] == 0:
                        trans[i-1, j] = (1 + probaTransition)/2
                        trans[i-1, j+1] = (1 - probaTransition)/2
                    else:
                        if j+1 > nbcolonnes-1 or g[i-1, j+1] == 0:
                            trans[i-1, j] = (1 + probaTransition)/2
                            trans[i-1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i-1, j] = probaTransition
                            trans[i-1, j-1] = (1 - probaTransition)/2
                            trans[i-1, j+1] = (1 - probaTransition)/2
        if direction == BAS and i < nblignes-1:
            if g[i+1, j] != 0:
                if (j-1 < 0 or g[i+1, j-1] == 0) and (j+1 > nbcolonnes-1 or g[i+1, j+1] == 0)  :
                    trans[i+1, j] = 1
                else:
                    if j-1 < 0 or g[i+1, j-1] == 0:
                        trans[i+1, j] = (1 + probaTransition)/2
                        trans[i+1, j+1] = (1 - probaTransition)/2
                    else:
                        if j+1 > nbcolonnes-1 or g[i+1, j+1] == 0:
                            trans[i+1, j] = (1 + probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
                        else:
                            trans[i+1, j] = probaTransition
                            trans[i+1, j+1] = (1 - probaTransition)/2
                            trans[i+1, j-1] = (1 - probaTransition)/2
    return trans



################################################################################
#
#                            FONCTIONS GRAPHIQUES
#
################################################################################

def initialize():
    global cost
# position initiale du robot
    
    for k in range(5):
        cost[k]=0
# cout et affichage
    Canevas.coords(Pion,PosX -9*zoom, PosY -9*zoom, PosX +9*zoom, PosY +9*zoom)
    w.config(text='Cost = '+ str(cost[0]))


# dessine la grille avec des ovales
def colordraw(g,nblignes,nbcolonnes):
    for i in range(nblignes):
        for j in range(nbcolonnes):          
            y =zoom*20*j+20
            x =zoom*20*i+20
            if i == 0 and j == 0 :
                Canevas.create_text(x+zoom*10,y+zoom*10,text="DEPART",fill=myblack,font = "Verdana 12 bold")
            else:
                if i == nblignes -1 and j == nbcolonnes -1 :
                    Canevas.create_text(x+zoom*10,y+zoom*10,text="BUT",fill=myblack,font = "Verdana 12 bold")
                else:
                    if g[i,j]==0: 
                        Canevas.create_rectangle(x, y, x+zoom*20, y+zoom*20, fill=myblack)
                    else:
                        Canevas.create_oval(x+zoom*(10-3),y+zoom*(10-3),x+zoom*(10+3),y+zoom*(10+3),width=1,outline=color[g[i,j]],fill=color[g[i,j]])
                   
                        


           
#Place des valeurs coloré dans le labyrinte                    
def colordraw2(g,nblignes,nbcolonnes):
    #Place les valeurs coloré dans le labyrinthe    
    for i in range(nblignes):
        for j in range(nbcolonnes):          
            y =zoom*20*i+20
            x =zoom*20*j+20
            if g[i,j,0]>0: 
                Canevas.create_text(x+zoom*(10),y+zoom*(10),font="1",text =g[i,j],fill=color[g[i,j,0]])
            else:
                Canevas.create_rectangle(x, y, x+zoom*20, y+zoom*20, fill=myblack)


def Clavier (event):
    global PosX,PosY,posX,posY,cost,g
    touche = event.keysym
    i = posX
    j= posY
    value = 0
    z=np.random.uniform(0,1)
    if touche == 'space':
        if (j+i)%2==0:
            touche = 'm'
        else:
             touche ='q'
    if touche =="a" and i>0 and g[i-1,j]!=0:
        print 'haut'
        trans= transition (g,HAUT,i,j)
        for t in trans:
            value += trans[t]
            if(value > z):
                i=t[0]
                j=t[1]
                cost[g[i,j]] +=1
                break
    if touche =="q" and i< nblignes and g[i+1,j]!=0:
        print 'haut'
        trans= transition (g,BAS,i,j)
        for t in trans:
            value += trans[t]
            if(value > z):
                i=t[0]
                j=t[1]
                cost[g[i,j]] +=1
                break
    if touche =="l" and j>0 and g[i,j-1]!=0:
        print 'gauche'
        trans= transition (g,GAUCHE,i,j)
        for t in trans:
            value += trans[t]
            if(value > z):
                i=t[0]
                j=t[1]
                cost[g[i,j]] +=1
                break
    if touche =="m" and j< nbcolonnes and g[i,j+1]!=0:
        print 'droit'
        trans= transition (g,DROITE,i,j)
        for t in trans:
            value += trans[t]
            if(value > z):
                i=t[0]
                j=t[1]
                if (g[i,j]>0):
                    cost[g[i,j]] +=1
                break
    print 'j='+str(j)+'  i='+str(i)
    PosY = j *20*zoom +20+zoom*10
    PosX = i *20*zoom +20+zoom*10
    posY = j
    posX = i
    print 'PosX=' +str(PosX) + 'PosY=' +str(PosY)
    Canevas.coords(Pion,PosY -9*zoom, PosX -9*zoom, PosY +9*zoom, PosX +9*zoom)
    cost[0]=0    
    for k in range(4):
        cost[0]+=cost[k+1]*weight[k+1]
    w.config(text='Cost = '+ str(cost[0]))
                    
        
        
                



#Sert a bouger le pion dans l'interface
def Clavier2(event):
    global PosX,PosY,posX,posY,cost,g
    touche = event.keysym
#    cj=(PosX-30)/(20*zoom)
#    li=(PosY-30)/(20*zoom)
    cj = posX
    li = posY
    value = 0 ;
    z=np.random.uniform(0,1)
    print 'z=' +str(z)
    #print(li,cj)
    # deplacement vers le haut
    if touche == 'space':
        Canevas.coords(Pion,30 -9*zoom, 30 -9*zoom, 30 +9*zoom, 30 +9*zoom)
        return
    if touche == 'a' and li>0 and g[li-1,cj]>0:
        print  'gauche'        

        trans = transition (g,HAUT,li,cj)
        print trans
        for t in trans:
            value += trans[t]
            
            print 'trans='+ str(trans[t])
            if  value < z:
                cj= t[0]
                li= t[1]                                    
        cost[g[li,cj]] +=1
       # PosY -= zoom*20
        #cost[g[li-1,cj]]+=1        
    # deplacement vers le bas
    if touche == 'm' and li<nblignes-1 and g[li+1,cj]>0:
        
        z=np.random.uniform(0,1)
        trans = transition (g,BAS,li,cj)
        print trans        
        for t in trans:
            value += trans[t]
            print 'value=' + str(value)
            print  'droit (' +str(cj)+ ' '+  str(li   )+')'+'(' +str(t[0])+ ' '+  str(t[1])+')'
            if   z< value:
                print 'its alive !'
                cj= t[0]
                li= t[1]
        cost[g[li,cj]] +=1
        #PosY += zoom*20
        #cost[g[li+1,cj]]+=1
    # deplacement vers la droite
    if touche == 'q' and cj< nbcolonnes-1 and g[li,cj+1]>0:
        print  'bas'
        z=np.random.uniform(0,1)
        trans = transition (g,DROITE,li,cj)
        print trans        
        for t in trans:
            value += trans[t]
            if  value > z:
                cj= t[0]
                li= t[1]
        cost[g[li,cj]] +=1
        #PosX += zoom*20
        #cost[g[li,cj+1]]+=1
    # deplacement vers la gauche
    if touche == 'a' and cj >0 and g[li,cj-1]>0:
        print  'haut'
        z=np.random.uniform(0,1)
        trans = transition (g,GAUCHE,li,cj)
        print trans
        for t in trans:
            value += trans[t]
            if  value > z:
                cj= t[0]
                li= t[1]
        cost[g[li,cj]] +=1
       # PosX -= zoom*20
        #cost[g[li,cj-1]]+=1
    # on dessine le pion a sa nouvelle position
    print 'cj='+str(cj)+'  li='+str(li)
    PosX = cj *20*zoom +20+zoom*(10)
    PosY = li *20*zoom +20+zoom*(10)
    posX= cj
    posY = li
    print 'PosX=' +str(PosX) + 'PosY=' +str(PosY)
    Canevas.coords(Pion,PosX -9*zoom, PosY -9*zoom, PosX +9*zoom, PosY +9*zoom)
    cost[0]=0    
    for k in range(4):
        cost[0]+=cost[k+1]*weight[k+1]
    w.config(text='Cost = '+ str(cost[0]))


def Clavier3(event):
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
        cost[1]+=g[li-1,cj]        
    # deplacement vers le bas
    if touche == 'q' and li<nblignes-1 and g[li+1,cj]>0:
        PosY += zoom*20
        cost[1]+=g[li+1,cj] 
    # deplacement vers la droite
    if touche == 'm' and cj< nbcolonnes-1 and g[li,cj+1]>0:
        PosX += zoom*20        
        cost[1]+=g[li,cj+1] 
    # deplacement vers la gauche
    if touche == 'l' and cj >0 and g[li,cj-1]>0:
        PosX -= zoom*20
        cost[1]+=g[li,cj-1] 
    # on dessine le pion a sa nouvelle position
    Canevas.coords(Pion,PosX -9*zoom, PosY -9*zoom, PosX +9*zoom, PosY +9*zoom)
    cost[0]=0    
    for k in range(4):
        cost[0]+=cost[k+1]*weight[k+1]
    w.config(text='Cost = '+ str(cost[0]))
#    w1.config(text='vert = '+ str(cost[1]))
#    w2.config(text='bleu = '+ str(cost[2]))
#    w3.config(text='rouge = '+ str(cost[3]))
#    w4.config(text='noir = '+ str(cost[4]))
#      

################################################################################
#
#                            FONCTIONS DE RESOLUTION (INTERFACE GUROBI)
#
################################################################################


def programmeprimal(grille, gamma):
    #Matrice des contraintes + second membre
    A = np.zeros((nblignes*nbcolonnes*4, nblignes*nbcolonnes))
    b = np.zeros(nblignes*nbcolonnes*4)
    for i in range(nblignes):
        for j in range(nbcolonnes):
            for k in range (4):
                b[(i*nbcolonnes+j)*4+k]=grille[i][j]
                #Valeur de la case d'arrivée
                if (i == (nblignes - 1) and j == (nbcolonnes -1)):
                    #A changer si on veut maximiser
                    b[(i*nbcolonnes+j)*4+k]=-1000
                A[(i*nbcolonnes+j)*4+k][i*nbcolonnes+j]=1
                trans = transition(grille, k, j, i)
                for t in trans:
                    A[(i*nbcolonnes+j)*4+k][t[0]*nbcolonnes+t[1]]=-gamma*trans[t]

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
    print 
    for i in range(nblignes*nbcolonnes*4):
        m.addConstr(quicksum(a[i][j]*v[j] for j in range(nblignes*nbcolonnes)) <= b[i], "Contrainte%d" % i)

    # Resolution
    m.optimize()

    return v

#A revoir quand la résolution du PL marcheras
def politique(valeurs,grille):
    pol = np.zeros((nblignes, nbcolonnes))
    for i in range (nblignes):
        for j in range (nbcolonnes):
            minimum = 100000
            for k in range (4):
                temp = grille[j][i]
                trans = transition(grille, k, i, j)
                for t in trans:
                    temp += gamma * trans[t] * valeurs[t[0]*nblignes+t[1]]
                if ( minimum > temp ):
                    minimum= temp
                    pol[i][j]= k
    return pol



################################################################################
#
#                            PROGRAMME PRINCIPAL
#
################################################################################


# GRAPHIQUE
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
g = defineMaze(nblignes, nbcolonnes)
colordraw(g,nblignes,nbcolonnes)

 
Canevas.focus_set()
Canevas.bind('<Key>',Clavier)
Canevas.pack(padx =5, pady =5)



# Creation d'un widget Button (bouton Quitter)
Button(Mafenetre, text ='Restart', command = initialize).pack(side=LEFT,padx=5,pady=5)
Button(Mafenetre, text ='Quit', command = Mafenetre.destroy).pack(side=LEFT,padx=5,pady=5)

w = Label(Mafenetre, text='Cost = '+str(cost[0]),fg=myblack,font = "Verdana 14 bold")
w.pack() 

Pion = Canevas.create_oval(PosX-10,PosY-10,PosX+10,PosY+10,width=2,outline='black',fill=myyellow)

initialize()



Mafenetre.mainloop()

"""


##g = defineMaze(10,10)
##print g
g = np.ones((nblignes,nbcolonnes), dtype=np.int)
g[0,1] = 4
g[0,2] = 4
g[2,0] = 4
g[2,1] = 4
#print g
(A, b, obj) = programmeprimal(g, gamma)
##print A
##print b
##print obj
v = resolutionGurobiprimal(A, b, obj)
#print v
#pol = politique(v, g)
#print pol
"""
