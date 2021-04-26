# -*- coding: utf-8 -*-

# Nicolas, 2021-03-05
from __future__ import absolute_import, print_function, unicode_literals

import random 
import numpy as np
import sys
from itertools import chain


import pygame

from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import *
from search import probleme


# ---- ---- ---- ---- ---- ----
# ---- Misc                ----
# ---- ---- ---- ---- ---- ----




# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

map1='demoMap'
map2='exAdvCoopMap'
map3='map3'
map4='map4'
map5='map2'



game = Game()

def init(_boardname=None):
    global player,game
    name = _boardname if _boardname is not None else map1
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    player = game.player



def strategie1(alll,players,equip,numequipe,paths,initStates,objectifs,g,p,pas,indices,posPlayers,score,game): 

    """ Cette stratégie se base sur la méthode de résolution A* indépendants 
        au sein d'une équipe avec recalcul des chemins en cas de blocage. """
    
    #equipe=liste des numéros des joueurs 1 à 6 par exemple
    #paths=[[] for _ in range(nbPlayers)]
    equipe=equip.copy()

    #premier calcul du chemin de chaque objectif
    #cas où on recalcule le chemin :
    
    for joueur in equipe:
        boole = False
        k=False
        i=indices[joueur]
        if i < len(paths[joueur]):
            
            elem = paths[joueur][i]
            for joueur2 in range(alll): #s'il y a collision entre joueurs
                if (elem == posPlayers[joueur2] and joueur != joueur2):
                    #print("COLLISION ENTRE JOUEURS en : ",elem) #Dans ce cas ci on place la case elem dans les cases obstacles
                    print(joueur, paths[joueur])
                    print(joueur2, paths[joueur2])
                    boole = True
                    k=True
                    p.grid[elem]=False #devient case obstacle
                    
            # S'il y a collision ou si N est atteint:
            if (boole==True) :
                #on recalcul du point où le joueur est, vers l'objectif
                p = ProblemeGrid2D(posPlayers[joueur],objectifs[joueur],g,'manhattan')
                paths[joueur] = probleme.astar(p) 
                indices[joueur]=0
                i=indices[joueur]

                if k:
                    p.grid[elem]=True #on retire elem des cases obstacles
                    k=False
            elif (i>0 and (i%pas==0)):
                #on recalcul du point où le joueur est, vers l'objectif
                p = ProblemeGrid2D(paths[joueur][i],objectifs[joueur],g,'manhattan')
                paths[joueur] = probleme.astar(p)
                indices[joueur]=0
                i=indices[joueur]


            if i < len(paths[joueur]):

                row,col = paths[joueur][i]
                posPlayers[joueur]=(row,col)
                players[joueur].set_rowcol(row,col)
                indices[joueur]+=1
                if (row,col) == objectifs[joueur]:
                    score[numequipe]+=1
                    print("le joueur", joueur, " a atteint son but!")
                    equipe.remove(joueur)
                    k=True
                    if score[numequipe]==len(equip):
                        break
    

        game.mainiteration()



def strategie2(alll,players,equip,numequipe,paths,chemin,cpti,initStates,objectifs,g,p,N,indices,posPlayers,score,game): 

    """ Cette stratégie se base sur la méthode de résolution de path splicing
        au sein d'une équipe avec recalcul des chemins partiels en cas de blocage. """
    
    #equipe=liste des numéros des joueurs 1 à 6 par exemple
    #paths=[[] for _ in range(nbPlayers)]
    equipe=equip.copy()
    #premier calcul du chemin de chaque objectif
    #cas où on recalcule le chemin :
    
    for joueur in equipe:
        #print("Joueur ", joueur," Position: ",posPlayers[joueur])
        boole = False
        k=False
        cpt=cpti[joueur]
        i=indices[joueur]
        if i < len(chemin[joueur]):
            
            elem = chemin[joueur][i]
            for joueur2 in range(alll): #s'il y a collision entre joueurs
                if (elem == posPlayers[joueur2] and joueur != joueur2):
                    boole = True
                    k=True
                    p.grid[elem]=False #devient case obstacle
                    
            # S'il y a collision ou si N est atteint:
            
            if (boole==True) :
                #on recalcul du point où le joueur est, vers l'objectif
                if len(paths[joueur]) > N+1: #s'il reste assez d'élements que de nombre de pas
                    
                    p = ProblemeGrid2D(posPlayers[joueur],paths[joueur][cpt],g,'manhattan')
                    chemin[joueur] = probleme.astar(p)
                    chemin[joueur].extend(paths[joueur][cpt+1::]) #on rassemble le chemin recalculé et la suite de l'ancien chemin
                    indices[joueur]=0
                    i=indices[joueur]

                else: #sinon
                    p = ProblemeGrid2D(posPlayers[joueur],objectifs[joueur],g,'manhattan')
                    chemin[joueur] = probleme.astar(p)
                    indices[joueur]=0
                    i=indices[joueur]

                if k:
                    p.grid[elem]=True #on retire elem des cases obstacles
                    k=False

            elif (i>0 and (i%N==0)):
                if len(paths[joueur]) > N+1: #s'il reste assez d'élements que de nombre de pas
                    p = ProblemeGrid2D(chemin[joueur][i],paths[joueur][cpt],g,'manhattan')
                    chemin[joueur] = probleme.astar(p)
                    chemin[joueur].extend(paths[joueur][cpt::]) #on rassemble le chemin recalculé et la suite de l'ancien chemin
                    indices[joueur]=0
                    i=indices[joueur]

                else: #sinon
                    p = ProblemeGrid2D(chemin[joueur][0],objectifs[joueur],g,'manhattan')
                    paths[joueur] = probleme.astar(p)
                    indices[joueur]=0
                    i=indices[joueur]

            if i < len(chemin[joueur]):

                row,col = chemin[joueur][i]
                posPlayers[joueur]=(row,col)
                players[joueur].set_rowcol(row,col)
                indices[joueur]+=1
                if cpt<len(paths[joueur])-2:
                        cpti[joueur]+=1
                if (row,col) == objectifs[joueur]:
                    score[numequipe]+=1
                    print("le joueur", joueur, " a atteint son but!")
                    equipe.remove(joueur)
                    k=True
                    if score[numequipe]==len(equip):
                        break
    

        game.mainiteration()





