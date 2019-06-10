from tkinter import *
from math import sqrt,atan,cos,sin,pi,exp,asin,acos
from threading import Thread
from random import randint
from time import sleep,time
from copy import deepcopy
import pickle

fen = Tk()
fen.geometry("1200x1000")
fen["bg"]="white"

TEMPS=time()
canvas = Canvas(fen,width=1200,height=1000,bg="white")
canvas.place(x=0,y=0)
    
canvas.create_line(100,200,1100,200,width=5)    
canvas.create_line(1100,200,1100,700,width=5)    
canvas.create_line(1100,700,100,700,width=5)    
canvas.create_line(100,700,100,500,width=5)    
canvas.create_line(100,200,100,400,width=5)  

vmax=1 #pixels/sec en horizontale ET verticale
x_sortie,y_sortie=100,450
l={}   #dictionnaire contenant toutes les informations
moves = {}  #Dictionnaire avec uniquement les disques et les coordonnees pour le deplacement final
rayon=20    #rayon de base d'un disque
to_write=""
pos=[]
c=0
permission=0
pause = False
#si pause, alors l'affichage est fait lentement


pc=15
#precision du champ
#taille du cote d'un carre du maillage


def scalaireAB_AD(xa,ya,xb,yb,xd,yd): #AB.AD
        scal = (xb-xa)*(xd-xa)+(yb-ya)*(yd-ya)
        return scal
def projete(xV,yV,xB,yB,xA,yA):  #projete de (xV,yV) sur la droite (xA,yA)-(xB,yB)
    rapport = scalaireAB_AD(xB,yB,xA,yA,xV,yV)/scalaireAB_AD(xB,yB,xA,yA,xA,yA)
    #BA.BV / (BA.BA)
    xH = rapport*(xA-xB) + xB
    yH = rapport*(yA-yB) + yB
    return [xH,yH]

def zone_sortie(x,y,xs,ys):
    #renvoie un boolean indiquant si le disque en (x,y) peut sortir
    #eclipse centree en xt,yt, de demi petit axe b, de demi grand axe a
    
    #definition de l'ellipse:
    a=50
    if rayon==20:
        b=40
    elif rayon==10:
        b=30
    if (x/b)*(x/b)+(y/a)*(y/a)==1 or (y==ys and x-xs<=b):
        return True
    else:
        if x-xs>b:
            return False
        else:
            xi=xs+(a*((x-xs)/abs(y-ys)))/sqrt(1+(a*a/(b*b))*((x-xs)/(y-ys))**2)
            delta_y=a*sqrt(b*b-(xs-xi)*(xs-xi))/b
            if y>ys:
                yi=ys+delta_y
            else:
                yi=ys-delta_y
            return (x-xs)*(xi-x)+(y-ys)*(yi-y)>0
            
def repere_champ(x,y,champ):
    #champ est un maillage, donc tous les points ne sont pas calcules
    #on calcule donc le point (xv,yv) le plus proche de (x,y) tel que le champ
    #soit calcule en (xv,yv), et on renvoie champ[xv][yv]
    #sachant qu'on a un maillage de base a une distance au plus de sqrt(2)*pc
    xv,yv=10*int(x/10),10*int(y/10)
    dist=pc*pc
    for xp in range(x-int(1+sqrt(2)*pc),x+int(2+sqrt(2)*pc)):
        for yp in range(y-int(1+sqrt(2)*pc),y+int(2+sqrt(2)*pc)):
            d=sqrt((x-xp)**2+(y-yp)**2)
            if dist>d:
                try:
                    if champ[xp][yp]!=(0,0):
                        xv,yv=xp,yp
                        dist=d
                except IndexError:
                    pass
    return champ[xv][yv],dist
    
    
            
def add_cercle(x,y,r,defl):
    #cree (et affiche) l'objet tkinter
    #et l'ajoute dans defl
    canvas.create_oval(x-r,y-r,x+r,y+r,fill="black",outline="black",width=1)
    defl.append(("C",[x,y,r]))
def add_poly(L,defl):
    #L : liste des sommets
    #a relier dans le sens de lecture de l
    #cree (et affiche) l'objet tkinter
    #et l'ajoute dans defl
    new_L=[]
    for i in L:
        new_L+=[i[0],i[1]]
    canvas.create_polygon(new_L,fill="black",outline="black")
    defl.append(("T",L))
    

def superpose(defl,x,y):
    #retourne un boolean indiquant si le disque de centre (x,y) est superpose
    #au deflecteur defl
    (t,props)=defl
    if t=="C":
        (xc,yc,r)=props
        return (sqrt((x-xc)**2+(y-yc)**2)<rayon+r)
    else:
        L=props
        x,y=int(x),int(y)
        for xp in range(x-rayon,x+rayon+1,3):
            for yp in range(y-rayon,y+rayon+1,3):
                if sqrt((x-xp)**2+(y-yp)**2)<=rayon:
                    intersect=0
                    #nombre d'intersection avec la demi-droite horizontale de
                    #depart (x,y) avec le lacet formant le polygone
                    for i in range(len(L)):
                        try:
                            (x1,y1),(x2,y2)=L[i],L[i+1]
                        except IndexError:
                            (x1,y1),(x2,y2)=L[-1],L[0]
                        if y1==y2:
                            continue
                        xi=x1+(yp-y1)*(x2-x1)/(y2-y1)
                        intersect+=((x1<xi<x2 or x2<xi<x1) or ((x1<=xi<=x2 or x2<=xi<=x1) and (y1<yp<y2 or y2<yp<y1)))*(xi>xp)
                    
                    if intersect%2:
                        return True
        return False


