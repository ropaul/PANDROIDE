# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 15:52:20 2015

@author: Yann Ropaul & Margot Calbrix
"""

#from modele_1critere import *
from modele_multicritere import *
from minmax_multicritere import *
from Tkinter import *
from gurobipy import *
import random
import numpy as np
import math
import SommePondere_multicritere
import RegretPondere



################################################################################
#
#                        VARIABLES ET CONSTANTES GLOBALES
#
################################################################################

zoom=4

#Position initiale du robot dans le dessin
PosX = 20+10*zoom 
PosY = 20+10*zoom

Pion = ""

saveLine=[]
alpha=[]
poidcritere = []

# def des couleurs
myred="#D20B18"
mygreen="#25A531"
myblue="#0B79F7"
mygrey="#E8E8EB"
myyellow="#F9FB70"
myblack="#2D2B2B"
mywalls="#5E5E64"
mywhite="#FFFFFF"
mygold="#FFD700"
mypurple="#C722E1"
myazur="#A3F7F2"
mygrey="#C0C0C0"
mymaroon="#800000"

color=[mywhite,mygreen,myblue,myred,myblack,mygold,mypurple,myazur,mygrey,mymaroon]
colorname= ["mywhite","green","blue","red","black","gold","purple","azur","grey","maroon"]


################################################################################
#
#                               INITIALISATION
#
################################################################################



def initialize():
    global cost,posX,posY,PosX,PosY
    # cout et affichage
    '''
    for k in range(5):
        cost[k]=0
    '''
    # position initiale du robot
    i=0
    j=0
    PosY = j *20*zoom +20+zoom*10
    PosX = i *20*zoom +20+zoom*10
    posY = j
    posX = i
    Canevas.coords(Pion,PosX -9*zoom, PosY -9*zoom, PosX +9*zoom, PosY +9*zoom)
    '''
    w.config(text='Cost = '+ str(cost[0]))
    w1.config(text='vert = '+ str(cost[1]))
    w2.config(text='bleu = '+ str(cost[2]))
    w3.config(text='rouge = '+ str(cost[3]))
    w4.config(text='noir = '+ str(cost[4]))
    '''
    cost[0]=0
    w.config(text='Cost = '+ str(cost[0]))
    for i in range (nbcriteres):
        cost[i+1]=0
        labels[i].config(text= colorname[i+1]+'='+str(cost[i+1])+' | ')

#Sert a la premiere initialisation du labyrinthe. verifie si tous les choix demandé sont fait
def choix():
    global gamma, probaTransition,nblignes, nbcolonnes,zoom,nbcriteres
#    if ((liste.get() != "1" and liste.get() != "2"and liste.get() != "3")):
#        
#        champ_erreur = Label(init, text="Erreur sur les entrer")
#        champ_erreur.pack()      
#        return
    if ( nb.get() != '' ):
        valueL= (nb.get())
    if ( nbprime.get() != '' ):
        valueC= (nbprime.get())        
            
        nblignes = valueL
        nbcolonnes = valueC
        
        valueCritere=(critere.get())
        nbcriteres=    valueCritere
        
        val = max(valueC,valueL)
        
        if val >0:# and valueCL < 5:
            zoom = 4
        if val >10 :#and valueCL < 10:
            zoom = 3
        if val >=15:
            zoom = 2
        if val >=20:
            zoom = (val -10)/10         
    probaTransition= nb2.get()
    gamma = nb3.get()
    init.destroy()
    
def choixEvent(event):
    if event.keysym == 'Return':
        choix();

#initialise la fenetre d'initialisation
def initFenetre() :
    global nb,nbprime, nb2 , nb3,critere, init, liste
    #création fenetre choix
    
    init.title('Choix')
    
    champ_label = Label(init, text="Number of line")
    champ_label.pack()
    nb = IntVar()
    nb.set(3)
    # Création d'un widget Spinbox
    boite = Spinbox(init,from_=2,to=42,increment=1,textvariable=nb,width=5)
    boite.pack(padx=30,pady=10)
    
    champ_labelprime = Label(init, text="Number of column ")
    champ_labelprime.pack()
    nbprime = IntVar()
    nbprime.set(3)
    # Création d'un widget Spinbox
    boiteprime = Spinbox(init,from_=2,to=42,increment=1,textvariable=nbprime,width=5)
    boiteprime.pack(padx=30,pady=10)


    champ_labelcritere = Label(init, text="number of criterion")
    champ_labelcritere.pack()
    critere = IntVar()
    critere.set(4)
    # Création d'un widget Spinbox
    boitecritere = Spinbox(init,from_=1,to=9,increment=1,textvariable=critere,width=5)
    boitecritere.pack(padx=30,pady=10)        
    
    champ_label2 = Label(init, text="transition probability")
    champ_label2.pack()
    nb2 = DoubleVar()
    nb2.set(0.8)
    # Création d'un widget Spinbox
    boite2 = Spinbox(init,from_=0,to=1,increment=0.05,textvariable=nb2,width=5)
    boite2.pack(padx=30,pady=10)    
    
    
    champ_label3 = Label(init, text="value of gamma")
    champ_label3.pack()
    nb3 =DoubleVar()
    nb3.set(0.8)
    # Création d'un widget Spinbox
    boite3 = Spinbox(init,from_=0,to=1,increment=0.05,textvariable=nb3,width=5)
    boite3.pack(padx=30,pady=10)   
    
    
    
    
    #liste de choix de labyrhinte possible et le bouton de changement de maze
    Button(init, text ='Create the Maze', command = choix).pack(side=LEFT,padx=5,pady=5)
    
    init.bind('<Key>',choixEvent)
    init.mainloop()
    
    
def politiquelancher():
    global liste

    if liste.get()=="1":
        return resolutionMultiSomme(g, gamma, probaTransition, nbcriteres, nblignes, nbcolonnes)
    if liste.get()=="2":
        return resolutionMultiMinMax(g, gamma, probaTransition, nbcriteres, nblignes, nbcolonnes)
    if liste.get()=="3":
        return resolutionMultiRegretMinMax2(g, gamma, probaTransition, nbcriteres, nblignes, nbcolonnes)
    if liste.get()=="4":
        return SommePondere_multicritere.resolutionMultiSommePondere(g,alpha, gamma, probaTransition, nbcriteres, nblignes, nbcolonnes)
    if liste.get()=="5":
        return RegretPondere.resolutionMultiRegretPondere2(alpha,g, gamma, probaTransition, nbcriteres, nblignes, nbcolonnes)
                        
        
            
    
def colordrawlancher(value):
    if value == 1:
        colordrawMulti1(g,nblignes,nbcolonnes)
        return
    if value == 2:
        colordrawMulti2(g,nblignes,nbcolonnes)
        return
    if value == 3:
        colordrawMulti3(g,nblignes,nbcolonnes)
        return
    if value == 4:
        colordrawMulti4(g,nblignes,nbcolonnes)
        return
    if value == 5:
        colordrawMulti5(g,nblignes,nbcolonnes)
        return
    if value == 6:
        colordrawMulti6(g,nblignes,nbcolonnes)
        return
    if value == 7:
        colordrawMulti7(g,nblignes,nbcolonnes)
        return
    if value == 8:
        colordrawMulti8(g,nblignes,nbcolonnes)
        return
    if value == 9:
        colordrawMulti9(g,nblignes,nbcolonnes)
        return
        


################################################################################
#
#                            AFFICHAGES COUT DES CIRTERES
#
################################################################################

# pour un nombre de critere : 9
#Place pour chaque couleur un cout différents choisit alétoirement. Ici le choix de la couleur ne sert que pour choisir si il y a mur ou pas. 
def colordrawMulti9(g,nblignes,nbcolonnes):    
    #Place les différents couts dans l'affichage 
    vzero = np.zeros(nbcriteres, dtype=np.int)
    for i in range(nblignes):
        for j in range(nbcolonnes):          
            y =zoom*20*i+20
            x =zoom*20*j+20
            
            if i == 0 and j == 0 :
                Canevas.create_text(x+zoom*10,y+zoom*10,text="DEPART",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
            else:
                if i == nblignes -1 and j == nbcolonnes -1 :
                    Canevas.create_text(x+zoom*10,y+zoom*10,text="BUT",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
                else:        
                    if np.array_equal(g[i,j], vzero)==False:
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10-5),font="1",text =g[i,j,0],fill=color[1])
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10+5),font="1",text =g[i,j,1],fill=color[2])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10-5),font="1",text =g[i,j,2],fill=color[3])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10+5),font="1",text =g[i,j,3],fill=color[4])
                        Canevas.create_text(x+zoom*(10),y+zoom*(10-5),font="1",text =g[i,j,4],fill=color[5])
                        Canevas.create_text(x+zoom*(10),y+zoom*(10+5),font="1",text =g[i,j,5],fill=color[6])
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10),font="1",text =g[i,j,6],fill=color[7])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10),font="1",text =g[i,j,7],fill=color[8])
                        Canevas.create_text(x+zoom*(10),y+zoom*(10),font="1",text =g[i,j,7],fill=color[9])
                    else:
                        Canevas.create_rectangle(x, y, x+zoom*20, y+zoom*20, fill=myblack)



# pour un nombre de critere : 8
#Place pour chaque couleur un cout différents choisit alétoirement. Ici le choix de la couleur ne sert que pour choisir si il y a mur ou pas. 
def colordrawMulti8(g,nblignes,nbcolonnes):    
    #Place les différents couts dans l'affichage 
    vzero = np.zeros(nbcriteres, dtype=np.int)
    for i in range(nblignes):
        for j in range(nbcolonnes):          
            y =zoom*20*i+20
            x =zoom*20*j+20
            
            if i == 0 and j == 0 :
                Canevas.create_text(x+zoom*10,y+zoom*10,text="DEPART",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
            else:
                if i == nblignes -1 and j == nbcolonnes -1 :
                    Canevas.create_text(x+zoom*10,y+zoom*10,text="BUT",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
                else:        
                    if np.array_equal(g[i,j], vzero)==False:
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10-5),font="1",text =g[i,j,0],fill=color[1])
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10+5),font="1",text =g[i,j,1],fill=color[2])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10-5),font="1",text =g[i,j,2],fill=color[3])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10+5),font="1",text =g[i,j,3],fill=color[4])
                        Canevas.create_text(x+zoom*(10),y+zoom*(10-5),font="1",text =g[i,j,4],fill=color[5])
                        Canevas.create_text(x+zoom*(10),y+zoom*(10+5),font="1",text =g[i,j,5],fill=color[6])
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10),font="1",text =g[i,j,6],fill=color[7])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10),font="1",text =g[i,j,7],fill=color[8])
                    else:
                        Canevas.create_rectangle(x, y, x+zoom*20, y+zoom*20, fill=myblack)
                        

# pour un nombre de critere : 7
#Place pour chaque couleur un cout différents choisit alétoirement. Ici le choix de la couleur ne sert que pour choisir si il y a mur ou pas. 
def colordrawMulti7(g,nblignes,nbcolonnes):    
    #Place les différents couts dans l'affichage 
    vzero = np.zeros(nbcriteres, dtype=np.int)
    for i in range(nblignes):
        for j in range(nbcolonnes):          
            y =zoom*20*i+20
            x =zoom*20*j+20
            
            if i == 0 and j == 0 :
                Canevas.create_text(x+zoom*10,y+zoom*10,text="DEPART",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
            else:
                if i == nblignes -1 and j == nbcolonnes -1 :
                    Canevas.create_text(x+zoom*10,y+zoom*10,text="BUT",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
                else:        
                    if np.array_equal(g[i,j], vzero)==False:
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10-5),font="1",text =g[i,j,0],fill=color[1])
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10+5),font="1",text =g[i,j,1],fill=color[2])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10-5),font="1",text =g[i,j,2],fill=color[3])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10+5),font="1",text =g[i,j,3],fill=color[4])
                        Canevas.create_text(x+zoom*(10),y+zoom*(10-5),font="1",text =g[i,j,4],fill=color[5])
                        Canevas.create_text(x+zoom*(10),y+zoom*(10+5),font="1",text =g[i,j,5],fill=color[6])
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10),font="1",text =g[i,j,6],fill=color[7])
                    else:
                        Canevas.create_rectangle(x, y, x+zoom*20, y+zoom*20, fill=myblack)


# pour un nombre de critere : 6
#Place pour chaque couleur un cout différents choisit alétoirement. Ici le choix de la couleur ne sert que pour choisir si il y a mur ou pas. 
def colordrawMulti6(g,nblignes,nbcolonnes):    
    #Place les différents couts dans l'affichage 
    vzero = np.zeros(nbcriteres, dtype=np.int)
    for i in range(nblignes):
        for j in range(nbcolonnes):          
            y =zoom*20*i+20
            x =zoom*20*j+20
            
            if i == 0 and j == 0 :
                Canevas.create_text(x+zoom*10,y+zoom*10,text="DEPART",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
            else:
                if i == nblignes -1 and j == nbcolonnes -1 :
                    Canevas.create_text(x+zoom*10,y+zoom*10,text="BUT",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
                else:        
                    if np.array_equal(g[i,j], vzero)==False:
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10-5),font="1",text =g[i,j,0],fill=color[1])
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10+5),font="1",text =g[i,j,1],fill=color[2])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10-5),font="1",text =g[i,j,2],fill=color[3])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10+5),font="1",text =g[i,j,3],fill=color[4])
                        Canevas.create_text(x+zoom*(10),y+zoom*(10-5),font="1",text =g[i,j,4],fill=color[5])
                        Canevas.create_text(x+zoom*(10),y+zoom*(10+5),font="1",text =g[i,j,5],fill=color[6])
                    else:
                        Canevas.create_rectangle(x, y, x+zoom*20, y+zoom*20, fill=myblack)
                        
                        

# pour un nombre de critere : 5
#Place pour chaque couleur un cout différents choisit alétoirement. Ici le choix de la couleur ne sert que pour choisir si il y a mur ou pas. 
def colordrawMulti5(g,nblignes,nbcolonnes):    
    #Place les différents couts dans l'affichage 
    vzero = np.zeros(nbcriteres, dtype=np.int)
    for i in range(nblignes):
        for j in range(nbcolonnes):          
            y =zoom*20*i+20
            x =zoom*20*j+20
            
            if i == 0 and j == 0 :
                Canevas.create_text(x+zoom*10,y+zoom*10,text="DEPART",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
            else:
                if i == nblignes -1 and j == nbcolonnes -1 :
                    Canevas.create_text(x+zoom*10,y+zoom*10,text="BUT",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
                else:        
                    if np.array_equal(g[i,j], vzero)==False:
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10-5),font="1",text =g[i,j,0],fill=color[1])
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10+5),font="1",text =g[i,j,1],fill=color[2])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10-5),font="1",text =g[i,j,2],fill=color[3])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10+5),font="1",text =g[i,j,3],fill=color[4])
                        Canevas.create_text(x+zoom*(10),y+zoom*(10-5),font="1",text =g[i,j,4],fill=color[5])
                    else:
                        Canevas.create_rectangle(x, y, x+zoom*20, y+zoom*20, fill=myblack)


# pour un nombre de critere : 4
#Place pour chaque couleur un cout différents choisit alétoirement. Ici le choix de la couleur ne sert que pour choisir si il y a mur ou pas. 
def colordrawMulti4(g,nblignes,nbcolonnes):    
    #Place les différents couts dans l'affichage 
    vzero = np.zeros(nbcriteres, dtype=np.int)
    for i in range(nblignes):
        for j in range(nbcolonnes):          
            y =zoom*20*i+20
            x =zoom*20*j+20
            
            if i == 0 and j == 0 :
                Canevas.create_text(x+zoom*10,y+zoom*10,text="DEPART",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
            else:
                if i == nblignes -1 and j == nbcolonnes -1 :
                    Canevas.create_text(x+zoom*10,y+zoom*10,text="BUT",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
                else:        
                    if np.array_equal(g[i,j], vzero)==False:
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10-5),font="1",text =g[i,j,0],fill=color[1])
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10+5),font="1",text =g[i,j,1],fill=color[2])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10-5),font="1",text =g[i,j,2],fill=color[3])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10+5),font="1",text =g[i,j,3],fill=color[4])
                    else:
                        Canevas.create_rectangle(x, y, x+zoom*20, y+zoom*20, fill=myblack)




# pour un nombre de critere : 3
#Place pour chaque couleur un cout différents choisit alétoirement. Ici le choix de la couleur ne sert que pour choisir si il y a mur ou pas. 
def colordrawMulti3(g,nblignes,nbcolonnes):    
    #Place les différents couts dans l'affichage 
    vzero = np.zeros(nbcriteres, dtype=np.int)
    for i in range(nblignes):
        for j in range(nbcolonnes):          
            y =zoom*20*i+20
            x =zoom*20*j+20
            
            if i == 0 and j == 0 :
                Canevas.create_text(x+zoom*10,y+zoom*10,text="DEPART",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
            else:
                if i == nblignes -1 and j == nbcolonnes -1 :
                    Canevas.create_text(x+zoom*10,y+zoom*10,text="BUT",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
                else:        
                    if np.array_equal(g[i,j], vzero)==False:
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10+5),font="1",text =g[i,j,0],fill=color[1])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10+5),font="1",text =g[i,j,1],fill=color[2])
                        Canevas.create_text(x+zoom*(10),y+zoom*(10-5),font="1",text =g[i,j,2],fill=color[3])
                    else:
                        Canevas.create_rectangle(x, y, x+zoom*20, y+zoom*20, fill=myblack)



# pour un nombre de critere : 2
#Place pour chaque couleur un cout différents choisit alétoirement. Ici le choix de la couleur ne sert que pour choisir si il y a mur ou pas. 
def colordrawMulti2(g,nblignes,nbcolonnes):    
    #Place les différents couts dans l'affichage 
    vzero = np.zeros(nbcriteres, dtype=np.int)
    for i in range(nblignes):
        for j in range(nbcolonnes):          
            y =zoom*20*i+20
            x =zoom*20*j+20
            
            if i == 0 and j == 0 :
                Canevas.create_text(x+zoom*10,y+zoom*10,text="DEPART",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
            else:
                if i == nblignes -1 and j == nbcolonnes -1 :
                    Canevas.create_text(x+zoom*10,y+zoom*10,text="BUT",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
                else:        
                    if np.array_equal(g[i,j], vzero)==False:
                        Canevas.create_text(x+zoom*(10-5),y+zoom*(10),font="1",text =g[i,j,0],fill=color[1])
                        Canevas.create_text(x+zoom*(10+5),y+zoom*(10),font="1",text =g[i,j,1],fill=color[2])
                    else:
                        Canevas.create_rectangle(x, y, x+zoom*20, y+zoom*20, fill=myblack)


# pour un nombre de critere : 1
#Place pour chaque couleur un cout différents choisit alétoirement. Ici le choix de la couleur ne sert que pour choisir si il y a mur ou pas. 
def colordrawMulti1(g,nblignes,nbcolonnes):    
    #Place les différents couts dans l'affichage 
    vzero = np.zeros(nbcriteres, dtype=np.int)
    for i in range(nblignes):
        for j in range(nbcolonnes):          
            y =zoom*20*i+20
            x =zoom*20*j+20
            
            if i == 0 and j == 0 :
                Canevas.create_text(x+zoom*10,y+zoom*10,text="DEPART",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
            else:
                if i == nblignes -1 and j == nbcolonnes -1 :
                    Canevas.create_text(x+zoom*10,y+zoom*10,text="BUT",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
                else:        
                    if np.array_equal(g[i,j], vzero)==False:
                        Canevas.create_text(x+zoom*(10),y+zoom*(10),font="1",text =g[i,j,0],fill=color[1])
                    else:
                        Canevas.create_rectangle(x, y, x+zoom*20, y+zoom*20, fill=myblack)





################################################################################
#
#                            GESTION DEPLACEMENT
#
################################################################################


#fonction servant a manipuler le pion dans la labirhynte
def Clavier (event):
    global PosX,PosY,posX,posY,cost,g,politique, Pion
    vzero = np.zeros(nbcriteres, dtype=np.int)
    touche = event.keysym
    i = posX
    j= posY
    value = 0
    z=np.random.uniform(0,1)
    if touche == 'space':
#        if (j+i)%2==0:
#            touche = 'm'
#        else:
#             touche ='q'
        touche = marcheAutoMixte(i,j,politique)
    if (touche =="a"or touche== "Up") and i>0 :
        if np.array_equal(g[i-1,j], vzero)==False:
            print 'haut'
            trans= transition (g,HAUT,i,j,probaTransition,nbcriteres)
            for t in trans:
                value += trans[t]
                if(value > z):
                    i=t[0]
                    j=t[1]
                    if (i!= nblignes-1 or j != nbcolonnes -1):
                        for k in range (nbcriteres) :
                            cost[k+1] += g[i,j,k]
                    break
    if (touche =="q" or touche=="Down") and i< nblignes -1:
        if np.array_equal(g[i+1,j], vzero)==False :
            print 'bas'
            trans= transition (g,BAS,i,j,probaTransition,nbcriteres)
            for t in trans:
                value += trans[t]
                if(value > z):
                    i=t[0]
                    j=t[1]
                    if (i!= nblignes-1 or j != nbcolonnes -1):
                        for k in range (nbcriteres) :
                            cost[k+1] += g[i,j,k]
                    break
    if (touche =="l" or touche=="Left") and j>0:
        if  np.array_equal(g[i,j-1], vzero)==False :
            print 'gauche'
            trans= transition (g,GAUCHE,i,j,probaTransition,nbcriteres)
            for t in trans:
                value += trans[t]
                if(value > z):
                    i=t[0]
                    j=t[1]
                    if (i!= nblignes-1 or j != nbcolonnes -1):
                        for k in range (nbcriteres) :
                            cost[k+1] += g[i,j,k]
                    break
    if (touche =="m" or touche== "Right") and j< nbcolonnes-1 :
        if np.array_equal(g[i,j+1], vzero)==False:
            print 'droit'
            trans= transition (g,DROITE,i,j,probaTransition,nbcriteres)
            for t in trans:
                value += trans[t]
                if(value > z):
                    i=t[0]
                    j=t[1]
                    if (i!= nblignes-1 or j != nbcolonnes -1):
                        for k in range (nbcriteres) :
                            cost[k+1] += g[i,j,k]
                    break
#    print 'j='+str(j)+'  i='+str(i)
    PosY = j *20*zoom +20+zoom*10
    PosX = i *20*zoom +20+zoom*10
    posY = j
    posX = i
#    print 'PosX=' +str(PosX) + 'PosY=' +str(PosY)
    Canevas.coords(Pion,PosY -9*zoom, PosX -9*zoom, PosY +9*zoom, PosX +9*zoom)
    cost[0]=0  
    '''
    for k in range(4):
        cost[0]+=cost[k+1]*weight[k+1]
    w.config(text='Cost = '+ str(cost[0]))
    w1.config(text='vert = '+ str(cost[1]))
    w2.config(text='bleu = '+ str(cost[2]))
    w3.config(text='rouge = '+ str(cost[3]))
    w4.config(text='noir = '+ str(cost[4])) 
    '''
    for k in range(nbcriteres ):
        cost[0]+=cost[k+1]
        w.config(text='Cost = '+ str(cost[0]))
        labels[k].config(text= colorname[k+1]+'='+str(cost[k+1])+' | ')
        
    #pour qu'on puisse restart avec le bacspace
    if touche == 'BackSpace':
        initialize()
    #pour qu'on quite le programme en appuyant sur esc
    if touche == 'Esc':
        Fenetre.destroy()
        

################################################################################
#
#                            MARCHE AUTOMATIQUE
#
################################################################################
        
#fonction qui donne la direction lorsque l'on appuie sur espace                    
def marcheAuto(i,j,pol):
    if (i == nblignes-1 and  j == nbcolonnes-1) :
        return " "
    if pol[i,j] == HAUT:
        return "a"
    if pol[i,j] == BAS:
        return "q"
    if pol[i,j] == GAUCHE:
        return "l"
    if pol[i,j] == DROITE:
        return "m"


#donne la valeur de la touche pour l'indice associer (existe que pour marcheAutoMixte)
def touchevalue (i,j,value):
    if (i == nblignes-1 and  j == nbcolonnes-1) :
        return " "
    if value == HAUT:        
        return "a"
    if value == BAS:        
        return "q"
    if value == GAUCHE:        
        return "l"
    if value == DROITE:       
        return "m"

    
    
  
        
#fonction qui donne la direction lorsque l'on appuie sur espace (marche avec les politiques mixtes)                 
def marcheAutoMixte(i,j,pol):
    z=np.random.uniform(0,1)
    value = 0;
    for k in range(4):
        value += pol[i,j,k] 
        if (z < value):
            return touchevalue(i,j,k)
    return " "
    
    
#prend la grille multicritere (mais avec solution pure) et la transforme en une grille solution monocritere
def createGrilleSoluce(resultPL):
    grille = np.zeros((resultPL.shape[0],resultPL.shape[1]))
    for i in range (resultPL.shape[0]):
        for j in range (resultPL.shape[1]):
            for k in range(resultPL.shape[2]):
                if resultPL[i][j][k] == 1:
                    grille[i][j]= k
    return grille
    
    

################################################################################
#
#                            AFFICHAGE SOLUTIONS
#
################################################################################

    
    
       
# fonction servant a afficher la solution  donné par le PDM monocritere        
def afficheSolution(grille):
    vzero = np.zeros(nbcriteres, dtype=np.int)
    for i in range (nblignes):
        for j in range (nbcolonnes):
            if (i != nblignes-1 or  j != nbcolonnes-1) and np.array_equal(g[i,j], vzero)==False:
                if grille[i,j] == HAUT:
                    PosY = j *20*zoom +20+zoom*10
                    PosX = i *20*zoom +20+zoom*10
                    Canevas.create_line(PosY,PosX-zoom*7,PosY,PosX-zoom*12,width=zoom/2)
                    Canevas.create_line(PosY-zoom*2,PosX-zoom*10,PosY,PosX-zoom*12,width=zoom/2)
                    Canevas.create_line(PosY+zoom*2,PosX-zoom*10,PosY,PosX-zoom*12,width=zoom/2)
                if grille[i,j] == BAS:
                    PosY = j *20*zoom +20+zoom*10
                    PosX = i *20*zoom +20+zoom*10
                    Canevas.create_line(PosY,PosX+zoom*7,PosY,PosX+zoom*12,width=zoom/2)
                    Canevas.create_line(PosY-zoom*2,PosX+zoom*10,PosY,PosX+zoom*12,width=zoom/2)
                    Canevas.create_line(PosY+zoom*2,PosX+zoom*10,PosY,PosX+zoom*12,width=zoom/2)
                if grille[i,j] == GAUCHE:
                    PosY = j *20*zoom +20+zoom*10
                    PosX = i *20*zoom +20+zoom*10
                    Canevas.create_line(PosY-zoom*7,PosX,PosY-zoom*12,PosX,width=zoom/2)
                    Canevas.create_line(PosY-zoom*10,PosX-zoom*2,PosY-zoom*12,PosX,width=zoom/2)
                    Canevas.create_line(PosY-zoom*10,PosX+zoom*2,PosY-zoom*12,PosX,width=zoom/2) 
                if grille[i,j] == DROITE:
                    PosY = j *20*zoom +20+zoom*10
                    PosX = i *20*zoom +20+zoom*10
                    Canevas.create_line(PosY+zoom*7,PosX,PosY+zoom*12,PosX,width=zoom/2)
                    Canevas.create_line(PosY+zoom*10,PosX-zoom*2,PosY+zoom*12,PosX,width=zoom/2)
                    Canevas.create_line(PosY+zoom*10,PosX+zoom*2,PosY+zoom*12,PosX,width=zoom/2) 
                    


#donne la valeur de l'épaisseur d'une fleche de direction pour la solution
def grosseurfleche(valeur):
    if valeur == 0:
        return 0
    if valeur < 0.33:
        return 1
    if valeur < 0.66:
        return 2
    return 3

                    
#affiches les solutions mixtes.
#plus la fleche est grosse et plus la probabilité d'aller vers la case est grande                    
def afficheSolutionMixte(grille):
    ecart = 3
    global saveLine
    saveLine=[]
    vzero = np.zeros(nbcriteres, dtype=np.int)
    for i in range (nblignes):
        for j in range (nbcolonnes):
            if (i != nblignes-1 or  j != nbcolonnes-1) and np.array_equal(g[i,j], vzero)==False:
                #fleche du haut
                if grille[i,j,0] != 0 and  not math.isnan(grille[i,j,0]):
                    taille = zoom/2 * grosseurfleche(grille[i,j,0])
                    PosY = j *20*zoom +20+zoom*10
                    PosX = i *20*zoom +20+zoom*10
                    saveLine.append(Canevas.create_line(PosY+ecart*zoom,PosX-zoom*7,PosY+ecart*zoom,PosX-zoom*12.5,width=taille))
                    saveLine.append(Canevas.create_line(PosY-zoom*2+ecart*zoom,PosX-zoom*10,PosY+ecart*zoom,PosX-zoom*12,width=taille))
                    saveLine.append(Canevas.create_line(PosY+zoom*2+ecart*zoom,PosX-zoom*10,PosY+ecart*zoom,PosX-zoom*12,width=taille))
                #fleche du bas    
                if grille[i,j,1] != 0 and  not math.isnan(grille[i,j,1]):
                    taille = zoom/2 * grosseurfleche(grille[i,j,1])
                    PosY = j *20*zoom +20+zoom*10
                    PosX = i *20*zoom +20+zoom*10
                    saveLine.append(Canevas.create_line(PosY-ecart*zoom,PosX+zoom*7,PosY-ecart*zoom,PosX+zoom*12.5,width=taille))
                    saveLine.append(Canevas.create_line(PosY-zoom*2-ecart*zoom,PosX+zoom*10,PosY-ecart*zoom,PosX+zoom*12,width=taille))
                    saveLine.append(Canevas.create_line(PosY+zoom*2-ecart*zoom,PosX+zoom*10,PosY-ecart*zoom,PosX+zoom*12,width=taille))
                #fleche du gauche    
                if grille[i,j,2] != 0 and  not math.isnan(grille[i,j,2]):
                    taille = zoom/2 * grosseurfleche(grille[i,j,2])
                    PosY = j *20*zoom +20+zoom*10
                    PosX = i *20*zoom +20+zoom*10
                    saveLine.append(Canevas.create_line(PosY-zoom*7,PosX+ecart*zoom,PosY-zoom*12.5,PosX+ecart*zoom,width=taille))
                    saveLine.append(Canevas.create_line(PosY-zoom*10,PosX-zoom*2+ecart*zoom,PosY-zoom*12,PosX+ecart*zoom,width=taille))
                    saveLine.append(Canevas.create_line(PosY-zoom*10,PosX+zoom*2+ecart*zoom,PosY-zoom*12,PosX+ecart*zoom,width=taille)) 
                #fleche du droite
                if grille[i,j,3] != 0 and  not math.isnan(grille[i,j,3]):
                    taille = zoom/2 * grosseurfleche(grille[i,j,3])
                    PosY = j *20*zoom +20+zoom*10
                    PosX = i *20*zoom +20+zoom*10
                    saveLine.append(Canevas.create_line(PosY+zoom*7,PosX-ecart*zoom,PosY+zoom*12.5,PosX-ecart*zoom,width=taille))
                    saveLine.append(Canevas.create_line(PosY+zoom*10,PosX-zoom*2-ecart*zoom,PosY+zoom*12,PosX-ecart*zoom,width=taille))
                    saveLine.append(Canevas.create_line(PosY+zoom*10,PosX+zoom*2-ecart*zoom,PosY+zoom*12,PosX-ecart*zoom,width=taille)) 
    
    
def afficheSolutionMixteButton():
    global politique, Pion,alpha,poidcritere
    effacer()
        
    #initinalise alpha
    alpha = np.zeros(nbcriteres)
    for i in range (nbcriteres):
        alpha[i] = poidcritere[i].get()
        
    politique = politiquelancher()
    print "politique"
    print politique
    afficheSolutionMixte(politique)       


def effacer():
    for i in range (len(saveLine)):
        Canevas.delete(saveLine[i])
    



################################################################################
#
#                            PROGRAMME PRINCIPAL
#
################################################################################


# GRAPHIQUE
#Creation de la fenetre

#########################initialisation#############################

#variable pour initialisation , ne pas y faire attention 
''' a renommer'''
gagner = ""
init = Tk()
init.title('initialisation')
nb = ""
nbprime=""
nb2 = ""
nb3 = ""
critere=""
liste=""

initFenetre()

# Creation d'un widget Canvas (pour la grille)
Largeur = zoom*20*nbcolonnes+40
Hauteur = zoom*20*nblignes+40

Mafenetre = Tk()
Mafenetre.title('MDP')

#######################creation de l'affichage#########################


champ_label3 = Label(Mafenetre, text=" policy's choice")
champ_label3.grid(row=0, column=4,sticky=N)
liste= StringVar()
liste.set("1")
choix1 = Radiobutton(Mafenetre, text= "multicriterion sum", variable = liste, value="1",font = "Verdana 10 bold")
choix2 = Radiobutton(Mafenetre, text= " min max criterion", variable = liste, value="2",font = "Verdana 10 bold")
choix3 = Radiobutton(Mafenetre, text= " min max regret", variable = liste, value="3",font = "Verdana 10 bold")
choix4 = Radiobutton(Mafenetre, text= " weighted sum", variable = liste, value="4",font = "Verdana 10 bold")
choix5 = Radiobutton(Mafenetre, text= " weighted regret", variable = liste, value="5",font = "Verdana 10 bold")
choix1.grid(row=1, column=4,sticky=N)
choix2.grid(row=2, column=4,sticky=N)
choix3.grid(row=3, column=4,sticky=N)
choix4.grid(row=4, column=4,sticky=N)
choix5.grid(row=5, column=4,sticky=N)


champ_labelprime = Label(Mafenetre, text="wieght for wiegted methods ")
champ_labelprime.grid(row=0,column =5)

for i in range(nbcriteres):
    poidcritere.append( IntVar())
    poidcritere[i].set(1)
    # Création d'un widget Spinbox
    boiteprime = Spinbox(Mafenetre,from_=1,to=100,increment=1,textvariable=poidcritere[i],width=1)
    boiteprime.grid(row=(i)%(4)+1, column =5+((i)/4))

Button(Mafenetre, text ='View Solution', command = afficheSolutionMixteButton).grid(row=5, column=5)#pack(side=LEFT,padx=5,pady=5)
Button(Mafenetre, text ='Erase Solution', command = effacer).grid(row=5, column=6)#pack(side=LEFT,padx=5,pady=5)



# ecriture du quadrillage et coloration
Canevas = Canvas(Mafenetre, width = Largeur, height =Hauteur, bg =mywhite)
for i in range(nblignes+1):
    ni=zoom*20*i+20
    Canevas.create_line(20, ni, Largeur-20,ni)
for j in range(nbcolonnes+1):
    nj=zoom*20*j+20
    Canevas.create_line(nj, 20, nj, Hauteur-20)
    
#creation de la grille de poid des critere
g = defineMaze(nblignes, nbcolonnes,  nbcriteres)

#affichage des poids des cirteres
'''
colordrawMulti9(g,nblignes,nbcolonnes)
'''
colordrawlancher(nbcriteres)

#initilaise les touches du clavier 
Canevas.focus_set()
Canevas.bind('<Key>',Clavier)
Canevas.grid(row=0, column=1,rowspan=6,columnspan=3,padx =5, pady =5)



# Creation d'un widget Button (bouton Quitter)
Button(Mafenetre, text ='Restart', command = initialize).grid(row=6, column=0)#pack(side=LEFT,padx=5,pady=5)
Button(Mafenetre, text ='Quit', command = Mafenetre.destroy).grid(row=6, column=1)#pack(side=LEFT,padx=5,pady=5)



#Création de l'affichage des coûts

cost= np.zeros(nbcriteres+1, dtype=np.int)
#Création de l'affichage des coûts
w = Label(Mafenetre, text='cost = '+str(cost[0]),fg=mywalls,font = "Verdana 15 bold")
w.grid(row=6, column=3)#pack(side=RIGHT) 
labels =[]
for i in range (nbcriteres):
    labels.append(Label(Mafenetre, text= colorname[i+1]+'='+str(cost[i+1])+' | ',fg=color[i+1],font = "Verdana 10 bold"))
    labels[i].grid(row=6, column=4+i)#pack(side=RIGHT)

Pion = Canevas.create_oval(PosX-10,PosY-10,PosX+10,PosY+10,width=2,outline='black',fill=myyellow)

initialize()

print "g"
print g




################################affichage solution#########################################

#
#(A, b, obj) = dualSomme(g, gamma,probaTransition,nbcriteres)
#
#print 'gamma=' +str(gamma)+ "   proba=" + str(probaTransition) 
#v, m,t = gurobiMultiSomme(A, b, obj,nblignes,nbcolonnes)
#
#politique = politique(v, g)
#print "pol :"
#print politique
#grilleSolution= createGrilleSoluce(politique)
#print 'grilleSolution'
#print grilleSolution
#afficheSolutionMixte(politique)
#
#politique,v = politiquelancher()
#print "politique"
#print politique
#afficheSolutionMixte(politique)


#pol= [[[0,0.5,0,0.5],[0,0.5,0,0.5],[0,0.5,0,0.5]],[[0,0.5,0,0.5],[0,0.5,0,0.5],[0,0.5,0,0.5]],[[0,0.5,0,0.5],[0,0.5,0,0.5],[0,0.5,0,0.5]]]

#pol = np.zeros(((10,10,4)))
#for i in range(3):
#    for j in range (3):
#        pol[i,j,1]= 0.6
#        pol[i,j,3]= 0.2
#        pol[i,j,2]= 0.9
#
#afficheSolutionMixte(pol)







Mafenetre.mainloop()