iterations = 100 # default
if len(sys.argv) == 2:
    iterations = int(sys.argv[1])
print ("Iterations: ")
print (iterations)

init()
    
    #-------------------------------
    # Initialisation
    #-------------------------------
    
nbLignes = game.spriteBuilder.rowsize
nbCols = game.spriteBuilder.colsize
   
print("lignes", nbLignes)
print("colonnes", nbCols)


players = [o for o in game.layers['joueur']]
nbPlayers = len(players)
score = [0]*2

     
# on localise tous les états initiaux (loc du joueur)
# positions initiales des joueurs
initStates = [o.get_rowcol() for o in game.layers['joueur']]
print ("Init states:", initStates)

# on localise tous les objets ramassables
# sur le layer ramassable
goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
print ("Goal states:", goalStates)
    
# on localise tous les murs
# sur le layer obstacle
wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
print ("Wall states:", wallStates)

def legal_position(row,col):
    # une position legale est dans la carte et pas sur un mur
    return ((row,col) not in wallStates) and row>=0 and row<nbLignes and col>=0 and col<nbCols
    
#-------------------------------
# Attributaion aleatoire des fioles 
#-------------------------------

objectifs = goalStates
random.shuffle(objectifs)

equipe1=[i for i in range(nbPlayers//2)]
equipe2=[i for i in range(nbPlayers//2,nbPlayers)]

for i in range(nbPlayers):
    print("Objectif joueur "+ str(i) + " : ", objectifs[i])


g =np.ones((nbLignes,nbCols),dtype=bool)  # par defaut la matrice comprend des True  
for w in wallStates:            # putting False for walls
    g[w]=False
posPlayers = initStates



def duel(a,b,ecart): #stratégie_a{1,2} vs stratégie_b{1,2} avec recalcul de chemin tous les 'écarts'

    periple=[[] for _ in range(nbPlayers)]
    indices=[0 for i in range(nbPlayers)]
    cpt=[0 for i in range(nbPlayers)]
    cpt1=cpt.copy()
    cpt2=cpt.copy()
    gagnant=2

    for joueur in range (nbPlayers):
        p = ProblemeGrid2D(initStates[joueur],objectifs[joueur],g,'manhattan')
        periple[joueur] = probleme.astar(p)
        paths=periple.copy()
        chemin=paths.copy()

    
    if a==1 and b==2: #stratégie 1 (equipe 1) vs 2 (equipe 2) :
        for it in range(iterations):
            #pause=True
            strategie2(nbPlayers,players,equipe2,1,paths,chemin,cpt1,initStates,objectifs,g,p,ecart,indices,posPlayers,score,game) 
            strategie1(nbPlayers,players,equipe1,0,paths,initStates,objectifs,g,p,ecart,indices,posPlayers,score,game)      
            
            if score[0]==len(equipe1) or score[1]==len(equipe2):
                print ("scores:", score)
                if score[0]>score[1]:
                    gagnant=0
                    print("L'équipe 1 a gagné !")
                elif score[0]<score[1]:
                    gagnant=1
                    print("L'équipe 2 a gagné !")
                else:
                    gagnant=2
                    print("Les deux équipes sont ex-aequo !")
                pygame.quit()
                break;
        #quelques lignes pour suivre étape par étape les déplacements
        # if pause :
        #     stop_pause = input("Press Enter to continue (s to stop)...")
        #     if stop_pause == "q":
        #         pause = False
    if a==2 and b==1: #stratégie 1 (equipe 2) vs 2 (equipe 1) :
        for it in range(iterations):
            pause=True
            strategie2(nbPlayers,players,equipe1,0,paths,chemin,cpt1,initStates,objectifs,g,p,ecart,indices,posPlayers,score,game) 
            strategie1(nbPlayers,players,equipe2,1,paths,initStates,objectifs,g,p,ecart,indices,posPlayers,score,game)      
            
            if score[0]==len(equipe1) or score[1]==len(equipe2):
                print ("scores:", score)
                if score[0]>score[1]:
                    gagnant=0
                    print("L'équipe 1 a gagné !")
                elif score[0]<score[1]:
                    gagnant=1
                    print("L'équipe 2 a gagné !")
                else:
                    gagnant=2
                    print("Les deux équipes sont ex-aequo !")

                pygame.quit()
                break;
        #quelques lignes pour suivre étape par étape les déplacements
        # if pause :
        #     stop_pause = input("Press Enter to continue (s to stop)...")
        #     if stop_pause == "q":
        #         pause = False
    return gagnant

if __name__ == '__main__':
    # elem=[0,0]
    # for i in range(100):
    #     score=[0]*2
    #     gagnant=duel(1,2,5)
    #     if gagnant==2:
    #         elem[0]+=1
    #         elem[1]+=1
    #     else:
    #         elem[gagnant]+=1

    # print(elem,score)
    duel(1,2,5)