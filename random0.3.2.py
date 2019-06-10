from tkinter import *
from math import pi,cos,sin,sqrt,exp,atan
from threading import Thread
from random import randint
from copy import deepcopy
import pickle
from sys import exit
from time import sleep,time

running = True
TEMPS=time()
fen = Tk()
fen.geometry("1200x900")
fen["bg"]="red"

canvas = Canvas(fen,width="1200",height="900",background="white")
canvas.place(x=0,y=0)

canvas.create_line(100,200,1100,200,width=5)    
canvas.create_line(1100,200,1100,700,width=5)    
canvas.create_line(1100,700,100,700,width=5)    
canvas.create_line(100,700,100,500,width=5)    
canvas.create_line(100,200,100,400,width=5) 

#point à atteindre
xt,yt=100,450
l={}   #dictionnaire contenant toutes les informations
rayon=20    #rayon de base d'un disque
moves={}
pause=False

to_write=""

with open("coordonnees.txt","wb") as writing:
    write = pickle.Pickler(writing)
    write.dump(moves)

pos=[]
c=0
n_max = 170
amount=0
while 1:
    if amount>=n_max:
        break
    c+=1
    x,y = randint(100+rayon,1100-rayon),randint(200+rayon,700-rayon)
    test = True
    for i in pos:
        if sqrt((x-i[0])**2+(y-i[1])**2)<2*rayon:
            test=False
            break
    if test:
        c=0
        pos.append((x,y))
        amount+=1
    if c==50000:
        break
n=len(pos)
def create_point(xa,ya,col):
    """Fonction pour placer un disque de couleur 'col' à la coordonnée (xa,ya)"""
    disque = canvas.create_oval(xa-(rayon),ya-(rayon),xa+(rayon),ya+(rayon),fill="white",outline=col)
    return disque

def create_mark(xa,ya,col):
    """Fonction pour placer un petit marquer de couleur 'col' à la coordonnée (xa,ya)"""
    disque = canvas.create_oval(xa-2,ya-2,xa+2,ya+2,fill=col,outline=col)
    return disque


"""Création du quadrillage                              |   |  <- Pixels inclus           
On a un rectangle noir de 1000x500                      | O |      
on veut créer un quadrillage avec cases de coté 4*r     |   |  <- Pixels exclus
Un quadrillage est représenté par un couple de coordonnés (x,y)
tel que x,y soit le point en haut à gauche du quadrillage
"""
cote = 4*rayon
nbr_cases_x = int(999/cote)   #Si on est censé avoir PILE le nombre de case pour rentrer parfaitement,
                              #on enlève la dernière et on la rajoute après dans la boucle,
                              #sinon, on aura une case plus petite que prévu, mais jamais une case trop grande
nbr_cases_y = int(499/cote)
cases = {}   #Dictionnaire cases:  {(x_coin,y_coin):[liste des disques dont\
                                   # le centre est dans la case],...}
distances = {}  
for i in range(nbr_cases_x+1):
    for j in range(nbr_cases_y+1):
        cases[i*cote+100,j*cote+200] = []                   


def id_case(x,y):
    """Prend un couple de coordonnées (x,y) et retourne le couple (a,b)
    tel que le point représenté par (x,y) soit dans la case de coin
    haut-gauche de coordonnés (a,b)"""
    try:
        assert (100<x<1100 and 200<y<700)
        a=int((x-100)/cote)*cote+100
        b=int((y-200)/cote)*cote+200
        return (a,b)
    except AssertionError:
        raise ValueError
        print(x,y)
        print("Le couple à identifier n'est pas dans le rectangle")

def add_list(ens,liste):
    return ens.__or__(set(liste))