def gene(defl,x,y,xt,yt):
    #prend en arg un deflecteur:
    #(type (cercle ou polygone <=> "C" ou "P"),[x,y,r] ou L (selon "C" ou "P"))
    #un point x,y
    #et retourne le boolean indiquant si le disque en x,y sera bloque par defl
    #s'il va tout droit vers xt,yt
    #et un entier indiquant la distance en pixels entre (x,y) et le point d'impact
    #a cet distance, il n'y a pas encore d'impact
    
    #on fait un while a priori
    (t,props)=defl
    if t=="C":
        (xc,yc,r)=props
        xh,yh=projete(xc,yc,x,y,xt,yt)
        return (sqrt((xc-xh)**2+(yc-yh)**2)<r+rayon and sqrt((x-xt)**2+(y-yt)**2)>sqrt((xc-xt)**2+(yc-yt)**2),sqrt((x-xc)**2+(y-yc)**2)-r)
    
    else:
        new_x,new_y=x,y
        pas_bloque=True
        dist=rayon//2
        d=sqrt((x-xt)**2+(y-yt)**2)
        while not(zone_sortie(new_x,new_y,xt,yt)) and pas_bloque:
            new_x=x+(xt-x)*dist/d
            new_y=y+(yt-y)*dist/d
            dist+=rayon//2
            pas_bloque=1-superpose(defl,new_x,new_y)
        return 1-pas_bloque,dist-1


def calcul_champ(x,y,defl):
    #retourne le point vise si on se trouvait au point x,y
    #ou retourne donc champ[x][y]
    #on determine les deflecteurs qui bloqueraient (x,y)
    #si (x,y) se dirigeait vers (x_sortie,y_sortie)
    bloquants=[]
    mini=9999999999
    cont=False
    for i in defl:                  
        if superpose(i,x,y): cont=True
        boolean,distance=gene(i,x,y,x_sortie,y_sortie)
        if boolean:
            if distance<mini:
                mini=distance
                bloquants=[i]
    if cont:
        #s'il y avait un disque en (x,y) alors il serait superpose a un deflecteur
        #or on considere que c'est impossible, donc on ne traite pas ce cas
        return (0,0)
    if bloquants==[]:
        if x<x_sortie+rayon+10:
            return (x_sortie+rayon+1,y_sortie)
        return (x_sortie,y_sortie)
    else:
        #print("test6")
        #bloquants[0] est le deflecteur qui va en premier bloquer (x,y)
        #donc c'est lui qu'il faut contourner en premier
        #c'est unqiuement selon lui qu'on va calculer le champ en (x,y)
        (t,props)=bloquants[0]
        if t=="C":
            (xc,yc,r)=props 
            L=(xc,yc,r)
            y_max,y_min=yc+r,yc-r
            if y_max-y>=y-y_min:
                tourne=-1
            else:
                tourne=1
            angle=0
            bloque=True
            while bloque and angle<2*pi:
                alpha=tourne*angle
                xb=x+(x_sortie-x)*cos(alpha)+(y_sortie-y)*sin(alpha)
                yb=y-(x_sortie-x)*sin(alpha)+(y_sortie-y)*cos(alpha)
                #rotation de centre (x,y), d'angle alpha
                #appliquee a x_sortie,y_sortie
                xb,yb=x+(xb-x)*500/sqrt((x-xb)**2+(y-yb)**2),y+(yb-y)*500/sqrt((x-xb)**2+(y-yb)**2)
                bloque=gene((t,L),x,y,xb,yb)
                bloque=bloque[0]
                angle+=3*(pi/180)
            alpha=tourne*angle
            xb=x+(x_sortie-x)*cos(alpha)+(y_sortie-y)*sin(alpha)
            yb=y-(x_sortie-x)*sin(alpha)+(y_sortie-y)*cos(alpha)
            return (xb,yb)
        else:
            L=props
            y_max=max([i[1] for i in L])
            y_min=min([i[1] for i in L])
            if y_max-y>=y-y_min:
                tourne=-1
            else:
                tourne=1
            angle=0
            bloque=True
            while bloque:
                alpha=tourne*angle
                xb=x+(x_sortie-x)*cos(alpha)+(y_sortie-y)*sin(alpha)
                yb=y-(x_sortie-x)*sin(alpha)+(y_sortie-y)*cos(alpha)
                #rotation de centre (x,y), d'angle alpha
                #appliquee a x_sortie,y_sortie
                xb,yb=x+(xb-x)*500/sqrt((x-xb)**2+(y-yb)**2),y+(yb-y)*500/sqrt((x-xb)**2+(y-yb)**2)
                bloque=gene((t,L),x,y,xb,yb)
                bloque=bloque[0]
                angle+=3*(pi/180)
            alpha=tourne*angle
            xb=x+(x_sortie-x)*cos(alpha)+(y_sortie-y)*sin(alpha)
            yb=y-(x_sortie-x)*sin(alpha)+(y_sortie-y)*cos(alpha)
            if xb==yb==0:
                print("done",bloquants,x,y)
                exit()
                        
            """xb,yb=x+(xb-x)*10/sqrt((xb-x)**2+(yb-y)**2),y+(yb-y)*10/sqrt((xb-x)**2+(yb-y)**2)
            canvas.create_line(x,y,xb,yb,arrow="last",width=1)"""
            return (xb,yb) 

def champ_sortie(defl):
    #champ[x][y]=(xt,yt)
    #defl[k]=(type (cercle ou polygone <=> "C" ou "P"),[x,y,r] ou L (selon "C" ou "P"))
    champ=[[(0,0) for i in range(701)] for j in range(1101)]
    for x in range(100+rayon,1101-rayon,pc):
        print(x)
        for y in range(200+rayon,701-rayon,pc):
            champ[x][y]=calcul_champ(x,y,defl)
            xv,yv=champ[x][y]
            #xv,yv=x+(xv-x)*pc/(2*sqrt((xv-x)**2+(yv-y)**2)),y+(yv-y)*pc/(2*sqrt((xv-x)**2+(yv-y)**2))
            #canvas.create_line(x,y,xv,yv,arrow='last',width=1)
    return champ
deflecteurs=[]
add_poly([(950,400),(1000,425),(1000,475),(950,500),(900,475),(900,425)],deflecteurs)
#add_cercle(180,450,50,deflecteurs)
add_poly([(200,400),(200,520),(260,450)],deflecteurs)
#add_cercle(700,300,40,deflecteurs)
#add_cercle(700,600,40,deflecteurs)
#sorties=champ_sortie(deflecteurs)


#Fonctions de permissions
def f1(dp,cst1=8,cst2=50):
    return cst1*(1+exp(-dp/cst2))
def f2(ds,cst1=14,cst2=100):
    return cst1/sqrt(1+((ds-50)/cst2)**4)
def perm_max(ds,dp):
    return min(f1(dp),f2(ds))
def perm_max_cone(ds,dp):
    return min(f1(dp),f2(ds))
