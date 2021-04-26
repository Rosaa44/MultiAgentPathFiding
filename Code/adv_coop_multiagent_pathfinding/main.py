
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

from search.grid2D import ProblemeGrid2D,ProblemeGrid2D_Time
from search import probleme,algorithmes



# ---- ---- ---- ---- ---- ----
# ---- Misc                ----
# ---- ---- ---- ---- ---- ----




# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()


        
def init(_boardname=None):
    global player,game
    name = _boardname if _boardname is not None else 'exAdvCoopMap'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 8  # frames per second
    game.mainiteration()
    player = game.player
    

init()



#-------------------------------
# Initialisation
#-------------------------------

nbLignes = game.spriteBuilder.rowsize
nbCols = game.spriteBuilder.colsize
def legal_position(row,col):
        # une position legale est dans la carte et pas sur un mur
        return ((row,col) not in wallStates) and row>=0 and row<nbLignes and col>=0 and col<nbCols
   
print("lignes", nbLignes)
print("colonnes", nbCols)


players = [o for o in game.layers['joueur']]
nbPlayers = len(players)
score = [0]*nbPlayers

   
       
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
            
    
#-------------------------------
# Attributaion aleatoire des fioles 
#-------------------------------
objectifs = goalStates
random.shuffle(objectifs)
#tmp5=objectifs[5]
#tmp4=objectifs[4]
#tmp1=objectifs[1]
#tmp2=objectifs[2]
#objectifs[1]=tmp5
#objectifs[2]=tmp4
#objectifs[4]=tmp1
#objectifs[5]=tmp2
N=len(objectifs)
for i in range(N):
    print("Objectif joueur "+str(i)+" : ", objectifs[i])
g =np.ones((nbLignes,nbCols),dtype=bool)  # par defaut la matrice comprend des True  
for w in wallStates:            # putting False for walls
    g[w]=False
N=len(objectifs)
posPlayers = initStates    
compteur=[0 for _ in range(nbPlayers)]    
    
def strategie1(iterations):
    print("N: ",N)
    it=[1 for _ in range(N)]
    paths=[[] for _ in range(N)]
    for i in range(N):
        p = ProblemeGrid2D(initStates[i],objectifs[i],g,'manhattan')
        paths[i] = probleme.astar(p)
    i_joueurs=[0 for _ in range(N)]
    n=int(N/2)
    equipe=[[i for i in range(n)],[i for i in range(n,N)]]
    equipe_courante=equipe[0]
    for i in range(iterations):
        for joueur in equipe_courante:
            if(score[joueur]==0):
                posPlayers[joueur]=paths[joueur][i_joueurs[joueur]]
                compteur[joueur]+=1
                players[joueur].set_rowcol(posPlayers[joueur][0],posPlayers[joueur][1])
                if(posPlayers[joueur]==objectifs[joueur]):
                    score[joueur]+=1
                    it[joueur]=0
                    print("Le joueur "+str(joueur)+" a atteint son but !")
        #on change d'équipe
        equipe_courante=equipe[i%len(equipe)]
        col=True
        while(col):
            col=False
            for joueur1 in equipe_courante:
                for joueur2 in range(N):
                    if(joueur1!=joueur2 and it[joueur1]!=0):
                        place1_joueur1=paths[joueur1][i_joueurs[joueur1]]     
                        place2_joueur1=paths[joueur1][i_joueurs[joueur1]+it[joueur1]]
                        if(joueur2 in equipe_courante):
                            place1_joueur2=paths[joueur2][i_joueurs[joueur2]]
                            place2_joueur2=paths[joueur2][i_joueurs[joueur2]+it[joueur2]]
                        else:
                            place1_joueur2=paths[joueur2][i_joueurs[joueur2]]
                            place2_joueur2=paths[joueur2][i_joueurs[joueur2]]
                        r=algorithmes.futur_collision(place1_joueur1,place2_joueur1,place1_joueur2,place2_joueur2)
                        if(r==2):
                            col=True
                            paths[joueur1]=algorithmes.astar_splicing(joueur1,paths[joueur1],i_joueurs[joueur1],place1_joueur2,g.copy(),score,objectifs)
                        elif(r==1):
                            col=True
                            paths[joueur1]=algorithmes.astar_splicing(joueur1,paths[joueur1],i_joueurs[joueur1],place2_joueur2,g.copy(),score,objectifs)

                            
                            
        for joueur in equipe_courante:
            if(i_joueurs[joueur]<len(paths[joueur])-1):
                i_joueurs[joueur]+=it[joueur]
        
        # on passe a l'iteration suivante du jeu
        game.mainiteration()
    
