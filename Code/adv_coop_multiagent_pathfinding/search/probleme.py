# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 09:32:05 2016

@author: nicolas
"""

import numpy as np
import copy
import heapq
from abc import ABCMeta, abstractmethod
import functools
import time


def distManhattan(p1,p2):
    """ calcule la distance de Manhattan entre le tuple 
        p1 et le tuple p2
        """
    (x1,y1)=p1
    (x2,y2)=p2
    return abs(x1-x2)+abs(y1-y2) 



    
###############################################################################

class Probleme(object):
    """ On definit un probleme comme étant: 
        - un état initial
        - un état but
        - une heuristique
        """
        
    def __init__(self,init,but,heuristique):
        self.init=init
        self.but=but
        self.heuristique=heuristique
        
    @abstractmethod
    def estBut(self,e):
        """ retourne vrai si l'état e est un état but
            """
        pass
        
    @abstractmethod    
    def cost(self,e1,e2):
        """ donne le cout d'une action entre e1 et e2, 
            """
        pass
        
    @abstractmethod
    def successeurs(self,etat):
        """ retourne une liste avec les successeurs possibles
            """
        pass
        
    @abstractmethod
    def immatriculation(self,etat):
        """ génère une chaine permettant d'identifier un état de manière unique
            """
        pass
    
    



###############################################################################

@functools.total_ordering # to provide comparison of nodes
class Noeud:
    def __init__(self, etat, g, pere=None):
        self.etat = etat
        self.g = g
        self.pere = pere
        
    def __str__(self):
        #return np.array_str(self.etat) + "valeur=" + str(self.g)
        return str(self.etat) + " valeur=" + str(self.g)
        
    def __eq__(self, other):
        return str(self) == str(other)
        
    def __lt__(self, other):
        return str(self) < str(other)
        
    def expand(self,p):
        """ étend un noeud avec ces fils
            pour un probleme de taquin p donné
            """
        nouveaux_fils = [Noeud(s,self.g+p.cost(self.etat,s),self) for s in p.successeurs(self.etat)]
        return nouveaux_fils
        
    def expandNext(self,p,k):
        """ étend un noeud unique, le k-ième fils du noeud n
            ou liste vide si plus de noeud à étendre
            """
        nouveaux_fils = self.expand(p)
        if len(nouveaux_fils)<k: 
            return []
        else: 
            return self.expand(p)[k-1]
            
    def trace(self,p):
        """ affiche tous les ancetres du noeud
            """
        n = self
        c=0    
        while n!=None :
            print (n)
            n = n.pere
            c+=1
        print ("Nombre d'étapes de la solution:", c-1)
        return            
        
class ArbreMINMAX:
    def __init__(self,successeurs,valeur,profondeur):
        self.inf=100000
        self.successeurs=successeurs
        self.valeur=valeur
        self.profondeur=profondeur
        #print(self.valeur)
    def alphabeta(self,state,max_debut):
        """ implementation de alphabeta, version Russel & Norvig, Chapter 6
        """
        if(max_debut):
            return self.maxValue(state,-self.inf,self.inf,self.profondeur)
        return self.minValue(state,-self.inf,self.inf,self.profondeur)
    
    def feuille(self,state): # les feuilles n'apparaissent pas comme clés dans mon dictionnaire successeurs
        return state not in self.successeurs
    
    def maxValue(self,state,alpha,beta,prof):
        if self.feuille(state) or prof==0: # si feuille on renvoie la valeur
            return (self.valeur[state],[state])
        v = -self.inf
        l1=[]
        for s in self.successeurs[state]:
            #print ("étendu noeud ", s)
            l=self.minValue(s,alpha,beta,prof-1)
            v = max(v,l[0])
            if(v==l[0]):
                l1=l[1]
            """
            if v >= beta: # coupe beta, pas la peine d'étendre les autres fils
                #print ("coupe beta")
                return (v,[(state,self.valeur[state])]+l1)
            
            alpha = max(alpha,v) # mise à jour de alpha par MAX
            """
        return (v,[state]+l1)
                
    def minValue(self,state,alpha,beta,prof):
        if self.feuille(state) or prof==0: # si feuille on renvoie la valeur
            return (self.valeur[state],[state])
        v = self.inf
        l1=[]
        for s in self.successeurs[state]:
            #print ("étendu noeud ", s)
            l=self.maxValue(s,alpha,beta,prof-1)
            v = min(v,l[0])
            if(v==l[0]):
                l1=l[1]
            """
            if v <= alpha: # coupe alpha, pas la peine d'étendre les autres fils
                #print ("coupe alpha")
                return (v,[(state,self.valeur[state])]+l1)
            
            beta = min(beta,v)
            """
        return (v ,[state]+l1)  
"""
#successeurs = {'a':['b','c','d'],'b':['e','f','g'],'c':['h','i','j'],'d':['k','l','m']}
#valeur = {'e':3, 'f':12, 'g': 8, 'h': 2, 'i':4, 'j':6, 'k':14, 'l':5, 'm':2}
successeurs = {'a':['b','c'],'b':['d','e'],'c':['f','g'],'d':['h','i'],'e':['j','k'],'f':['l','m'],'g':['n','o']}
#valeur = {'h':4, 'i':9, 'j': 8, 'k': 12, 'l':5, 'm':6, 'n':1, 'o':7}
valeur = {'h':12, 'i':49, 'j': 39, 'k': 36, 'l':3, 'm':18, 'n':4, 'o':5}  
arbre=ArbreMINMAX(successeurs,valeur)
print(arbre.alphabeta('a'))
"""
           
###############################################################################
# A*
###############################################################################

def astar(p,verbose=False,stepwise=False):
    """
    application de l'algorithme a-star
    sur un probleme donné
        """
    startTime = time.time()

    nodeInit = Noeud(p.init,0,None)
    frontiere = [(nodeInit.g+p.h_value(nodeInit.etat,p.but),nodeInit)] 

    reserve = {}        
    bestNoeud = nodeInit
    
    while frontiere != [] and not p.estBut(bestNoeud.etat):              
        (min_f,bestNoeud) = heapq.heappop(frontiere)
           
    # VERSION 1 --- On suppose qu'un noeud en réserve n'est jamais ré-étendu
    # Hypothèse de consistence de l'heuristique        
        
        if p.immatriculation(bestNoeud.etat) not in reserve:            
            reserve[p.immatriculation(bestNoeud.etat)] = bestNoeud.g #maj de reserve
            nouveauxNoeuds = bestNoeud.expand(p)
            for n in nouveauxNoeuds:
                f = n.g+p.h_value(n.etat,p.but)
                heapq.heappush(frontiere, (f,n))

    # TODO: VERSION 2 --- Un noeud en réserve peut revenir dans la frontière        
        
        stop_stepwise=""
        if stepwise==True:
            stop_stepwise = input("Press Enter to continue (s to stop)...")
            print ("best", min_f, "\n", bestNoeud)
            print ("Frontière: \n", frontiere)
            print ("Réserve:", reserve)
            if stop_stepwise=="s":
                stepwise=False
    
            
    # Mode verbose            
    # Affichage des statistiques (approximatives) de recherche   
    # et les differents etats jusqu'au but
    if verbose:
        bestNoeud.trace(p)          
        print ("=------------------------------=")
        print ("Nombre de noeuds explorés", len(reserve))
        c=0
        for (f,n) in frontiere:
            if p.immatriculation(n.etat) not in reserve:
                c+=1
        print ("Nombre de noeuds de la frontière", c)
        print ("Nombre de noeuds en mémoire:", c + len(reserve))
        print ("temps de calcul:", time.time() - startTime)
        print ("=------------------------------=")
     
    n=bestNoeud
    path = []
    while n!=None :
        path.append(n.etat)
        n = n.pere
    return path[::-1] # extended slice notation to reverse list

def astar_space_time(p,temps_initial):
    nodeInit = Noeud((p.init[0],p.init[1],temps_initial),0,None)
    frontiere = [(nodeInit.g+p.h_value((nodeInit.etat[0],nodeInit.etat[1]),p.but),nodeInit)] 

    reserve = {}        
    bestNoeud = nodeInit
    et=(bestNoeud.etat[0],bestNoeud.etat[1])
    while frontiere != [] and not p.estBut(et):              
        (min_f,bestNoeud) = heapq.heappop(frontiere)
        et=(bestNoeud.etat[0],bestNoeud.etat[1])

        if p.immatriculation(et) not in reserve:            
            reserve[p.immatriculation(et)] = bestNoeud.g #maj de reserve
            nouveauxNoeuds = bestNoeud.expand(p)
            for n in nouveauxNoeuds:
                f = n.g+p.h_value((n.etat[0],n.etat[1]),p.but)
                heapq.heappush(frontiere, (f,n))
    n=bestNoeud
    path = []
    while n!=None :
        path.append(n.etat)
        n = n.pere
    return path[::-1]

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