nbr_max=25
amount=0              

while 1:
    if amount>=nbr_max: break
    c+=1
    x,y = randint(100+rayon,1100-rayon),randint(200+rayon,700-rayon)
    test = True
    for i in pos:
        if sqrt((x-i[0])**2+(y-i[1])**2)<=2*rayon:
            test=False
            break
    for j in deflecteurs:
        if superpose(j,x,y):
            test=False
            break
    if test:
        c=0
        amount+=1
        pos.append((x,y))
    if c==100000:
        break
def ClickScreen(event):
    print(event.x,event.y)   

n=len(pos) #n: nombre de disques
def create_point(xa,ya,col):
    """Fonction pour placer un disque de couleur 'col' a la coordonnee (xa,ya)"""
    disque = canvas.create_oval(xa-(rayon),ya-(rayon),xa+(rayon),ya+(rayon),fill="white",outline=col)
    return disque

def create_mark(xa,ya,col):
    """Fonction pour placer un petit marquer de couleur 'col' a la coordonnee (xa,ya)"""
    disque = canvas.create_oval(xa-2,ya-2,xa+2,ya+2,fill=col,outline=col)
    return disque


"""Creation du quadrillage                              |   |  <- Pixels inclus           
On a un rectangle noir de 1000x500                      | O |      
on veut creer un quadrillage avec cases de cote 4*r     |   |  <- Pixels exclus
Un quadrillage est represente par un couple de coordonnes (x,y)
tel que x,y soit le point en haut a gauche du quadrillage
"""
cote = 4*rayon
nbr_cases_x = int(999/cote)   #Si on est cense avoir PILE le nombre de case pour rentrer parfaitement,
                              #on enleve la derniere et on la rajoute apres dans la boucle,
                              #sinon, on aura une case plus petite que prevu, mais jamais une case trop grande
nbr_cases_y = int(499/cote)
cases = {}   #Dictionnaire cases:  {(x_coin,y_coin):[liste des disques dont\
                                   # le centre est dans la case],...}
distances = {}    #disque : distance_sortie
for i in range(nbr_cases_x+1):
    for j in range(nbr_cases_y+1):
        cases[i*cote+100,j*cote+200] = []


#UNE CASE A UN COTE 4*R = 200
       
def id_case(x,y):
    """Prend un couple de coordonnees (x,y) et retourne le couple (a,b)
    tel que le point represente par (x,y) soit dans la case de coin
    haut-gauche de coordonnes (a,b)"""
    try:
        assert (100<x<1100 and 200<y<700)
        a=int((x-100)/cote)*cote+100
        b=int((y-200)/cote)*cote+200
        return (a,b)
    except AssertionError:
        print(x,y)
        print("Le couple a identifier n'est pas dans le rectangle")

def add_list(ens,liste):
    return ens.__or__(set(liste))


     
    
    #on calcule xi,yi, l'intersection de la droite ((xt,yt),(x,y)) sur l'ellispe
    #on renvoie le boolean: (TA).(AI)>0   (ta.ai = ai*ta*cos(ta,ai)
    #cos(ta,ai)>0 ssi ta,ai dans ]-pi/2 ; pi/2[
    #car on a cos(ta,ai) dans {0,pi}
    #si c'est 0, alors c'est dedans, sinon c'est dehors

def C(v,securite):
    """Fonction qui renvoie les disques qui le touchent directement
    Prend en argument un disque
    Retourn la liste des disques a son contact / liste vide si aucun"""
    to_return = set()
    x,y = l[v][0],l[v][1]
    a,b = id_case(x,y)   #on recupere la case ou se trouve le disque qu'on test
    voisinage = set(cases[a,b])  #on recupere la liste du voisinage (pas forcement contact)
    #4
    #012
    #345
    #678    
    if a>100:
        voisinage = add_list(voisinage,cases[a-4*rayon,b])  #3
        if b>200:
            voisinage = add_list(voisinage,cases[a-4*rayon,b-4*rayon]) #0
            voisinage = add_list(voisinage,cases[a,b-4*rayon]) #1
        if b<600:
            voisinage = add_list(voisinage,cases[a-4*rayon,b+4*rayon])  #6
            voisinage = add_list(voisinage,cases[a,b+4*rayon])  #7
    if a<1100-4*rayon:
        voisinage = add_list(voisinage,cases[a+4*rayon,b]) #5
        if b>200:
            voisinage = add_list(voisinage,cases[a+4*rayon,b-4*rayon]) #2
            voisinage = add_list(voisinage,cases[a,b-4*rayon]) #1
        if b<600:
            voisinage = add_list(voisinage,cases[a+4*rayon,b+4*rayon]) #8
            voisinage = add_list(voisinage,cases[a,b+4*rayon])  #7
            
    #On ajoute plusieurs fois le meme a un ensemble -> pas grave
    for i in voisinage:
        xb,yb = l[i][0],l[i][1]
        if 0<sqrt((x-xb)**2+(y-yb)**2)<=2*rayon+securite:
            to_return.add(i)
    return to_return
    
    

def T(v,securite,xt,yt):
    """Fonction qui prend en argument un disque
    Qui renvoie tous les disques en son contact direct ou non
    (le contact du contact du contact ... est renvoye)
    et qui se trouve derriere v"""
    to_return = {}    #renvoie le dictionnaire {indice du contact (0 -> direct / sinon -> plus ou moins direct) : set({disque})}  
    Cv = set(C(v,securite))
    Tv = set(Cv)
    i=0
    xv,yv=l[v][0],l[v][1]
    #xt,yt=sorties[int(xv)][int(yv)]
    while Cv != set() and i<5:
        to_return[str(i)]=Cv
        new_Cv = set()
        for j in Cv:
            xj,yj=l[j][0],l[j][1]
            #si j est devant v, on ne le copte pas
            if sqrt((xj-xt)**2+(yj-yt)**2)<sqrt((xv-xt)**2+(yv-yt)**2):
                continue
            new_Cv= new_Cv.__or__(C(j,securite).__sub__(Tv.__or__(set(j).__or__({v}))))
        Tv = Tv.__or__(new_Cv)
        Cv = new_Cv
        i+=1
    return to_return
    
