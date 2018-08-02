from tkinter import *
from math import pi,cos,sin,sqrt
from threading import Thread
from random import randint
from copy import deepcopy
import pickle
from sys import exit



"""
Si une partie de l'amas est bloquée, l'autre partie ne doit pas être collée à celle bloquée
donc privilégier le fait qu'un amas reste tel quel n'est pas nécessairement toujours bénéfique

Au moment de regarder les coordonnées possibles, peut-être positionner le centre du carré
de recherches au niveau du barycentre du groupe, ou au moins essayer de garder une cohérence
générale dans l'amas (les disque à droite d'un amais resteraint à droite),
donc essayer de positionner le centre de recherches au niveau d'un point de coordonnées
qui correspondrait à une translation parallèle au celle du barycentre
à partir du point de départ du disque considéré
ex:
    si le barycentre fait -50x et +20y
    et qu'on veut bouger le disque en coordonnées x,y=a,b
    on va placer le centre en x=a-50 et y=b+20

-> cohérence globale, permet de débloquer un amas si le reste est bloqué

Revoir la fonction de coût
car si une partie de l'amas est bloquée, un partie non bloquée, pour se libérer, devra s'éloigner
du barycentre, donc prendre une poistion moins optimale selon la fonction actuelle.


Dans le dernier calculé, cas très simple, un disque se bloque directement à côté
de la sortie -> nécessité d'affiner la zone de recherche ou de trouver une autre
possibilité si celle ci ne fonctionne pas

"""

running = True

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


with open("coordonnees.txt","wb") as writing:
    write = pickle.Pickler(writing)
    write.dump(moves)

pos=[]
c=0
while 1:
    c+=1
    x,y = randint(100+rayon,1100-rayon),randint(200+rayon,700-rayon)
    test = True
    for i in pos:
        if sqrt((x-i[0])**2+(y-i[1])**2)<2*rayon:
            test=False
    if test:
        c=0
        pos.append((x,y))
    if c==1:
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


def get_k_max(L,k):
    S = deepcopy(L)
    maxs=[]
    for i in range(k):
        a=max(S)
        maxs.append(a)
        S.remove(a)
    return maxs
    
    

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
            new_Cv= new_Cv.__or__(C(j).__sub__(Tv.__or__(set(j))))
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
    

def barycentre(L):
    """Fonction qui prend en argument une liste d'indices de disques et
    retourne le tuple (x,y) des coordonnées du barycentre
    """
    sum_x = sum([l[i][0] for i in L])
    sum_y = sum([l[i][1] for i in L])
    taille = len(L)
    return (sum_x/taille,sum_y/taille)
    

def fct_cout(f_n,f_n1,G):
    """
    f_n est une liste de tuples de coordonnées
    Fonction qui prend en argument une famille de coordonnées f_n1
    (coordonnées sous la forme de tuples (x,y)) et le barycentre 
    de l'amas après déplacement de ce barycentre
    Retourne un float qui caractérise la qualité de la famille f_n1
    float augmente <=> qualité augmente
    """
    try:
        Gn_x = sum([i[0] for i in f_n])
        Gn_y=sum([i[1] for i in f_n])
        Gn1_x = G[0] #G est le barycentre déplacé de l'amas
        Gn1_y=G[1]   #Correspond au point à atteindre au plus proche
    except TypeError:
        print(f_n,f_n1)
    #On veut les résultats le:
    dist_G = sum([(i[0]-Gn1_x)**2+(i[1]-Gn1_y)**2 for i in f_n1]) #Plus petit possible
    dist_S = sum([(i[0]-xt)**2+(i[1]-yt)**2 for i in f_n1])  #Plus petit possible
    d_Gn_Gn1 = (Gn_x-Gn1_x)**2+(Gn_y-Gn1_y)**2  #plus grand possible
    try:
        return d_Gn_Gn1/(dist_G*dist_S)
    except ZeroDivisionError:
        return 99999
    
    
    