def C(v):
    """Fonction qui renvoie les disques qui le touchent directement
    Prend en argument un disque
    Retourne l'ensemble des disques à son contact / ensemble vide si aucun"""
    to_return = set()
    x,y = l[v][0],l[v][1]
    a,b = id_case(x,y)   #on récupère la case où se trouve le disque qu'on test
    voisinage = set(cases[a,b])  #on récupère la liste du voisinage (pas forcément contact)
    #4         On imagine un disque à la case 4
    #012
    #345       Donc on regarde dans tous les cases de 0 à 9
    #678    
    if a>100: #On n'est pas sur les cases tout à gauche
        voisinage = add_list(voisinage,cases[a-4*rayon,b])  #3
        if b>200:
            voisinage = add_list(voisinage,cases[a-4*rayon,b-4*rayon]) #0
            voisinage = add_list(voisinage,cases[a,b-4*rayon]) #1
        if b<600:
            voisinage = add_list(voisinage,cases[a-4*rayon,b+4*rayon])  #6
            voisinage = add_list(voisinage,cases[a,b+4*rayon])  #7
    if a<1100-4*rayon: #Pas tout à droite
        voisinage = add_list(voisinage,cases[a+4*rayon,b]) #5
        if b>200:
            voisinage = add_list(voisinage,cases[a+4*rayon,b-4*rayon]) #2
            voisinage = add_list(voisinage,cases[a,b-4*rayon]) #1
        if b<600:
            voisinage = add_list(voisinage,cases[a+4*rayon,b+4*rayon]) #8
            voisinage = add_list(voisinage,cases[a,b+4*rayon])  #7
    
    epsilon = 10  #nombre de pixels représentant la distance entre 2 disques
                  #tels qu'ils forment un amas
    
    
    #On ajoute plusieurs fois le même à un ensemble -> pas grave
    for i in voisinage:
        xb,yb = l[i][0],l[i][1]
        if sqrt((x-xb)**2+(y-yb)**2)<2*rayon+epsilon:
            to_return.add(i)
    return to_return


def get_k_min(L,k):
    #renvoie la liste des k plus petits nombres de L tries par ordre croissant
    S = deepcopy(L)
    n=len(S)
    k=min(k,n)
    indexs=[None for i in range(k)]
    mins=[]
    for i in range(n):
        x=L[i]
        c=0
        while c<k and (indexs[c]==None or x>=L[indexs[c]]):
            if indexs[c]==None:
                indexs[c]=i
                c=k
                break
            c+=1
        if c<k:
            z=i
            while c<k:
                y=indexs[c]
                indexs[c]=z
                c+=1
                z,y=y,z
    for i in range(k):
        try:
            mins.append(L[indexs[0]])
        except TypeError:
            print(L,k)
            break
        del indexs[0]
    return mins
    
    

def T(v):
    """Fonction qui prend en argument un disque
    Qui renvoie tous les disques en son contact direct ou non
    (le contact du contact du contact ... est renvoyé)"""
    to_return = {}    #renvoie le dictionnaire {indice du contact (0 -> direct / sinon -> plus ou moins direct) : set({disque})}  
    Cv = set(C(v)) #Initialisation: contact direct de v
    Tv = set(Cv)   #de même, contact direct de v
    
    #Cv: groupe de contact direct actuel
    #Tv: ensemble de tous les contacts (in)directs déjà déterminés
    i=0 #Indice de contact
    while Cv != set(): #On ajoute les contacts des contacts de manière récursive
        to_return[str(i)]=Cv #Groupe de contact à l'indice i
        new_Cv = set() #Ensemble de groupe de contact d'indice  i+1
        for j in Cv: #On regarde tout le groupe d'indice i
            new_Cv= new_Cv.__or__(C(j).__sub__(Tv.__or__(set(j).__or__({v}))))
            #Et on ajoute les contacts directs de i à i+1 sauf ceux des k<=i
        Tv = Tv.__or__(new_Cv) #On ajoute les nouveaux contacts à Tv
        Cv = new_Cv #Et on réinitialise Cv pour l'itération suivante
        i+=1 #ET on incrémente l'indice de contact
    return to_return
    