def influence(k,L,n):
    """
    pour un indice de disque k, la famille des listes de des indices, et l'indice du disque k
    dans la famille L, renvoie la liste / l'ensemble des indices de disques
    dont la vitesse va etre modifiee par k
    """
    try:
        to_check = L[n-1] #set des indices
        contact_direct=C(k,0)
        return list(to_check.intersection(contact_direct))
    except:
        return []

def coef_poussee(ds):
    return 0.7/(1+5*exp(-(x**(1.3)-350)*1.5*0.001))
    
    
    
    
    
    
for i in range(len(pos)):
    x,y=pos[i][0],pos[i][1]
    d=create_point(x,y,"black")
    v=vmax
    case = id_case(x,y)
    a,b = case[0],case[1]
    distance = sqrt((x-x_sortie)**2+(y-y_sortie)**2)
    distances[str(i)]=distance
    cases[a,b].append(str(len(l)))
    moves[str(len(l))]=[x,y,d]
    #Pour avoir des cibles en fonction du disque, on pourra creer une fonction
    #qui a  une case donnee (un couple) associe le point a atteindre (couple)
    
    
    #x, y, vx, vy, rayon, vmax, temps, disque_canvas, x_to_reach, y_to_reach,
    #v_contraintes_x,v_contraintes_y, case,distance_sortie
    l[str(len(l))]=[x,y,0,0,rayon,vmax,0,d,x_sortie,y_sortie,0,0,case,distance]
    



def normal(vx,vy,n):
    """Pour un vecteur v=(vx,vy) renvoie le vecteur colineaire a v de norme n"""
    if vx==0:
        if vy==0: 
            return (0,0)
        else:
            return (0,n)
    elif vy==0:
        return (n,0)
    else:
        return (n/sqrt(1+(vy/vx)**2),n/sqrt(1+(vx/vy)**2))


def deplacement_possible(xa,ya,x,y,famille_n,indice,permis=0):
    #un disque d'indice 'indice', à la base en position (xa,ya) cherche
    #à se déplacer à la position (x,y), sachant qu'il fait partie de
    #la famille en cours de calcul 'famille'
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
        xb,yb = l[i][0],l[i][1]
        if sqrt((x-xb)**2+(y-yb)**2)<2*rayon-permis and i!=indice:
            return False
            #si ca se touche
    for j in deflecteurs:
        if superpose(j,x,y):
            #print("bloque:",x,y)
            return False
    for j in sort_fam:
        try:
            if sqrt((j[0]-x)**2+(j[1]-y)**2)<2*rayon and indice!=j[2]:
                return False
        except IndexError:
            pass
    return True

