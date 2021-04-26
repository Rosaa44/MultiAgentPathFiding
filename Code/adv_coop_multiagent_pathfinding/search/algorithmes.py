import numpy as np
import copy
import heapq
from search.grid2D import ProblemeGrid2D
import search.probleme
import time


def futur_collision(place1_joueur1,place2_joueur1,place1_joueur2,place2_joueur2):
    #collision de 1 et 2
    if(place2_joueur1==place2_joueur2):
        return 1
    #1 et 2 se croisent
    if( place1_joueur1==place2_joueur2 and place2_joueur1==place1_joueur2):
        return 2
    return 0

def astar_splicing(j,path_initial,i,case_a_eviter,g,score,objectifs):
    for joueur in range(len(score)):
        if(score[joueur]>0):
            g[objectifs[joueur]]=False
    g[case_a_eviter]=False
    n=len(path_initial)
    if(i+4<n):
        p=ProblemeGrid2D(path_initial[i],path_initial[i+4],g,'manhattan')
    else:
        p=ProblemeGrid2D(path_initial[i],objectifs[j],g,'manhattan')
    path_slice=search.probleme.astar(p)
    p1=path_initial[:i]+path_slice+path_initial[i+5:]
    if(len(p1)>=len(path_initial)+6 and i+4<n):
        ps=ProblemeGrid2D(path_initial[i],objectifs[j],g,'manhattan')
        path_slice2=search.probleme.astar(ps)
        p1=path_initial[:i]+path_slice2
    if(p1[len(p1)-1]!=objectifs[j]):
        p=ProblemeGrid2D(path_initial[i],objectifs[j],g,'manhattan')
        path_slice=search.probleme.astar(p)
        p1=path_initial[:i]+path_slice
    return p1 
   
tab_score=[]
def initialise_score_tab(g,objectifs,liste_joueurs):
    global tab_score
    for ligne in range(len(g)):
        tab_score.append([])
        for colonne in range(len(g[ligne])):
            tab_score[ligne].append([])
            if(g[ligne][colonne]):
                for obj in objectifs:
                    if((ligne,colonne)==obj):
                        tab_score[ligne][colonne].append(0)
                    else:
                        p=ProblemeGrid2D((ligne,colonne),obj,g,'manhattan')
                        path=search.probleme.astar(p)
                        tab_score[ligne][colonne].append(len(path)-1)                
                
    
def score_minmax(equipes,positions,objectifs,g):
    global tab_score
    res=0
    for joueur in equipes[0]:
        if(positions[joueur]==objectifs[joueur]):
            res+=1000
        else:
            colonne,ligne=positions[joueur]
            res-=tab_score[colonne][ligne][objectifs.index(objectifs[joueur])]
    for joueur in equipes[1]:
        if(positions[joueur]==objectifs[joueur]):
            res-=1000
        else:
            colonne,ligne=positions[joueur]
            res+=tab_score[colonne][ligne][objectifs.index(objectifs[joueur])]
    return res


    
def legal_position(n_case,v_case,g,pos_equipe_en_cours,pos_ancienne,equipe):
    def croisee(n_case1,v_case1,n_case2,v_case2):
        return n_case1==v_case2 and v_case1==n_case2
    x,y=n_case
    nbLignes=len(g)
    nbCol=len(g[0])
    if(x<0 or x>=nbLignes or y<0 or y>=nbCol):
        return False
    if(g[x][y]==False):
        return False
    i=0
    for pos in pos_equipe_en_cours:
        if pos==n_case or (i in equipe and croisee(n_case,v_case,pos,pos_ancienne[equipe[i]])):
            return False
        i+=1
    i=0
    for pos in pos_ancienne:
        if i not in equipe and pos==n_case:
            return False
        i+=1
    return True

def possibilites(racine,equipe,i,poss,g,objectifs):
    if(i==len(equipe)):
        res=[]
        for p in poss:
            r=[]
            for k in range(len(racine)):
                if k in equipe:
                    r.append(p[equipe.index(k)])
                else:
                    r.append(racine[k])
            res.append(r)
        return res
    joueur=equipe[i]
    case=racine[joueur]
    poss2=[]
    for p in poss:
        if((objectifs[joueur]==case and not g[case[0]][case[1]]) or (objectifs[joueur]==case and legal_position(case,case,g,p,racine,equipe))):
            p2=p.copy()
            p2.append(case)
            poss2.append(p2)
            g[case[0]][case[1]]=False
        else:
            for choix in [(0,0),(0,1),(1,0),(0,-1),(-1,0)]:
                new_case=(case[0]+choix[0],case[1]+choix[1])
                if(legal_position(new_case,case,g,p,racine,equipe)):
                    p2=p.copy()
                    p2.append(new_case)
                    poss2.append(p2)
    return possibilites(racine,equipe,i+1,poss2,g,objectifs)

def immatriculation(racine,i_equipe):
    res=""
    for pos in racine:
        res+=str(pos[0])+"_"+str(pos[1])+"__"
    res+=str(i_equipe)
    return res

score={}
successeurs={}
dic={} 

def arbre_rec(racine,profondeur,equipes,g,objectifs,i):
    global dic,score,successeurs
    equ=equipes[i%len(equipes)]
    if(i==profondeur):
        score[immatriculation(racine,i%len(equipes))]=score_minmax(equipes,racine,objectifs,g)
        score[immatriculation(racine,(i+1)%len(equipes))]=score_minmax(equipes,racine,objectifs,g)
        return [racine]
    poss=possibilites(racine,equ,0,[[]],g,objectifs)
    successeurs[immatriculation(racine,(i-1)%len(equipes))]=[immatriculation(p,i%len(equipes)) for p in poss]
    l=[]
    for p in poss:
        dic[immatriculation(p,i%len(equipes))]=(p,i%len(equipes))
        l+=arbre_rec(p,profondeur,equipes,g,objectifs,i+1)
    return l
   
def arbre_main(profondeur,equipes,g,initstates,objectifs):
    global score,successeurs,dic
    l=[]
    for equ in equipes:
        l+=equ
    initialise_score_tab(g,objectifs,l)
    dic[immatriculation(initstates,0)]=(initstates,0)
    l=arbre_rec(initstates, profondeur, equipes, g, objectifs, 0) 
    return (successeurs,score,dic)
    
def mise_a_jour_arbre(choix,equipes,i_equipe_du_choix,profondeur,g,objectifs):
    global score,successeurs,dic
    etendre=[choix]
    i_equ=i_equipe_du_choix
    for i in range(profondeur-1):
        
        etendre2=[]
        for c in etendre:
            etendre2+=successeurs[c]
        etendre=etendre2
        i_equ=(i_equ+1)%len(equipes)
    new_score=[]
    equipe=equipes[i_equ]
    for c in etendre:
        racine=dic[c]
        poss=possibilites(racine[0],equipe,0,[[]],g,objectifs)
        new_score+=poss
        successeurs[c]=[immatriculation(p,i_equ) for p in poss]
    for s in new_score:
        score[immatriculation(s,i_equ)]=score_minmax(equipes,s,objectifs,g)
        dic[immatriculation(s,i_equ)]=(s,i_equ)
    return (successeurs,score,dic)
        
            
    
        
    

