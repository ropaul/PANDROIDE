# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 10:33:41 2015

@author: teddy & rose-may
"""

# script pion.py
from modele_1critere import *
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

#Position initiale du robot dans le dessin
PosX = 20+10*zoom 
PosY = 20+10*zoom



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

#sert a l'initalisation
nb = ""
nbprime=""
nb2 = ""
nb3 = ""



################################################################################
#
#                            FONCTIONS GRAPHIQUES
#
################################################################################

def initialize():
    global cost,posX,posY,PosX,PosY
# position initiale du robot
    
    for k in range(5):
        cost[k]=0
# cout et affichage
    i=0
    j=0
    PosY = j *20*zoom +20+zoom*10
    PosX = i *20*zoom +20+zoom*10
    posY = j
    posX = i
    Canevas.coords(Pion,PosX -9*zoom, PosY -9*zoom, PosX +9*zoom, PosY +9*zoom)
    w.config(text='Cost = '+ str(cost[0]))
    w1.config(text='vert = '+ str(cost[1]))
    w2.config(text='bleu = '+ str(cost[2]))
    w3.config(text='rouge = '+ str(cost[3]))
    w4.config(text='noir = '+ str(cost[4]))


# dessine la grille avec des ovales
def colordraw(g,nblignes,nbcolonnes):
    
    for i in range(nblignes):
        for j in range(nbcolonnes):          
            y =zoom*20*j+20
            x =zoom*20*i+20
            if i == 0 and j == 0 :
                Canevas.create_text(x+zoom*10,y+zoom*10,text="DEPART",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
            else:
                if i == nblignes -1 and j == nbcolonnes -1 :
                    Canevas.create_text(y+zoom*10,x+zoom*10,text="BUT",fill=myblack,font = "Verdana "+str(int(10*zoom/3))+" bold")
                else:
                    if g[i,j]==0: 
                        Canevas.create_rectangle(y, x, y+zoom*20, x+zoom*20, fill=myblack)
                    else:
                        Canevas.create_oval(y+zoom*(10-3),x+zoom*(10-3),y+zoom*(10+3),x+zoom*(10+3),width=1,outline=color[g[i,j]],fill=color[g[i,j]])
                   
                        

#fonction servant a manipuler le pion dans la labirhynte
def Clavier (event):
    global PosX,PosY,posX,posY,cost,g,pol
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
        touche = marcheAuto(i,j,pol)
    if (touche =="a"or touche== "Up") and i>0 :
        if g[i-1,j]!=0 :
            print 'haut'
            trans= transition (g,HAUT,i,j,probaTransition)
            for t in trans:
                value += trans[t]
                if(value > z):
                    i=t[0]
                    j=t[1]
                    if (g[i,j]>0):
                        cost[g[i,j]] +=1
                    break
    if (touche =="q" or touche=="Down") and i< nblignes -1:
        if g[i+1,j]!=0 :
            print 'bas'
            trans= transition (g,BAS,i,j,probaTransition)
            for t in trans:
                value += trans[t]
                if(value > z):
                    i=t[0]
                    j=t[1]
                    if (g[i,j]>0):
                        cost[g[i,j]] +=1
                    break
    if (touche =="l" or touche=="Left") and j>0:
        if  g[i,j-1]!=0 :
            print 'gauche'
            trans= transition (g,GAUCHE,i,j,probaTransition)
            for t in trans:
                value += trans[t]
                if(value > z):
                    i=t[0]
                    j=t[1]
                    if (g[i,j]>0):
                        cost[g[i,j]] +=1
                    break
    if (touche =="m" or touche== "Right") and j< nbcolonnes-1 :
        if g[i,j+1]!=0 :
            print 'droit'
            trans= transition (g,DROITE,i,j,probaTransition)
            for t in trans:
                value += trans[t]
                if(value > z):
                    i=t[0]
                    j=t[1]
                    if (g[i,j]>0):
                        cost[g[i,j]] +=1
                    break
#    print 'j='+str(j)+'  i='+str(i)
    PosY = j *20*zoom +20+zoom*10
    PosX = i *20*zoom +20+zoom*10
    posY = j
    posX = i
#    print 'PosX=' +str(PosX) + 'PosY=' +str(PosY)
    Canevas.coords(Pion,PosY -9*zoom, PosX -9*zoom, PosY +9*zoom, PosX +9*zoom)
    cost[0]=0    
    for k in range(4):
        cost[0]+=cost[k+1]*weight[k+1]
    w.config(text='Cost = '+ str(cost[0]))
    w1.config(text='vert = '+ str(cost[1]))
    w2.config(text='bleu = '+ str(cost[2]))
    w3.config(text='rouge = '+ str(cost[3]))
    w4.config(text='noir = '+ str(cost[4]))
#    if (i== nblignes-1 and j == nbcolonnes -1):
#        gagner = Tk()
#        gagner.title('Gagner')
#        texte = Label(gagner, text='Vous avez gagné !',fg=myblack,font = "Verdana 12 bold")
#        texte.pack()
#        Button(gagner, text ='Quit', command = gagner.destroy).pack(side=BOTTOM,padx=5,pady=5)
#        gagner.mainloop()
#        
    #pour qu'on puisse restart avec le bacspace
    if touche == 'BackSpace':
        initialize()
    #pour qu'on quite le programme en appuyant sur esc
    if touche == 'Escape':
        Fenetre.destroy()


#fonction servant a detruire le pop-up de victoire
def gagne():
    initialize()
    gagner.destroy()

# comme gagne mais pour l'associer a un bouton
def gagneKey(event):
    gagner()

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
    
    
        
# fonction servant a afficher la solution op donné par le PDM        
def afficheSolution(grille):
    for i in range (nblignes):
        for j in range (nbcolonnes):
            if (i != nblignes-1 or  j != nbcolonnes-1) and g[i,j]!= 0:
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
                
def afficheSolutionButton():
    afficheSolution(pol)                
                
#fonction servant a afficher des solutions multicritère                
def flechemixte (i,j ,pH,pB,pG,pD): #i et j les coord , pH,pB,pG les pourcentage de haut, bas , etc
    xi = i+zoom*pD*7 -zoom*pG*7
    yi = j+zoom*pH*7 -zoom*pD*7
    xf = i+zoom*pD*12 -zoom*pG*12
    yf =j+zoom*pH*12 -zoom*pD*12
    cv.create_line(xi,yi,xf,yf)
#                
#def afficheSolutionmixte(grille):
#    for i in range (nblignes):
#        for j in range (nbcolonnes):
#            if grille[i,j] == HAUT:
                


################################################################################
#
#                               INITIALISATION
#
################################################################################


#Sert a la premiere initialisation du labyrinthe. verifie si tous les choix demandé sont fait
def choix():
    global gamma, probaTransition,nblignes, nbcolonnes,zoom
#    if ((liste.get() != "1" and liste.get() != "2"and liste.get() != "3")):
#        
#        champ_erreur = Label(init, text="Erreur sur les entrer")
#        champ_erreur.pack()
#        
#        return
    if ( nb.get() != '' ):
        valueL= (nb.get())
    if ( nbprime.get() != '' ):
        valueC= (nbprime.get())        
            
        nblignes = valueL
        nbcolonnes = valueC
        
        val = max(valueC,valueL)
        
        if val >0:# and valueCL < 5:
            zoom = 3
        if val >5 :#and valueCL < 10:
            zoom = 2
        if val >=10:
            zoom = 1
        if val >=15:
            zoom = (30.0/val)
        
            
    probaTransition= nb2.get()
    gamma = nb3.get()
    init.destroy()
    
def choixEvent(event):
    if event.keysym == 'Return':
        choix();

#initialise la fenetre d'initialisation
def initFenetre() :
    global nb,nbprime, nb2 , nb3, init
    #création fenetre choix
    
    init.title('Choix')
    
    champ_label = Label(init, text="Number of line")
    champ_label.pack()
    nb = IntVar()
    nb.set(5)
    # Création d'un widget Spinbox
    boite = Spinbox(init,from_=3,to=42,increment=1,textvariable=nb,width=5)
    boite.pack(padx=30,pady=10)
    
    champ_labelprime = Label(init, text="Number of column ")
    champ_labelprime.pack()
    nbprime = IntVar()
    nbprime.set(5)
    # Création d'un widget Spinbox
    boiteprime = Spinbox(init,from_=3,to=42,increment=1,textvariable=nbprime,width=5)
    boiteprime.pack(padx=30,pady=10)    
    
    champ_label2 = Label(init, text="proba de transition")
    champ_label2.pack()
    nb2 = DoubleVar()
    nb2.set(0.8)
    # Création d'un widget Spinbox
    boite2 = Spinbox(init,from_=0,to=1,increment=0.05,textvariable=nb2,width=5)
    boite2.pack(padx=30,pady=10)    
    
    
    champ_label3 = Label(init, text="gamma")
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
    
    
#    valueCL= (nb.get())
#    print  type(valueCL)    
#    nblignes = valueCL
#    nbcolonnes = valueCL

################################################################################
#
#                            PROGRAMME PRINCIPAL
#
################################################################################


# GRAPHIQUE
#Creation de la fenetre


#########################initialisation#############################

#init
gagner = ""
init = Tk()
init.title('initialisation')
initFenetre()

# Creation d'un widget Canvas (pour la grille)
Largeur = zoom*20*nbcolonnes+40
Hauteur = zoom*20*nblignes+40

Mafenetre = Tk()
Mafenetre.title('MDP')



#######################creation de l'affichage#########################

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
Button(Mafenetre, text ='View Soluce', command = afficheSolutionButton).pack(side=LEFT,padx=5,pady=5)


#Création de l'affichage des coûts
w = Label(Mafenetre, text='cost = '+str(cost[0]),fg=mywalls,font = "Verdana 20 bold")
w.pack(side=RIGHT) 
w1 = Label(Mafenetre, text='vert = '+str(cost[1])+' | ',fg=mygreen,font = "Verdana 12 bold")
w1.pack(side=RIGHT)
w2 = Label(Mafenetre, text='bleu = '+str(cost[2])+' | ',fg=myblue,font = "Verdana 12 bold")
w2.pack(side=RIGHT)
w3 = Label(Mafenetre, text='rouge = '+str(cost[3])+' | ',fg=myred,font = "Verdana 12 bold")
w3.pack(side=RIGHT)
w4 = Label(Mafenetre, text='noir = '+str(cost[4])+' | ',fg=myblack,font = "Verdana 12 bold")
w4.pack(side=RIGHT) 

Pion = Canevas.create_oval(PosX-10,PosY-10,PosX+10,PosY+10,width=2,outline='black',fill=myyellow)

initialize()

################################affichage solution#########################################
(A, b, obj) = programmeprimal(g, gamma,probaTransition)
v, m,t = resolutionGurobiprimal(A, b, obj,nblignes,nbcolonnes)

pol = politique(v, g,probaTransition,gamma)
print "pol :"
print pol


Mafenetre.mainloop()