liste_sortis=[]
class Mouvement(Thread):
    def run(self):
        global distances,to_write,liste_sortis,pause
        changed = True    #Permet de savoir si le systeme est bloque -> arret pour l'instant
        tour = 0
        sleep(2)
        while len(l)!=0 and changed and tour<100000:
            tour+=1
                
            changed = False
            new_dist = {}
            for i in range(len(l)):

                #distances =  {disque: distance a la sortie}
                (mini,k)=min([(v,k) for k,v in distances.items()])
                #on recupere l'indice du disque le plus proche de la sortie
                try:
                    del distances[k]
                    new_dist[k]=mini
                except KeyError:
                    if pause: print("wot")
                    pass
                #et on le supprime de la liste des distances a traiter
                #puis on le rajoute a la liste pour la prochaine boucle
                
                #Vxa,Vya=l[k][2],l[k][3]
                xa,ya=l[k][0],l[k][1]
                #xt,yt=repere_champ(int(xa),int(ya),sorties)
                xt,yt=calcul_champ(xa,ya,deflecteurs)
                if pause: sleep(1)
                if pause and xa>800:
                    print("bloquer:",(xa,ya),(xt,yt))
                    for j in deflecteurs:
                        print(superpose(j,xa,ya))
                if (xt,yt)==(0,0):
                    #on est trp proche d'un deflecteur
                    #et par l'approximation de la dizaine de cases
                    #on a la meme trajectoire qu'un disque qui se trouverait
                    #sur le deflecteur
                    #ainsi, on cherche autour de notre position une trajectoire 
                    #telle que (xt,yt)!=(0,0)
                    #theoriquement, il existe une case voisine de trajectoire non nulle
                    #on regarde donc les 8 voisines
                    xt,yt=x_sortie,y_sortie
                d_at=sqrt((xa-xt)**2+(ya-yt)**2)
                if pause: canvas.create_oval(xt-4,yt-4,xt+4,yt+4,fill="blue")
                if pause: print((xa,ya),"vise:",(xt,yt))
                canvas.itemconfig(l[k][7],outline="gold",width=5)
                if pause: sleep(1)
                
                
                Tv = T(k,0,xt,yt) #en contact par l'arriere
                sorti=False
                if pause: print(Tv)
                #boolean qui dit si le disque actuel est sorti ou pas
                #permet d'eviter les keyerror si un disque est deja sorti mais est encore dans Tv ou autre 
                #(plus rapide que de supprimer les elements de Tv)
                        
                
                    
                #On place un marqueur vert sur tous les disques
                #en contact (in)direct du disque K de la boucle
                
                
                
                      
                    
                #On a (xi,yi) les nouvelles coordonnees s'il n'y a aucune interaction
                #Point b: point representant le vecteur contrainte totale recue par le disque de centre xa,ya
                #xc = (xb-xa + xi - xa)/sqrt((xb-xa+xi-xa)**2+(yb-ya+yi-ya)**2)
                #yc = (yb-ya+yi-ya)/sqrt((xb-xa+xi-xa)**2+(yb-ya+yi-ya)**2)
                
                epsilon=30 #taille du segment entre le disque et la sortie
                           #ou on regarde si on peut se deplacer directement
                pas=1
                d=pas+1
                d_to_move=0
                boucle_apres=False
                disques_proches =[]
                (a,b)=id_case(xa,ya)
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
                    x,y = l[i][0],l[i][1]
                    if sqrt((xa-x)**2+(ya-y)**2)<2*rayon+5 and (xa!=x or ya!=y):
                        disques_proches.append(i)
                compteur=0
                while d<=epsilon and Tv=={}:
                    compteur+=1
                    if compteur%65==0:print("BOUCLE")
                    if xa<100+rayon+10:
                        xi,yi=x_sortie+rayon+1,ya+d*(2*(ya<450)-1)
                    else:
                        xi=xa+int((xt-xa)*d/d_at)
                        yi=ya+int((yt-ya)*d/d_at)
                    if pause: create_mark(xa,ya,"red")
                    if pause: create_mark(xi,yi,"red")
                    if pause: create_mark(x_sortie,y_sortie,"red")
                    if deplacement_possible(xa,ya,xi,yi,[],k):
                        if zone_sortie(xi,yi,x_sortie,y_sortie):
                            d_to_move=d
                            break
                        #si on peut se deplacer pour un certain k
                        #on va s'interesser au k superieur
                        #qui sera meilleur s'il convient
                        d+=pas
                        continue
                    else:
                        if d-1==pas:
                            boucle_apres=True
                        
                            #si on n'a pas reussi a bouger d'un poil
                            #on essaye la formule des permissions
                            #on regarde si on peut traverser un peu les
                            #autres disques
                            if pause: print("test0")
                
                
                            
                            #ensemble des disques a moins de 5 pixels de distance
                            
                            
                                    
                                    
                            if pause:
                                if sqrt((xa-x_sortie)**2+(ya-y_sortie)**2)<100:
                                    print(disques_proches)
                            disques_bloquant = []
                            #Calcul de l'ensembles (ou liste) des disques
                            #en contact direct avec k et tel que l'angle
                            #entre la sortie et les 2 centres est plus petit
                            #que pi/4 (en gros les seuls qui peuvent bloquer
                            #k alors qu'il veut partir)
                            #IL FAUT QUE L'ANGLE ENTRE LES DEUX DISQUES ET
                            #LA SORTIE SOIT STRICTEMENT ENTRE pi/6 et pi/4
                            #sinon on break
                            # de la forme: {(k,x,y),...}  
                            hs=[]
                            for i in disques_proches: #i est l'index du disque
                                x,y=l[i][0],l[i][1]
                                xh,yh=projete(x,y,xa,ya,xt,yt)
                                d=sqrt((xh-x)**2+(yh-y)**2)
                                ha=2*rayon-d
                                
                                d=sqrt((xh-x)**2+(yh-y)**2)
                                ab=sqrt((xa-x)**2+(ya-y)**2)
                                if (xh-xt)**2+(yh-yt)**2 > (xa-xt)**2+(ya-yt)**2:
                                    continue
                                    
                                angle_a_la_sortie=asin(d/ab)
                                
                                if ha>0 and angle_a_la_sortie<pi/2:
                                    disques_bloquant.append((i,x,y))
                                    hs.append((ha,(i,x,y)))
                            if sqrt((xa-x_sortie)**2+(ya-y_sortie)**2)<150:
                                if pause: print("TRES PROCHE ICI")
                                if pause: sleep(1)
                                if pause: create_mark(xa,ya,"lightpink")
                            if disques_bloquant==[]:
                                #on a deux possibilites
                                #soit il est bloque par l'arriere, donc on utilise l'algorithme d'apres
                                #ou on calcul recursivement les forces qui s'appliquent sur le disque k
                                #soit il est bloque par un deflecteur
                                deflec=False
                                
                                for j in deflecteurs:
                                    if superpose(j,xi,yi):
                                        deflec=True
                                        t,props=j
                                if deflec:
                                    boucle_apres=False
                                    #sorties[int(xi)][int(yi)]=(xt,yt)
                                    d=epsilon+4
                                    if t=="C":
                                        xc,yc,r=props
                                        xi+=3*(2*(xa>xc)-1)
                                        yi+=3*(2*(ya>yc)-1)
                                    else:
                                        if ya>450:
                                            yi+=3
                                        else:
                                            yi-=3
                                        xi+=3
                                    xt,yt=calcul_champ(xi,yi,deflecteurs)
                                    if pause:
                                        print("bloque:",(xa,ya),(xt,yt),(xi,yi))
                                        create_mark(xa,ya,"tomato")
                                        create_mark(xi,yi,"aqua")
                                    break
                                else:
                                    if pause: print("test6")
                                    break
                                #on calcule la visee exacte du point qu'on veut atteindre
                                #par l'algorithme de champ, mais pour le seul point
                                #(xa,ya), puis on met a jour champ
                                #au cas ou par hasard, on a un autre disque qui tombe
                                #exactement sur cet coordonnee
                                
                                """
                                ON PEUT CHERCHER ICI A DEVELOPPER ET A CREER UN MAILLAGE
                                PLUS FIN, ET DONC UNE FONCTION QUI A UN POINT ASSSOCIE
                                LE POINT LE PLUS PROCHE OU LE CHAMP A ETE CALCULE
                                
                                """
                                
                            if pause: print("test2")
                            h,i=max(hs)
                            ds=sqrt((xa-x_sortie)**2+(ya-y_sortie)**2)
                            xe,ye=i[1],i[2]
                            #dp: distance qu'on devrait traverser pour aller au dela du disque qui nous bloque
                            ae=sqrt((xa-xe)**2+(ya-ye)**2)
                            dp=2*sqrt((ae*ae-(2*rayon-h)**2))
                            dp=2*sqrt(4*rayon*h-h*h)
                            if pause: create_mark(xa,ya,"brown")
                            if pause: create_mark(xa+3,ya,"brown")
                            if pause: create_mark(i[1],i[2],"brown")
                            if pause: print(xa,ya,i[1],i[2],h)

                            if pause: print("h:",h,"dp:",dp)
                            if pause: create_mark(xa,ya,"green")
                            if pause: create_mark(xa+3,ya,"green")
                            if pause: create_mark(i[1],i[2],"green")
                            if pause: sleep(5)
                            F=perm_max(ds,dp)
                            if h>rayon: #le trajet est trop bloqué, on fait rien
                                F=h-1
                            if F>=h: #si on peut permettre plus que ce qu'il faut
                                #alors on le laisse passer, si c'est possible
                                #avec les donnees du reste de l'environnement
                                if pause: print("test3")
                                if pause: print("dp:",dp,"ds:",ds,"F:",F,"h:",h)
                                if pause: create_mark(xa,ya,"blue")
                                #sleep(5)
                                
                                
                                #on calcule le point ou on doit deplacer A: point I(xi,yi)
                                #c'est le symetrique de A par rapport a la droite perpendiculaire
                                #a AT et passant par E
                                xb,yb=projete(xe,ye,xa,ya,xt,yt)
                                eb=sqrt((xe-xb)**2+(ye-yb)**2)
                                ab=sqrt((xa-xb)**2+(ya-yb)**2)
                                try:
                                    bi=sqrt((2*rayon+1)**2-eb*eb)
                                except ValueError:
                                    print("nani",ae,eb)
                                    create_mark(xe,ye,"red")
                                    create_mark(xb,yb,"blue")
                                    create_mark(xa,ya,"gold")
                                    sorti=True
                                    sleep(15)
                                    break
                                    
                                ai=sqrt((xa-xb)**2+(ya-yb)**2)+bi
                                ab=ai-bi
                                xi=xa+int((xb-xa)*ai/ab)
                                yi=ya+int((yb-ya)*ai/ab)
                                if pause: create_mark(xi,yi,"blue")
                                if pause: sleep(2)
                                if deplacement_possible(xa,ya,xi,yi,[],k):
                                    boucle_apres=False
                                    if pause: print("test4")
                                    changed=True
                                    xo,yo=deepcopy(l[k][0]),deepcopy(l[k][1])
                                    l[k][0],l[k][1]=xi,yi
                                    l[k][2],l[k][3]=xi-xo,yi-yo
                                    xa,ya=xi,yi
                                    cases[id_case(xo,yo)].remove(k)
                                    if zone_sortie(xi,yi,x_sortie,y_sortie):
                                        if pause: print("out")
                                        canvas.coords(l[k][7],-200,-200,-200,-200)
                                        sorti=True
                                        del l[k]
                                        liste_sortis.append(k)
                                        del new_dist[k]
                                    else:
                                        cases[id_case(xi,yi)].append(k)
                                        canvas.coords(l[k][7],xi-rayon,yi-rayon,xi+rayon,yi+rayon)
                                        if pause: print("1")
                                        new_dist[k]=sqrt((x_sortie-xi)**2+(y_sortie-yi)**2)
                                        if pause: sleep(2)
                                        canvas.itemconfig(l[k][7],outline="black",width=1)
                                    moves[k].append((xi,yi))
                                    to_write+="("+str(k)+","+str(xi)+","+str(yi)+"),"
                                else:
                                    if pause: print("bloque apres",xi,yi)
                                    if pause: create_mark(xa,ya,"firebrick")
                                    if pause: create_mark(xi,yi,"firebrick")
                                    
                                    canvas.itemconfig(l[k][7],outline="black",width=1)
                            elif F!=h-1:
                                if pause: print("dp:",dp,"ds:",ds,"F:",F,"h:",h)
                                if pause: create_mark(xa,ya,"yellow")
                                canvas.itemconfig(l[k][7],outline="black",width=1)
                        else:  #if (d-1)!=pas
                            #on a pu avancer au moins un peu
                            #et on est arrive au maximum, donc on effectue
                            #le deplacement pour le k precedent
                            if pause: print("test3")
                            d_to_move=d-pas
                            for j in deflecteurs:
                                if superpose(j,xi,yi):
                                    xi=xa+int((xt-xa)*d_to_move/d_at)
                                    yi=ya+int((yt-ya)*d_to_move/d_at)
                            #si on met a jour directement ca empeche les disques 
                            #de se toucher, donc on ne gere pas les contacts entre les
                            #disques, donc si ca touche un autre disque, on ne met
                            #pas a jour, mais si ca touche un deflecteur, alors
                            #on met a jour
                            break
                if pause: 
                    try:
                        print(d_to_move,xi,yi)
                    except:
                        pass
                if sorti:
                    continue
                if boucle_apres:
                    canvas.itemconfig(l[k][7],outline="black",width=1) 
                    continue
                if d>epsilon: d_to_move=epsilon
                if d_to_move==0:
                    if not(deplacement_possible(xa,ya,xi,yi,[],k)):
                        pass
                        #print((xa,ya),(xi,yi),(xt,yt))
                if d_to_move!=0:
                    if not(deplacement_possible(xa,ya,xi,yi,[],k)):
                        d=False
                        for j in deflecteurs:
                            x=superpose(j,xi,yi)
                            d=d or x
                            #print(x)
                        if d:
                            #print(xi,yi)
                            create_mark(xi,yi,"firebrick")
                    #on a pu avancer au moins un peu, et notre deplacement ne
                    #sera pas modifie par d'autres disques, donc on avance
                    #et on se place en (xi,yi)
                    if not(100+rayon<xi<1100-rayon) and not(400+rayon<yi<500-rayon) and not(zone_sortie(xi,yi,x_sortie,y_sortie)): 
                    #on verifie le x, mais en regardant qu'on ne soit pas a la sortie
                        #mur horizontal
                        if xi<100+rayon:
                            xi=100+rayon
                        else:
                            xi=1100-rayon
                    if not(200+rayon<yi<700-rayon):
                        if yi<200+rayon:
                            yi=200+rayon
                        else:
                            yi=700-rayon
                        #mur vertical
                    xo,yo=deepcopy(l[k][0]),deepcopy(l[k][1])
                    changed=True
                    if sorti: print("testbug")
                    l[k][0],l[k][1]=xi,yi
                    l[k][2],l[k][3]=xi-xo,yi-yo
                    xa,ya=xi,yi
                    cases[id_case(xo,yo)].remove(k)
                    if zone_sortie(xi,yi,x_sortie,y_sortie):
                        if pause: print("out")
                        canvas.coords(l[k][7],-200,-200,-200,-200)
                        sorti=True
                        del l[k]
                        liste_sortis.append(k)
                        del new_dist[k]
                    else:
                        cases[id_case(xi,yi)].append(k)
                        canvas.coords(l[k][7],xi-rayon,yi-rayon,xi+rayon,yi+rayon)
                        new_dist[k]=sqrt((x_sortie-xi)**2+(y_sortie-yi)**2)
                        if pause: print("2")
                        if pause: sleep(2)
                        canvas.itemconfig(l[k][7],outline="black",width=1)
                    moves[k].append((xi,yi))
                    to_write+="("+str(k)+","+str(xi)+","+str(yi)+"),"
                    continue
                
                
                    
                if sorti: continue  
                
                
                """
                ou a,b,c... sont les cles des disques dans la liste l
                T(v)={0:{a},1:{b,c},....,max_indice:{d}}
                """
                m=0
                
                while m<len(Tv.keys()):
                    removed=[]
                    if len(Tv[str(m)])>1:
                        for r in Tv[str(m)]:
                            xr,yr = l[r][0],l[r][1]
                            for z in Tv[str(m)]:
                                if z in removed: continue
                                xz,yz = l[z][0],l[z][1]
                                if z!=r and sqrt((xr-xz)**2+(yr-yz)**2)<=2*rayon:
                                    dist_r,dist_z=sqrt((xr-xt)**2+(yr-yt)**2),sqrt((xz-xt)**2+(yz-yt)**2)
                                    to_remove = r #indice qu'on va augmenter
                                    if dist_r<=dist_z:
                                        to_remove=z
                                    removed.append(to_remove)
                        removed=list(set(removed))
                        for r in removed:
                            Tv[str(m)].remove(r)
                            try:
                                Tv[str(m+1)].add(r)
                            except KeyError:
                                Tv[str(m+1)]=set({r})
                        
                    m+=1
                
                if pause: print(Tv)
                    
                #on calcule l'indice de chaque disques par rapport au disque qu'on est en train
                #de calculer, on calculer dans le sens decroissant des indices.
                #T(v)={0:{a,b],1:{c},2:{d,e},...,indice_max:{f}}}
                
                n=max([int(i) for i in Tv.keys()]+[-1])
                all_disques_to_calc=[k]
                for i in Tv.values():
                    all_disques_to_calc.extend(list(i))
                
                
                while n>=0:
                    pousseurs=list(Tv[str(n)])
                    for p in pousseurs:
                        xp,yp=l[p][0],l[p][1]
                        if pause: sleep(1)
                        if pause: create_mark(xp,yp,"yellow")
                        if n==0:
                            pousses=[k]
                        else:
                            pousses=Tv[str(n-1)].__and__(set(influence(p,Tv,n)))
                        for j in pousses:
                            vxj,vyj=l[j][2],l[j][3]
                            vxp,vyp=l[p][2],l[p][3]
                            xj,yj=l[j][0],l[j][1]
                            xh,yh=projete(xp+vxp,yp+vyp,xp,yp,xj,yj)
                            ds=sqrt((xj-x_sortie)**2+(yj-y_sortie)**2)
                            t=coef_poussee(ds)  #trouver le bon coef dans ]0;1[
                            #t augmente: le poussage a plus d'impact
                            vyj=t*(yh-yp)+(1-t)*vyj 
                            vxj=t*(xh-xp)+(1-t)*vxj
                            l[j][2:4]=[vxj,vyj]
                            if pause: create_mark(xj,yj,"green")
                            if pause: sleep(0.5)
                        break
                            
                    n-=1
                xc,yc=xa+l[k][2],ya+l[k][3]
                if (xc,yc)==(xa,ya): continue
                #xc,yc=xi,yi
                
                
                if pause: create_mark(xc,yc,"aqua")
                if pause: sleep(2)
                #si on est trop proche d'un mur vertical
                #on ne vise pas la sortie, on vise la verticale
                if xa<100+rayon+10:
                    
                    xd,yd=projete(xc,yc,xa,ya,xa+5,ya+5)
                    x_vise,y_vise=xa,ya+20*(-1)**(ya>yt)
                else:
                    xd,yd=projete(xc,yc,xa,ya,xt,yt)
                    x_vise,y_vise=xt,yt
                if pause: create_mark(x_vise,y_vise,"firebrick")
                if pause: print(x_vise,y_vise)
                if pause: sleep(2)
                ad=sqrt((xa-xd)**2+(ya-yd)**2)
                ac=sqrt((xa-xc)**2+(ya-yc)**2)
                try:
                    alpha=acos(ad/ac)
                    pas_angle=alpha/4
                except ValueError:
                    alpha=0
                    pas_angle=1
                d_vise=sqrt((x_vise-xa)**2+(y_vise-ya)**2)
                xe=xa+(x_vise-xa)*ac/d_vise
                ye=ya+(y_vise-ya)*ac/d_vise
                xb1,yb1=(xe+xc)/2,(ye+yc)/2
                ab1=sqrt((xa-xb1)**2+(ya-yb1)**2)
                epsilon=30 #rayon du cone de recherche
                xb=xa+(xb1-xa)*epsilon/ab1
                yb=ya+(yb1-ya)*epsilon/ab1
                pas_module=4
                moved=False
                nxc,nyc=xb,yb
                couleur=["aqua","green","brown","red","yellow","gold","blue","firebrick"]
                if tour>6 and pause:
                    create_mark(nxc,nyc,couleur[tour%8])
                    sleep(0.5)
                
                #on teste si on va trouver un deplacement possible dans le cone de recherche
                #quitte a traverser un disque
                #si on n'a rien alors on fait directement le disque suivant (continue)

                x_centre,y_centre=xb,yb
                while epsilon>0:
                    beta=0
                    pair=1                       
                    while abs(beta)<=5*alpha/4:
                        #rotation de centre xa,ya et d'angle beta
                        nxc,nyc=xa+(x_centre-xa)*cos(beta)-(y_centre-ya)*sin(beta),ya+(x_centre-xa)*sin(beta)+(y_centre-ya)*cos(beta)
                        nxc,nyc=xa+epsilon*(nxc-xa)/sqrt((nxc-xa)**2+(nyc-ya)**2),ya+epsilon*(nyc-ya)/sqrt((nxc-xa)**2+(nyc-ya)**2)
                        if pause: 
                            create_mark(nxc,nyc,couleur[tour%8])
                        if pause: sleep(0.1)
                        if deplacement_possible(xa,ya,nxc,nyc,[],k):
                            moved=True
                            break
                        else:
                            #on calcule les permissions
                            
                            #on determine les disques proches de xa,ya voulant se deplacer en nxc,nyc 
                            #(voisinage a moins de 5 px)
                            #if pause: print("test",beta,epsilon)
                            disques_proches=[]
                            (a,b)=id_case(xa,ya)
                            voisinage=set(cases[a,b])                            
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
                                try:
                                    x,y = l[i][0],l[i][1]
                                except KeyError:
                                    continue
                                if sqrt((xa-x)**2+(ya-y)**2)<2*rayon+5 and (xa!=x or ya!=y):
                                    disques_proches.append(i)
                            if disques_proches==[]:
                                beta=pair*(abs(beta)+(pair==1)*(pas_angle))
                                pair=-pair
                                continue
                            
                            
                            
                            #On determine les disques de disques_proches pouvant bloquer celui en xa,ya
                            #lors de son deplacement vers nxc,nyc
                            
                            disques_bloquant=[]
                            hs=[] #ceux qui vont bloquer et de combien 
                            #h=[(largeur de bloquage orthogonale,(indice,position du bloqueur))]
                            for i in disques_proches: #i: index du disque
                                try:
                                    x,y=l[i][0],l[i][1]
                                except KeyError:
                                    continue
                                xh,yh=projete(x,y,xa,ya,nxc,nyc)
                                d=sqrt((xh-x)**2+(yh-y)**2)
                                ha=2*rayon-d
                                if (xa-nxc)**2+(ya-nyc)**2<(xh-nxc)**2+(yh-nyc)**2:
                                    #alors h va pas bloquer       
                                    continue
                                if ha>0:
                                    disques_bloquant.append((i,x,y))
                                    hs.append((ha,(i,x,y)))
                            if disques_bloquant==[]:
                                #il y a rien devant, donc c'est a moins de 5 px derriere,
                                #mais on n'a pas eu deplacement possible
                                #ca veut dire qu'on a essaye de se deplacer trop loin
                                #mais on arrivera a un moment a un point qu'on pourra atteindre
                                #on attend d'y etre
                                #ou qu'on essaye d'aller selon un certain angle qui
                                #fait que on ne peut pas se deplacer meme si le bloqueur
                                #est a plus de 90°
                                #on qu'on bloque sur un mur                                
                                beta=pair*(abs(beta)+(pair==1)*pas_angle)
                                pair=-pair
                                continue
                            #au moins un disque nous bloque
                            h,i=max(hs) #on recupere le disque qui nous bloque le plus
                            xe,ye=i[1],i[2]
                            xb,yb=projete(xe,ye,xa,ya,nxc,nyc)
                            if xb==xa and ya==yb:                           
                                beta=pair*(abs(beta)+(pair==1)*pas_angle)
                                pair=-pair
                                continue                                
                            ds=sqrt((xa-nxc)**2+(ya-nyc)**2) #distance du point qu'on voudrait atteindre
                            ab=sqrt((xa-xb)**2+(ya-yb)**2)
                            eb=sqrt((xe-xb)**2+(ye-yb)**2)
                            dp=ab+sqrt((2*rayon)**2-eb*eb) #distance de la traversee a faire
                            F=perm_max_cone(ds,dp)
                            if pause: print("ds:",ds,"dp:",dp,"F:",F,"h:",h)
                            if h>rayon: #on voudrait traverser un trop grosse zone -> on essaye pas
                                F=h-1
                            if F>=h: #on a la permission d'effectuer la traversee
                                eb=sqrt((xe-xb)**2+(ye-yb)**2)
                                #on cherche a se deplacer au point I(xi,yi)
                                bi=sqrt((2*rayon+1)**2-eb*eb)
                                ab=sqrt((xa-xb)**2+(ya-yb)**2)
                                ai=ab+bi
                                xi=xa+int((xb-xa)*ai/ab)
                                yi=ya+int((yb-ya)*ai/ab)
                                if deplacement_possible(xa,ya,xi,yi,[],k) or zone_sortie(xi,yi,x_sortie,y_sortie):
                                    if pause:print("test10")
                                    #on peut se deplacer juste apres le disque qui nous bloquait de base
                                    #create_mark(xi,yi,"green")
                                    moved=True
                                    nxc,nyc=xi,yi
                                    break
                                else:
                                    #un autre disque en amont du premier doit encore nous bloquer
                                    #on ne peut pas avancer (on ne se donne pas trop de permissions)
                                    pass
                                    
                                    
                            elif F!=h-1:
                                #si on n'etait pas si derange que ca mais quand meme trop
                                #pour se permettre la traversee
                                if pause: print("dp:",dp,"ds:",ds,"F:",F,"h:",h)
                                if pause: create_mark(xa,ya,"yellow")
                            
                            #et si on peut pas bouger meme avec les permissions
                            if pause: print("nope")
                        beta=pair*(abs(beta)+(pair==1)*pas_angle)
                        pair=-pair
                    if moved: break
                    epsilon-=pas_module
                if sorti: continue
                xc,yc=int(nxc),int(nyc)
                if not moved:  #on passe trop souvent dans cette boucle
                    xc,yc=xa,ya
                    canvas.itemconfig(l[k][7],outline="black",width=1)
                    continue
                l[k][0],l[k][1]=xc,yc
                l[k][2],l[k][3]=xc-xa,yc-ya
                changed=True
                cases[id_case(xa,ya)].remove(k)
                if zone_sortie(xc,yc,x_sortie,y_sortie):
                    if pause: print("out")
                    canvas.coords(l[k][7],-200,-200,-200,-200)
                    del l[k]
                    liste_sortis.append(k)
                    del new_dist[k]
                else:
                    cases[id_case(xc,yc)].append(k)
                    if pause: print("move2")
                    if pause: create_mark(xa,ya,"darkblue")
                    canvas.coords(l[k][7],xc-rayon,yc-rayon,xc+rayon,yc+rayon)
                    new_dist[k]=sqrt((x_sortie-xc)**2+(y_sortie-yc)**2)
                    if pause: print("3")
                    if pause: sleep(2)
                    if pause: create_mark(xc,yc,"darkblue")
                    #print(xc,yc)
                    if pause: sleep(1)
                    canvas.itemconfig(l[k][7],outline="black",width=1)
                moves[k].append((xc,yc))
                to_write+="("+str(k)+","+str(xc)+","+str(yc)+"),"
                if pause: sleep(0.2)
            distances=new_dist
        
        
        with open("coordonnees.txt","wb") as writing:
            write = pickle.Pickler(writing)
            write.dump(moves)
        with open("coords.txt","w") as file:
            file.write(to_write)
        
        sleep(0.1)
        print("END")
        print(time()-TEMPS)
                    
Mouvement().start()
fen.mainloop()        