for i in range(len(pos)):
    x,y=pos[i][0],pos[i][1]
    d=create_point(x,y,"black")
    vmax=1
    v=vmax
    case = id_case(x,y)
    a,b = case[0],case[1]
    distance = sqrt((x-xt)**2+(y-yt)**2)
    distances[str(i)]=distance
    cases[a,b].append(str(len(l)))
    moves[str(len(l))]=[(x,y)]
    #Pour avoir des cibles en fonction du disque, on pourra créer une fonction
    #qui à une case donnée (un couple) associe le point à atteindre (couple)
    # <=> champ vectoriel des vitesse
    
    
    #x, y, vx, vy, rayon, vmax, temps, disque_canvas, x_to_reach, y_to_reach,
    #v_contraintes_x,v_contraintes_y, case,distance_sortie
    l[str(len(l))]=[x,y,0,0,rayon,vmax,0,d,xt,yt,0,0,case,distance]

def scalaireAB_AD(xa,ya,xb,yb,xd,yd):
        scal = (xb-xa)*(xd-xa)+(yb-ya)*(yd-ya)
        return scal
def projete(xV,yV,xB,yB,xA,yA):  #projeté de (xV,yV) sur la droite (xA,yA)-(xB,yB)
    rapport = scalaireAB_AD(xB,yB,xA,yA,xV,yV)/scalaireAB_AD(xB,yB,xA,yA,xA,yA)
    xH = rapport*(xA-xB) + xB
    yH = rapport*(yA-yB) + yB
    return [xH,yH]
    
def zone_sortie(x,y):
    #renvoie un boolean indiquant si le disque en (x,y) peut sortir
    #eclipse centree en xt,yt, de demi petit axe 50, de demi grand axe 60
    
    #definition de l'ellipse:
    a=50
    if rayon==20:
        b=35
    elif rayon==10:
        b=25
    
    if (x/b)*(x/b)+(y/a)*(y/a)==1 or (y==yt and x-xt<=b):
        return True
    else:
        if x-xt>b:
            return False
        else:
            xi=xt+(a*((x-xt)/abs(y-yt)))/sqrt(1+(a*a/(b*b))*((x-xt)/(y-yt))**2)
            delta_y=a*sqrt(b*b-(xt-xi)*(xt-xi))/b
            if y>yt:
                yi=yt+delta_y
            else:
                yi=yt-delta_y
            return (x-xt)*(xi-x)+(y-yt)*(yi-y)>0
        
        
def barycentre(L):
    """Fonction qui prend en argument une liste d'indices de disques et
    retourne le tuple (x,y) des coordonnées du barycentre
    """
    try:
        sum_x = sum([l[i][0] for i in L])
        sum_y = sum([l[i][1] for i in L])
    except:
        for i in L:
            if not i in l.keys():
                L.remove(i)
                sum_x = sum([l[i][0] for i in L])
                sum_y = sum([l[i][1] for i in L])
                
                    
    taille = len(L)
    return (sum_x/taille,sum_y/taille)
    

def new_cout(f):
    """
    parametres interessants:
        - distance moyenne a la sortie
        - si on est excentre et proche de la sortie, c'est bien de se recentrer
    """
    d_moy=sum([((i[0]-xt)**2+(i[1]-yt)**2)**1/2 for i in f])
    #pour le centrage, on calcule la somme des valeurs absolues des angles
    #disque - sortie - horizontale
    #et on renvoie directement cette somme
    a_moy=3000*sum([abs(atan((i[1]-yt)/(i[0]-xt))) for i in f])
    nbr_sortis=sum([zone_sortie(i[0],i[1]) for i in f])
    return d_moy+a_moy+1000*(10-nbr_sortis)
    
    