def chemin_space_time(debut,fin,g,reservations,joueur,iterations,temps_initial):
    p = ProblemeGrid2D_Time(debut,fin,g,'manhattan',reservations,joueur)
    path = probleme.astar_space_time(p,temps_initial)
    re=len(path)
    res={}
    for case in path:
        res[case]="r"
        (x,y,t)=case
    for i in range(t+1,iterations):
        c=(x,y,i)
        res[c]="r"
        path.append(c)
    return (res,path)

def mise_a_jour_autres_paths(joueur1,equipe_courante,paths,reservations,iterations,i_courant):
    col=True
    while(col):
        col=False
        for i in equipe_courante:
            if(i!=joueur1):
                for (x,y,t),val in reservations[i].items():
                    if(((x,y,t) in reservations[joueur1]) and reservations[joueur1][(x,y,t)]=="r" and val=="r"):
                        col=True
                        eviter=(x,y,t)
                        cop=equipe_courante.copy()
                        cop.remove(i)
                        res_cop=[reservations[i] for i in cop]
                        l=res_cop+[{eviter:"r"}]
                        reservations[i],p=chemin_space_time((paths[i][i_courant][0],paths[i][i_courant][1]),objectifs[i],g,l,equipe_courante.index(i),iterations,i_courant)
                        paths[i]=paths[i][:i_courant]+p
    return (reservations,paths)
                        
                                    
def strategie2(iterations):
    global score
    #comprend toutes les cases réservées dans les 2 equipes
    N=nbPlayers
    reservations=[{} for _ in range(N)]
    n=int(N/2)
    equipe2=[i for i in range(N)]
    equipe=[equipe2[:n],equipe2[n:]]
    paths=[[] for _ in range(N)]
    print("Equipe 1 : ",equipe[0]," Equipe 2 : ",equipe[1])
    for equ in equipe:
        j=0
        for joueur in equ:
            reserv_equipe=[reservations[j] for j in equ]
            reservations[joueur],paths[joueur]=chemin_space_time(initStates[joueur],objectifs[joueur],g,reserv_equipe,j,iterations,0)
            j+=1
        for joueur in equ:
            reservations,paths=mise_a_jour_autres_paths(joueur,equ,paths,reservations,iterations,0)
    equipe_courante=equipe[0]
    i_courant=0
    liste_i=[0,0]
    equipe_pause=equipe[1] 
    for it in range(iterations):
        for joueur in equipe_courante:
            if(score[joueur]==0):
                case=paths[joueur][i_courant]#la case correspondant au temps i
                posPlayers[joueur]=(case[0],case[1])
                players[joueur].set_rowcol(posPlayers[joueur][0],posPlayers[joueur][1])
                if(posPlayers[joueur]==objectifs[joueur]):
                    score[joueur]+=1
                    print("Le joueur "+str(joueur)+" a atteint son but !")
                else:
                    compteur[joueur]+=1

                    
        tmp=equipe_courante
        equipe_courante=equipe_pause
        equipe_pause=tmp
        
        liste_i[it%2]+=1
        i_courant=liste_i[(it+1)%2]
        i_pas_courant=liste_i[it%2]
        col=True
        while(col):
            col=False
            for joueur1 in equipe_courante:
                if(score[joueur1]==0):
                    place_joueur1=(paths[joueur1][i_courant+1][0],paths[joueur1][i_courant+1][1])
                    for joueur2 in equipe_pause:
                        place_joueur2=(paths[joueur2][i_pas_courant][0],paths[joueur2][i_pas_courant][1])
                        if(place_joueur1==place_joueur2):
                            col=True
                            eviter=(place_joueur1[0],place_joueur1[1],i_courant+1)
                            for case in paths[joueur1][i_courant:]:
                                reservations[joueur1]="l" #la case est libérée
                            l=[{eviter:"r"}]
                            reservations[joueur1],p=chemin_space_time((paths[joueur1][i_courant][0],paths[joueur1][i_courant][1]),objectifs[joueur1],g,l,-1,iterations,i_courant)
                            paths[joueur1]=paths[joueur1][:i_courant]+p
                            reservations,paths=mise_a_jour_autres_paths(joueur1,equipe_courante,paths,reservations,iterations,i_courant) 

        game.mainiteration()  
       
