# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 09:32:05 2016

@author: nicolas
"""

import numpy as np
import copy
import heapq
from abc import ABCMeta, abstractmethod
import search.probleme
from search.probleme import Probleme




def distManhattan(p1,p2):
    """ calcule la distance de Manhattan entre le tuple 
        p1 et le tuple p2
        """
    (x1,y1)=p1
    (x2,y2)=p2
    return abs(x1-x2)+abs(y1-y2) 


    
###############################################################################


class ProblemeGrid2D(Probleme): 
    """ On definit un probleme de labyrithe comme étant: 
        - un état initial
        - un état but
        - une grid, donné comme un array booléen (False: obstacle)
        - une heuristique (supporte Manhattan, euclidienne)
        """ 
    def __init__(self,init,but,grid,heuristique):
            self.init=init
            self.but=but
            self.grid=grid
            self.heuristique=heuristique
        
    
    def cost(self,e1,e2):
        """ donne le cout d'une action entre e1 et e2, 
            toujours 1 pour le taquin
            """
        return 1
        
    def estBut(self,e):
        """ retourne vrai si l'état e est un état but
            """
        return (self.but==e)
        
    def estObstacle(self,e):
        """ retorune vrai si l'état est un obsacle
            """
        return (self.grid[e]==False)
        
    def estDehors(self,etat):
        """retourne vrai si en dehors de la grille
            """
        (s,_)=self.grid.shape
        (x,y)=etat
        return ((x>=s) or (y>=s) or (x<0) or (y<0))

    
        
    def successeurs(self,etat):
            """ retourne des positions successeurs possibles
                """
            current_x,current_y = etat
            d = [(0,1),(1,0),(0,-1),(-1,0)]
            etatsApresMove = [(current_x+inc_x,current_y+inc_y) for (inc_x,inc_y) in d]
            return [e for e in etatsApresMove if not(self.estDehors(e)) and not(self.estObstacle(e))]

    def immatriculation(self,etat):
        """ génère une chaine permettant d'identifier un état de manière unique
            """
        s=""
        (x,y)= etat
        s+=str(x)+"_"+str(y)
        return s
        
    def h_value(self,e1,e2):
        """ applique l'heuristique pour le calcul 
            """
        if self.heuristique=='manhattan':
            h = distManhattan(e1,e2)
        elif self.heuristique=='uniform':
            h = 1
        return h
    
  
class ProblemeGrid2D_Time(ProblemeGrid2D): 
    def __init__(self,init,but,grid,heuristique,reservations,joueur):
        self.init=init
        self.but=but
        self.grid=grid
        self.heuristique=heuristique
        self.reservations=reservations
        self.joueur=joueur
        
    def case_reservee(self,Noeud):
        i=0
        for res in self.reservations:
            if(i!=self.joueur and Noeud in res and res[Noeud]=="r"):
                return True
            i+=1
        return False  
    
    def estObstacle(self,e):
        """ retourne vrai si l'état est un obsacle
        """
        return (self.grid[(e[0],e[1])]==False) or self.case_reservee(e) 
    
    def estDehors(self,etat):
        """retourne vrai si en dehors de la grille
            """
        (s,_)=self.grid.shape
        (x,y)=etat
        return ((x>=s) or (y>=s) or (x<0) or (y<0))
    
    def croisee(self,etat,etat2):
        (x,y,t)=etat
        (x2,y2,t2)=etat2
        i=0
        for res in self.reservations:
            if(i!=self.joueur):
                if(((x,y,t2) in res and res[(x,y,t2)]=="r") and ((x2,y2,t) in res and res[(x2,y2,t)]=="r")):
                    return True
            i+=1
        return False
        
    def successeurs(self,etat):
        """ retourne des positions successeurs possibles
        """
        current_x,current_y,current_t = etat
        d = [(0,1,1),(1,0,1),(0,-1,1),(-1,0,1),(0,0,1)]
        etatsApresMove = [(current_x+inc_x,current_y+inc_y,current_t+inc_t) for (inc_x,inc_y,inc_t) in d]
        return [e for e in etatsApresMove if not self.estDehors((e[0],e[1])) and not self.estObstacle(e) and not self.croisee(etat,e)]
    
    


            


