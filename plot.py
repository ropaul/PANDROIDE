# -*- coding: utf-8 -*-
"""
Created on Tue May 19 16:14:04 2015

@author: teddy
"""

import matplotlib.pyplot as plt
import numpy as np


#point est une matrice avec 2 ligne et n colonne chaque ligne représente labsicesse et l'ordonnée
def affichePoint(points):
    n = points.shape[1]
    ab =np.zeros(n)
    maxab=0
    maxcoord=0
    coord =np.zeros(n)
    for i in range(n):
        ab[i]=points[i][1]
        if (ab[i]> maxab):
            maxab = ab[i]
        coord[i]=points[i][0]
        if (coord[i]> maxab):
            maxcoord = coord[i]
    plt.plot(ab,coord,'ro')
    plt.axis([0,maxcoord+20,0,maxab+20])
    plt.show()
    
    

#plt.plot([1,2,3,4], [1,4,9,16], 'ro')
#plt.axis([0, 15, 0, 16])
#plt.show()
#
#plt.plot([8,7,2,4], [1,4,9,14], 'ro')
#
#plt.show()