def strategie3(iterations):
    global score
    equipes=[[0,1,2],[3,4,5]]
    choix =initStates
    choix_imm=algorithmes.immatriculation(initStates, 1)

    profondeur=3
    successeurs,scorex,dic=algorithmes.arbre_main(profondeur,equipes,g,initStates,objectifs)
    arbre=probleme.ArbreMINMAX(successeurs,scorex,profondeur) 

    for it in range(iterations):
        for joueur in range(nbPlayers):
            case=choix[joueur]
            if(score[joueur]==0):
                compteur[joueur]+=1
            posPlayers[joueur]=(case[0],case[1])
            players[joueur].set_rowcol(posPlayers[joueur][0],posPlayers[joueur][1])
            if(posPlayers[joueur]==objectifs[joueur] and score[joueur]==0):
                score[joueur]+=1
                print("Le joueur "+str(joueur)+" a atteint son but !")
        game.mainiteration()  
        l=arbre.alphabeta(choix_imm,it%2==0)
        choix_imm=l[1][1]
        choix=dic[choix_imm][0]
        successeurs,scorex,dic=algorithmes.mise_a_jour_arbre(choix_imm, equipes, (it+1)%2, profondeur, g, objectifs)
        arbre=probleme.ArbreMINMAX(successeurs,scorex,profondeur)

        
        
        
        
if __name__ == '__main__':
    nbiterations=100
    #stratégie 1 :
    #strategie1(nbiterations)
    #stratégie 2 :
    strategie2(nbiterations)
    #stratégie 3 :
    #strategie3(nbiterations)
    print ("scores: ", score)
    print("longueurs chemin : ",compteur)
    score_equipe1=[score[i] for i in range(3)]
    score_equipe2=[score[i] for i in range(3,6)]
    s1=sum(score_equipe1)
    s2=sum(score_equipe2)
    if(s1!=s2):
        if(s1<s2):
            print("L'équipe 2 a gagné !!!")
        else:
            print("L'équipe 1 a gagné !!!")
    else:
        compteur_equipe1=[compteur[i] for i in range(3)]
        compteur_equipe2=[compteur[i] for i in range(3,6)]
        c1=sum(compteur_equipe1)
        c2=sum(compteur_equipe2)
        if(c1<c2):
            print("L'équipe 1 a gagné !!!")
        elif(c2<c1):
            print("L'équipe 2 a gagné !!!")
        else:
            print("Les deux équipes sont ex-aequo !!!")
    compteur_equipe1=[i%100 for i in compteur_equipe1]
    compteur_equipe2=[i%100 for i in compteur_equipe2]
    moyenne=(sum(compteur_equipe1)+sum(compteur_equipe2))/sum(score)
    print("Moyenne : ",moyenne)
    