def deplacement_possible(xa,ya,x,y,individu,sortis,indice):
    #un disque d'indice 'indice', à la base en position (xa,ya) cherche
    #à se déplacer à la position (x,y), sachant qu'il fait partie de
    #l'individu 'individu' en cours de calcul
    sort_fam = individu
    if x<100+rayon or x>1100-rayon or y<200+rayon or y>700-rayon:
        return False
    to_return = set()
    try:
        (a,b)=id_case(x,y)
    except ValueError:
        return False
    voisinage = set(cases[a,b])
    if a>100:
        voisinage = add_list(voisinage,cases[a-4*rayon,b])
        if b>200:
            voisinage = add_list(voisinage,cases[a-4*rayon,b-4*rayon])
            voisinage = add_list(voisinage,cases[a,b-4*rayon])
        if b<600:
            voisinage = add_list(voisinage,cases[a-4*rayon,b+4*rayon])
            voisinage = add_list(voisinage,cases[a,b+4*rayon])
    if a<1100-4*rayon:
        voisinage = add_list(voisinage,cases[a+4*rayon,b])
        if b>200:
            voisinage = add_list(voisinage,cases[a+4*rayon,b-4*rayon])
            voisinage = add_list(voisinage,cases[a,b-4*rayon])
        if b<600:
            voisinage = add_list(voisinage,cases[a+4*rayon,b+4*rayon])
            voisinage = add_list(voisinage,cases[a,b+4*rayon])
    for i in voisinage:
        xb,yb = l[i][0],l[i][1]
        if i in sort_fam or i==indice:
            continue
        if sqrt((x-xb)**2+(y-yb)**2)<2*rayon:
            to_return.add((xb,yb))
    for j in sort_fam:
        try:
            if sqrt((j[0]-x)**2+(j[1]-y)**2)<2*rayon and indice!=j[2] and not(j in sortis):
                to_return.add(j)
        except IndexError:
            pass
    return (to_return==set())    



    