def deplacement_possible(xa,ya,x,y,famille_n,indice):
    sort_fam = []
    for i in famille_n:
        sort_fam.extend(i)
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
        test=False
        xb,yb = l[i][0],l[i][1]
        if sqrt((x-xb)**2+(y-yb)**2)<2*rayon and xb!=xa and yb!=ya and i!=indice and (xb,yb) not in sort_fam:
            test=True
        if test:
            to_return.add((xb,yb))
    for j in sort_fam:
        test=False
        try:
            if sqrt((j[0]-x)**2+(j[1]-y)**2)<2*rayon and j[0]!=xa and j[1]!=ya and indice!=j[2]:
                test=True
        except IndexError:
            pass
        if test:
                to_return.add(j)
    """if famille_n ==[] and to_return == set():
        create_point(x,y,"red")
        create_mark(xa,ya,"blue")
        create_mark(x,y,"red")
        print(a,b)
        create_mark(a,b,"black")
        for i in voisinage:
            xb,yb = l[i][0],l[i][1]
            if i!=indice:
                create_mark(xb,yb,"yellow")
        exit()"""
    return (to_return==set())    
        
    
class move(Thread):
    def run(self):
        global running
        changed = True
        tour = 0
        l_amas = []
        Coordonnees = []
        while running:
            while len(l)!=0 and changed and tour<100000:
                print(len(l),tour)
                """   LISTE VALEUR DU DICO DES DISQUES
                #x, y, vx, vy, rayon, vmax, temps, disque_canvas, x_to_reach, y_to_reach,
                #v_contraintes_x,v_contraintes_y, case,distance_sortie
                l[str(len(l))]=[x,y,0,0,rayon,vmax,0,d,xt,yt,0,0,case,distance,vxc,vyc]            
                """
                liste_disques = [i for i in l.keys()]   #Liste des indices de tous les disques
                changed = False
                #Détermination des amas
                
                while liste_disques!=[]: #LE FOR I IN LISTE_DISQUES NE MARCHE PAS CAR LISTE MODIFIEE
                    i=liste_disques[0]
                    Tv = T(i) #On calcule le voisinage indirect de chaque disque, 1 par 1
                    amas = []
                    for j in Tv.values(): #Pour tous les disques de ce voisinage, on ajoute
                        for k in j:       #ces disques à l'amas
                            amas.append(k)
                            try:
                                liste_disques.remove(k) #On enlève les disques déjà dans des amas
                                                        #Sinon on se retrouve avec plusieurs fois le même
                            except ValueError:
                                """create_mark(l[k][0],l[k][1],"red")
                                print("i:",i,"Voisinage_i:",Tv,"k:",k,"\ndisques restants",liste_disques,
                                      "\namas courant",amas,"\nAmas totaux",l_amas)"""
                                pass
                    l_amas.append(amas)  #On remplit l_amas des amas de chaque disque
                    #print(amas,"\nrestants:",liste_disques,"\n")
                    
                """for i in l_amas:                
                    for j in i:
                        canvas.create_line(l[j][0],l[j][1],
                        l[i[0]][0],l[i[0]][1],width=1)"""
                
                
                for i in l_amas:
                    #print(len(l_amas),l_amas.index(i))
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
                        pente = 0
                    if len(i)==1:
                        epsilon = 60  #dÃ©placement en pixel  (1 n'est pas forcÃ©ment le min)
                    else:
                        epsilon = 20
                    try:
                        assert abs(pente) != 1
                        delta_x = abs(epsilon/sqrt(1+pente**2))
                    except AssertionError: #triangle rectangle de cotÃ© 1 1 sqrt(2)
                        delta_x = 1
                    if xg>xt:
                        xi = xg-delta_x
                    else:
                        xi=xg+delta_x
                    try:
                        assert xt!=xg
                        delta_y = abs((xi-xg)*(yt-yg)/(xt-xg))
                    except AssertionError:
                        delta_y = 1
                    if yg>yt:
                        yi = int(yg-delta_y)
                    else:
                        yi = int(yg+delta_y)
                    create_mark(xi,yi,"yellow")
                    if len(i)==1 and deplacement_possible(l[i[0]][0],l[i[0]][1],xi,yi,[],i[0]):
                        j=i[0]
                        xo,yo=deepcopy(l[j][0]),deepcopy(l[j][1])
                        l[j][0]=xi
                        l[j][1]=yi
                        x,y = l[j][0],l[j][1]
                        cases[id_case(xo,yo)].remove(j)
                        cases[id_case(x,y)].append(j)
                        #on met à jour les coordonnées dans le dictionnaire et sur l'affichage
                        #Et on replace le disque à la bonne case du quadrillage
                        canvas.coords(l[j][7],x-rayon,y-rayon,x+rayon,y+rayon)
                        if x!=xo or y!=yo:
                            changed = True  #un disque bouge => la boucle continue
                        else:
                            print("fuck")
                        if sqrt((x-xt)**2+(y-yt)**2)<50:   #on regarde si le disque
                            #est proche de la sortie
                            print("out")
                            cases[id_case(x,y)].remove(j)
                            canvas.coords(l[j][7],-200,-200,-200,-200)
                            del l[j]
                        moves[j].append((x,y))
                        continue
                        
                    
                    
                    
                    #(xi,yi) = coordonnées du nouveau barycentre après
                    #s'être déplacé vers la sortie (sans contrainte)
                    y=7 #nombre d'itérations de calcul de k familles
                    to_save = []
                    to_keep=[]
                    new_fam = [[(l[s][0],l[s][1],s) for s in i]]
                    for p in range(y): #Nombre d'étapes qu'on fait
                        #print("test")
                        k = 8 #nombre de nouvelles coordonnées calculées pour chaque disque à chaque nouvelle famille pour chaque amas
                        famille=[[] for i in range(k)]
                        notes = []
                        for s in new_fam:  #On prend les amas (s=une liste de coordonnées (tuples))
                            for c in range(k):
                                for d in s:                 
                                    if not(running):
                                        exit()
                                    xa,ya =d[0],d[1]
                                    scale = max(20-3*len(s),5)
                                    """eps_x= randint(0,scale)
                                    eps_y= randint(0,scale)
                                    sgn_y=0
                                    if ya>yt:
                                        sgn_y=1                                    
                                    x,y=xa-eps_x,ya+((-1)**(sgn_y))*eps_y
                                    attempts = 0
                                    while not(deplacement_possible(xa,ya,x,y,famille,d[2])) and attempts<20:
                                        eps_x= randint(0,scale)
                                        eps_y= randint(0,scale)                            
                                        x,y=xa-eps_x,ya+((-1)**(sgn_y))*eps_y
                                        attempts+=1
                                    if attempts == 20:
                                        #create_mark(xa,ya,"red")
                                        famille[c].append((xa,ya,d[2]))                                
                                    else:
                                        famille[c].append((x,y,d[2])) #On ajoute des nouvelles coordonnées
                                    #pour le disque d'indice c"""
                                    possibles = []
                                    xo,yo=xa-scale,ya-scale
                                    
                                    for a in range(int(scale/2)):
                                        for j in range(int(scale/2)):
                                            if deplacement_possible(xa,ya,xo+2*a,yo+4*j,famille,d[2]):
                                                possibles.append((xo+2*a,yo+4*j,d[2]))
                                    taille = len(possibles)
                                    if taille!=0:
                                        famille[c].append(possibles[randint(0,taille-1)])
                                    else:
                                        famille[c].append((xa,ya,d[2]))
                            if p==0:
                                to_keep.append(famille[0])
                                to_keep.append(famille[1])
                                to_keep.append(famille[2])
                            for j in famille:
                                if j!=[]:
                                    notes.append((fct_cout(s,j,(xi,yi)),j))
                            for j in new_fam:
                                if j!=[]:
                                    notes.append((fct_cout(s,j,(xi,yi)),j))
                            maxs=get_k_max(notes,2)
                            """print("FAMILLE:",famille)
                            print("NEW_FAM:",new_fam)
                            print("MAXS:",maxs)
                            print("NOTES:",notes)"""
                            to_save.append((maxs[0][0],maxs[0][1]))
                            to_save.append((maxs[1][0],maxs[1][1]))
                        
                        saved = get_k_max(to_save,2)
                        """print("SAVED:",saved)
                        print("TO_SAVE:",to_save)"""
                        new_fam=[saved[0][1],saved[1][1]]
                        new_fam.extend(to_keep)
                    select = new_fam[randint(0,len(new_fam)-1)]
                    new_fam=select
                    index = 0
                    #print(i,select)
                    for j in i:
                        xo,yo=deepcopy(l[j][0]),deepcopy(l[j][1])
                        l[j][0]=select[index][0]
                        l[j][1]=select[index][1]
                        x,y = l[j][0],l[j][1]
                        index+=1
                        cases[id_case(xo,yo)].remove(j)
                        cases[id_case(x,y)].append(j)
                        #on met à jour les coordonnées dans le dictionnaire et sur l'affichage
                        #Et on replace le disque à la bonne case du quadrillage
                        canvas.coords(l[j][7],x-rayon,y-rayon,x+rayon,y+rayon)
                        if x!=xo or y!=yo:
                            changed = True  #un disque bouge => la boucle continue
                        else:
                            print("fuck")
                        if sqrt((x-xt)**2+(y-yt)**2)<50:   #on regarde si le disque
                            #est proche de la sortie
                            print("out")
                            cases[id_case(x,y)].remove(j)
                            canvas.coords(l[j][7],-200,-200,-200,-200)
                            del l[j]
                        moves[j].append((x,y))
                        
                l_amas = []
                tour+=1
            print("OVER")
            with open("coordonnees.txt","wb") as writing:
                write = pickle.Pickler(writing)
                write.dump(moves)
            running=False
                        
            """
                     DANS LA BOUCLE DEPLACEMENT POSSIBLE POUR TESTER TOUTES LES POSSIBILITES
                     LA PREMIERE COORDONNEES CALCULEE EST EN GENERAL POSSIBLE
                     DONC ON L'AJOUTE A LA FAMILLE
                     MAIS DES QU'ON VEUT CALCULER LA 2EME COORDONNEES
                     ALORS LA PREMIERE CALCULEE EST DANS LA FAMILLE
                     DONC ON N'ARRIVE JAMAIS A POSITIONNER UN DISQUE QUI NE SOIT PAS SUPPERPOSE
                     AU PREMIER CALCULE
                     DONC ON SE RETROUVE TOUJOURS DANS LE CAS ATTEMPTS=20
                     D'OU LE BUG
            """
                    
                        
                        
                            
                    
                    
                    #On calcule k nouvelles listes de disques (équivalentes à new_fam[0])
                    #qui "remplaceraient" i / new_fam[0] (de l_amas)
                    #pour calculer k, on prend aléatoirement 2 epsilons
                    #qu'on ajoute aux x et y des disques de l'amas
                    #(pas le même epsilon, 2 pour chaque disque)
                    #ON GARDE DE TOUTE FACON LES 5 PREMIERES FAMILLES
                    #CALCULEES POUR CHAQUE AMAS
                    #On définit une fonction de coût (juge la qualité de la famille calculée)
                    #On garde les 5 premières calculées et les 5 ayant eu les meilleurs
                    #résultats, en tout on en garde Z (Z entre 5 et 10)
                    #on recommence avec ces Z familles,
                    #on recalcule k familles pour chaque élément de Z
                    #On garde les 5 premiers calculés et les 5 meilleurs par la fonction de coût
                    #on a une famille Z' pour chaque élément de Z
                    #mais maintenant on ne se soucie plus que de Z'
                    #On recommence un certain nombre de fois
                    #Au final, on prend une famille au hasard de Z''''''...'
                    #et on effectue le déplacement
                    
            """
            -Ne s'éloigne pas trop du barycentre
            -Elle se rapproche globalement vers la sortie
            -Elle a bougé depuis l'étape précédente
            """           
                       
def ClickScreen(event):
    x=event.x
    y=event.y   
    create_mark(x,y,"red")
    print(x,y)
    print(deplacement_possible(x,y,x,y,[],0))        
            
            

move().start()

canvas.bind("<Button-1>",ClickScreen)

fen.mainloop()
running=False
move()._stop()