class move(Thread):
    def run(self):
        global running,to_write
        changed = True
        tour = 0
        l_amas = []
        while running:
            while len(l)!=0 and changed and tour<125 and time()-TEMPS<12000:
                #¶print(len(l),tour)
                if tour%100==0 and pause: print("TOUR",tour)
                """   LISTE VALEUR DU DICO DES DISQUES
                #x, y, vx, vy, rayon, vmax, temps, disque_canvas, x_to_reach, y_to_reach,
                #v_contraintes_x,v_contraintes_y, case,distance_sortie
                l[str(len(l))]=[x,y,0,0,rayon,vmax,0,d,xt,yt,0,0,case,distance,vxc,vyc]            
                """
                #liste_disques = [i for i in l.keys()]   #Liste des indices de tous les disques
                changed = False
                liste_disques=sorted(l,key=lambda x:l[x][13])
                
                to_iterate = list(l.keys())
                for j in to_iterate:
                        x,y=l[j][0],l[j][1]
                        if x<100+rayon+15:
                            xi=x
                            sgn=1-2*(y>yt)
                            for k in range(60,1,-5):
                                yi=y+sgn*k
                                if deplacement_possible(x,y,xi,yi,[],[],j):
                                    xo,yo=deepcopy(l[j][0]),deepcopy(l[j][1])
                                    l[j][0]=xi
                                    l[j][1]=yi
                                    x,y = l[j][0],l[j][1]
                                    l[j][13]=sqrt((x-xt)**2+(y-yt)**2)
                                    cases[id_case(xo,yo)].remove(j)
                                    cases[id_case(x,y)].append(j)
                                    #on met à jour les coordonnées dans le dictionnaire et sur l'affichage
                                    #Et on replace le disque à la bonne case du quadrillage
                                    
                                    canvas.coords(l[j][7],x-rayon,y-rayon,x+rayon,y+rayon)
                                    changed=True
                                    if zone_sortie(x,y):   #on regarde si le disque
                                        #est proche de la sortie
                                        if pause: print("out")
                                        cases[id_case(x,y)].remove(j)
                                        canvas.coords(l[j][7],-200,-200,-200,-200)
                                        del l[j]
                                        liste_disques.remove(j)
                                    moves[j].append((x,y))
                                    to_write+="("+str(j)+","+str(x)+","+str(y)+"),"
                                    sleep(0.01)
                                    break
                        else:
                            pente=(y-yt)/(x-xt)
                            ordo = yt-pente*xt
                            k=0
                            while k<2*rayon+5:
                                xi = x-k
                                yi=pente*xi+ordo
                                if (not(deplacement_possible(x,y,xi,yi,[],[],j)) or k==2*rayon) and k>0:
                                    if k<2*rayon:
                                        k-=5
                                        xi = x-k
                                        yi=pente*xi+ordo
                                    if k==0: break
                                    if not(deplacement_possible(x,y,xi,yi,[],[],j)): break
                                    xo,yo=deepcopy(l[j][0]),deepcopy(l[j][1])
                                    xi,yi=int(xi),int(yi)
                                    l[j][0]=xi
                                    l[j][1]=yi
                                    x,y = l[j][0],l[j][1]
                                    l[j][13]=sqrt((x-xt)**2+(y-yt)**2)
                                    cases[id_case(xo,yo)].remove(j)
                                    cases[id_case(x,y)].append(j)
                                    #on met à jour les coordonnées dans le dictionnaire et sur l'affichage
                                    #Et on replace le disque à la bonne case du quadrillage
                                    
                                    canvas.coords(l[j][7],x-rayon,y-rayon,x+rayon,y+rayon)
                                    if x!=xo or y!=yo:
                                        changed = True  #un disque bouge => la boucle continue
                                    if zone_sortie(x,y):   #on regarde si le disque
                                        #est proche de la sortie
                                        if pause:print("out")
                                        cases[id_case(x,y)].remove(j)
                                        canvas.coords(l[j][7],-200,-200,-200,-200)
                                        del l[j]
                                        liste_disques.remove(j)
                                    moves[j].append((x,y))
                                    to_write+="("+str(j)+","+str(x)+","+str(y)+"),"
                                    sleep(0.01)
                                    break
                                else:
                                    k+=5
                                
                
                #Détermination des amas
                
                while liste_disques!=[]: #LE FOR I IN LISTE_DISQUES NE MARCHE PAS CAR LISTE MODIFIEE
                    i=liste_disques[0]
                    Tv = T(i) #On calcule le voisinage indirect de chaque disque, 1 par 1
                    #Tv[niveau]={disques_au_niveau_i}
                    amas = []
                    taille_max=10
                    for j in Tv.values(): #Pour tous les disques de ce voisinage, on ajoute
                        if len(amas)==taille_max: break
                        for k in j:       #ces disques à l'amas
                            if k in liste_disques:
                                amas.append(k)                                    
                                liste_disques.remove(k)
                                if len(amas)==taille_max:
                                    break
                    try:
                        liste_disques.remove(i)
                    except ValueError:
                        pass
                    l_amas.append(amas)  #On remplit l_amas des amas de chaque disque
                    #print(amas,"\nrestants:",liste_disques,"\n")
                
                for i in l_amas:
                    if not(running):
                        exit()
                    G = barycentre(i)                    
                    xg,yg=G[0],G[1]
                    #On calcule le mouvement du barycentre comme celui d'un gros disque
                    #qui ne serait gêné par rien
                    try:
                        assert xt!=xg
                        pente = (yt-yg)/(xt-xg)
                    except AssertionError:
                        pente = 0  #cas impossible, car il serait dans le mur
                    if len(i)==1:
                        epsilon = 2*rayon+5  #deplacement en pixel  (1 n'est pas forcÃ©ment le min)
                    else:
                        epsilon = 20
                    delta_x = abs(epsilon/sqrt(1+pente**2))
                    try:
                        assert xt!=xg
                        delta_y = abs((xi-xg)*(yt-yg)/(xt-xg))
                    except AssertionError:
                        delta_y = epsilon
                        delta_x=0
                    if xg>xt:
                        xi = xg-delta_x
                    else:
                        xi=xg+delta_x
                    if yg>yt:
                        yi = int(yg-delta_y)
                    else:
                        yi = int(yg+delta_y)
                    if len(i)==1 and deplacement_possible(l[i[0]][0],l[i[0]][1],xi,yi,[],[],i[0]):
                        j=i[0]
                        xi,yi=int(xi),int(yi)
                        xo,yo=deepcopy(l[j][0]),deepcopy(l[j][1])
                        l[j][0]=xi
                        l[j][1]=yi
                        x,y = l[j][0],l[j][1]
                        l[j][13]=sqrt((x-xt)**2+(y-yt)**2)
                        cases[id_case(xo,yo)].remove(j)
                        cases[id_case(x,y)].append(j)
                        #on met à jour les coordonnées dans le dictionnaire et sur l'affichage
                        #Et on replace le disque à la bonne case du quadrillage
                        canvas.coords(l[j][7],x-rayon,y-rayon,x+rayon,y+rayon)
                        if x!=xo or y!=yo:
                            changed = True  #un disque bouge => la boucle continue
                        if zone_sortie(x,y):   #on regarde si le disque
                            #est proche de la sortie
                            if pause:print("out")
                            cases[id_case(x,y)].remove(j)
                            canvas.coords(l[j][7],-200,-200,-200,-200)
                            del l[j]
                        moves[j].append((x,y))
                        to_write+="("+str(j)+","+str(x)+","+str(y)+"),"
                        continue
                    
                                
                    
                    
                    #(xi,yi) = coordonnées du nouveau barycentre après
                    #s'être déplacé vers la sortie (sans contrainte)
                    y=6 #nombre d'itérations de calcul de k familles
                    #y=nombre de generations
                    to_save = []
                    new_fam = [[(l[s][0],l[s][1],s) for s in i]]
                    not_moved = deepcopy(new_fam)
                    
                    
                    if len(i)>1:
                        for p in range(y): #Nombre d'étapes qu'on fait (de generations)
                            k = 70 #nombre de nouvelles coordonnées calculées pour chaque disque à chaque nouvelle famille pour chaque amas
                            #nombre d'individus pour chaque génération
                            notes = []
                            #print("FIRST_EVER:",new_fam)
                            for s in new_fam:  #On prend les amas (s=une liste de coordonnées (tuples))
                                famille=[[] for i in range(k)]
                                sortis=[]
                                for c in range(k):
                                    old=[]
                                    for d in s: 
                                        if not(running):
                                            exit()
                                        xa,ya =d[0],d[1]
                                        sorti=False
                                        for m in sortis:
                                            if d[2]==m[2]:
                                                sorti=True
                                                famille[c].append((m[0],m[1],d[2]))
                                        if not sorti and zone_sortie(xa,ya):
                                            sortis.append((xa,ya,d[2]))
                                            famille[c].append((xa,ya,d[2]))
                                            continue
                                        if sorti:
                                            continue
                                        old.append(d)
                                        
                                        scale = int(max(15,20*exp(-0.05*len(s))))   
                                        #scale=50
                                        
                                        possibles = [(xa,ya,d[2])]
                                        xo,yo=xa-int((4*scale)/5),ya-scale
                                        """
                                        on suppose que les disques ne se deplacent pas
                                        en prevoyant le mouvement des autres
                                        ainsi, deplacement_possible ne prend pas en compte
                                        les mouvements qui sont en train d'etre calcules,
                                        mais ceux du tour precedent
                                        """
                                        pc=5
                                        for a in range(int(scale/pc)+1):
                                            if sorti: break
                                            for j in range(int(scale/pc)+1):
                                                if deplacement_possible(xa,ya,xo+pc*a,yo+2*pc*j,s+famille[c],sortis,d[2]):
                                                    possibles.append((xo+pc*a,yo+2*pc*j,d[2]))
                                                    if zone_sortie(xo+pc*a,yo+2*pc*j):
                                                        possibles=[(xo+pc*a,yo+2*pc*j,d[2])]
                                                        sorti=True
                                                        break
                                        taille = len(possibles)
                                        chosen = randint(0,taille-1)
                                        if sorti:
                                            sortis.append(possibles[chosen])
                                        old.append(possibles[chosen])
                                        famille[c].append(possibles[chosen])
                                        
                                        
                                    
                                for j in famille:
                                    if pause:
                                        for m in j:
                                            x,y,q=m
                                            r=l[q][7]
                                            canvas.coords(r,x-rayon,y-rayon,x+rayon,y+rayon)
                                            canvas.itemconfig(r,fill="red")
                                        sleep(.1)
                                        for m in j:
                                            x,y,q=m
                                            x,y=l[q][0],l[q][1]
                                            r=l[q][7]
                                            canvas.itemconfig(r,fill="white")
                                            canvas.coords(r,x-rayon,y-rayon,x+rayon,y+rayon)
                                            
                                    if j!=[]:
                                        notes.append((new_cout(j),j))
                                        
                                mins=get_k_min(notes,4)
                                to_save.extend(mins)
                                
                                
                                
                            saved = get_k_min(to_save,4)
                            new_fam=[saved[0][1],saved[1][1],saved[2][1],saved[3][1]]
                            
                            
                            
                        select = new_fam[randint(0,len(new_fam)-1)]
                        new_fam=select
                        a = new_cout(not_moved[0])
                        b=new_cout(select)
                        if pause:
                            print("test0",a,b,select)
                            print("test1",not_moved[0])
                            for j in select:
                                x,y,k = j
                                s=l[k][7]
                                canvas.itemconfig(s,fill="red")
                            sleep(1)
                            for j in select:
                                x,y,k=j
                                s=l[k][7]
                                canvas.coords(s,x-rayon-2,y-rayon-2,x+rayon+2,y+rayon+2)
                            sleep(1)
                            for j in select:
                                x,y,k = j
                                xo,yo=l[k][0],l[k][1]
                                s=l[k][7]
                                canvas.coords(s,xo-rayon,yo-rayon,xo+rayon,yo+rayon)
                                canvas.itemconfig(s,fill="white")
                                
                        if a<b:
                            #on n'a pas trouve mieux
                            select = not_moved[0]
                        index = 0
                        for j in i:
                            canvas.itemconfig(l[j][7],outline="gold",width=5)
                            if pause: sleep(1)
                            xo,yo=deepcopy(l[j][0]),deepcopy(l[j][1])
                            l[j][0]=select[index][0]
                            l[j][1]=select[index][1]
                            x,y = l[j][0],l[j][1]
                            l[j][13]=sqrt((x-xt)**2+(y-yt)**2)
                            index+=1
                            cases[id_case(xo,yo)].remove(j)
                            cases[id_case(x,y)].append(j)
                            #on met à jour les coordonnées dans le dictionnaire et sur l'affichage
                            #Et on replace le disque à la bonne case du quadrillage
                            canvas.coords(l[j][7],x-rayon,y-rayon,x+rayon,y+rayon)
                            canvas.itemconfig(l[j][7],outline="black",width=1)
                            if x!=xo or y!=yo:
                                changed = True  #un disque bouge => la boucle continue
                            if zone_sortie(x,y):   #on regarde si le disque
                                #est proche de la sortie
                                if pause:print("out")
                                cases[id_case(x,y)].remove(j)
                                canvas.coords(l[j][7],-200,-200,-200,-200)
                                del l[j]
                            moves[j].append((x,y))
                            to_write+="("+str(j)+","+str(x)+","+str(y)+"),"
                        
                l_amas = []
                tour+=1
            print("OVER")
            print(time()-TEMPS)
            with open("coordonnees.txt","wb") as writing:
                write = pickle.Pickler(writing)
                write.dump(moves)
            with open("coords.txt","w") as file:
                file.write(to_write)
            running=False
            
                       
def ClickScreen(event):
    x=event.x
    y=event.y   
    create_mark(x,y,"red")
    print("COORDS",x,y)
    print(deplacement_possible(x,y,x,y,[],[],0))        
            
            

move().start()

canvas.bind("<Button-1>",ClickScreen)

fen.mainloop()
running=False
move()._stop()