from tkinter import *
from math import pi,cos,sin,sqrt,exp
from threading import Thread
from random import randint
from copy import deepcopy
import pickle
from sys import exit
from time import sleep


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

xt,yt=100,450
l={}
rayon=40
moves={}

to_write=""

with open("coordonnees.txt","wb") as writing:
    write = pickle.Pickler(writing)
    write.dump(moves)

pos=[]
c=0
n_max = 80
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
    if test:
        c=0
        pos.append((x,y))
        amount+=1
    if c==15:
        break
    
n=len(pos)

def create_point(xa,ya,col):
    disque = canvas.create_oval(xa-(rayon),ya-(rayon),xa+(rayon),ya+(rayon),fill="white",outline=col)
    return disque

def create_mark(xa,ya,col):
    disque = canvas.create_oval(xa-2,ya-2,xa+2,ya+2,fill=col,outline=col)
    return disque

cote = 4*rayon
nbr_cases_x = int(999/cote)   
nbr_cases_y = int(499/cote)
cases = {}   
distances = {}  
for i in range(nbr_cases_x+1):
    for j in range(nbr_cases_y+1):
        cases[i*cote+100,j*cote+200] = []                   


def id_case(x,y):
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
    to_return = set()
    x,y = l[v][0],l[v][1]
    a,b = id_case(x,y)
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
    
    epsilon = 10 
    for i in voisinage:
        xb,yb = l[i][0],l[i][1]
        if sqrt((x-xb)**2+(y-yb)**2)<2*rayon+epsilon:
            to_return.add(i)
    return to_return


def get_k_min(L,k):
    S = deepcopy(L)
    mins=[]
    for i in range(k):
        try:
            a=min(S)
        except:
            pass
        mins.append(a)
        S.remove(a)
    return mins
    
    

def T(v):
    to_return = {}
    Cv = set(C(v))
    Tv = set(Cv)
    i=0
    while Cv != set():
        to_return[str(i)]=Cv
        new_Cv = set()
        for j in Cv:
            new_Cv= new_Cv.__or__(C(j).__sub__(Tv.__or__(set(j))))
        Tv = Tv.__or__(new_Cv)
        Cv = new_Cv
        i+=1
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
    l[str(len(l))]=[x,y,0,0,rayon,vmax,0,d,xt,yt,0,0,case,distance]

def scalaireAB_AD(xa,ya,xb,yb,xd,yd):
        scal = (xb-xa)*(xd-xa)+(yb-ya)*(yd-ya)
        return scal
def projete(xV,yV,xB,yB,xA,yA):
    rapport = scalaireAB_AD(xB,yB,xA,yA,xV,yV)/scalaireAB_AD(xB,yB,xA,yA,xA,yA)
    xH = rapport*(xA-xB) + xB
    yH = rapport*(yA-yB) + yB
    return [xH,yH]
    

def barycentre(L):
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
    

def fct_cout(f_n,f_n1,G):
    dist_S = sum([((i[0]-100)**2+(i[1]-450)**2)**1/2 for i in f_n1])
    try:
        return dist_S
    except ZeroDivisionError:
        return 99999
    
def new_cout(f):
    return sum([((i[0]-xt)**2+(i[1]-yt)**2)**1/2 for i in f])
    
    
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
    return (to_return==set())    

    
class move(Thread):
    def run(self):
        global running,to_write
        changed = True
        tour = 0
        l_amas = []
        while running:
            while len(l)!=0 and changed and tour<100000:
                print(len(l),tour)
                if int(tour/100)==tour/100: print("TOUR",tour)
                liste_disques = [i for i in l.keys()]
                changed = False
                
                to_iterate = list(l.keys())
                for j in to_iterate:
                        x,y=l[j][0],l[j][1]
                        if x<100+rayon+10:
                            xi=x
                            sgn=1-2*(y>yt)
                            for k in range(60,1,-5):
                                yi=y+sgn*k
                                if deplacement_possible(x,y,xi,yi,[],j):
                                    create_mark(xi,yi,"green")
                                    xo,yo=deepcopy(l[j][0]),deepcopy(l[j][1])
                                    l[j][0]=xi
                                    l[j][1]=yi
                                    x,y = l[j][0],l[j][1]
                                    cases[id_case(xo,yo)].remove(j)
                                    cases[id_case(x,y)].append(j)
                                    canvas.coords(l[j][7],x-rayon,y-rayon,x+rayon,y+rayon)
                                    if x!=xo or y!=yo:
                                        changed = True
                                    else:
                                        print("stuck_NORMALEMENT_IMPOSSIBLE_LIGNE538")
                                    if sqrt((x-xt)**2+(y-yt)**2)<50:
                                        print("out")
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
                                if (not(deplacement_possible(x,y,xi,yi,[],j)) or k==2*rayon) and k>0:
                                    if k<2*rayon:
                                        k-=5
                                    if k==0: break
                                    if not(deplacement_possible(x,y,xi,yi,[],j)): break
                                    xo,yo=deepcopy(l[j][0]),deepcopy(l[j][1])
                                    l[j][0]=xi
                                    l[j][1]=yi
                                    x,y = l[j][0],l[j][1]
                                    cases[id_case(xo,yo)].remove(j)
                                    cases[id_case(x,y)].append(j)
                                    canvas.coords(l[j][7],x-rayon,y-rayon,x+rayon,y+rayon)
                                    if x!=xo or y!=yo:
                                        changed = True  
                                    else:
                                        print("stuck_NORMALEMENT_IMPOSSIBLE_LIGNE538")
                                    if sqrt((x-xt)**2+(y-yt)**2)<50:
                                        print("out")
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
                
                
                
                while liste_disques!=[]:
                    i=liste_disques[0]
                    Tv = T(i)
                    amas = []
                    for j in Tv.values():
                        for k in j:
                            amas.append(k)
                            try:
                                liste_disques.remove(k)
                            except ValueError:
                                pass
                    l_amas.append(amas)
                for i in l_amas:
                    if not(running):
                        exit()
                    G = barycentre(i)                    
                    xg,yg=G[0],G[1]
                    try:
                        assert xt!=xg
                        pente = (yt-yg)/(xt-xg)
                    except AssertionError:
                        pente = 0
                    if len(i)==1:
                        epsilon = 2*rayon+5
                    else:
                        epsilon = 20
                    try:
                        assert abs(pente) != 1
                        delta_x = abs(epsilon/sqrt(1+pente**2))
                    except AssertionError:
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
                    if len(i)==1 and deplacement_possible(l[i[0]][0],l[i[0]][1],xi,yi,[],i[0]):
                        j=i[0]
                        xo,yo=deepcopy(l[j][0]),deepcopy(l[j][1])
                        l[j][0]=xi
                        l[j][1]=yi
                        x,y = l[j][0],l[j][1]
                        cases[id_case(xo,yo)].remove(j)
                        cases[id_case(x,y)].append(j)
                        canvas.coords(l[j][7],x-rayon,y-rayon,x+rayon,y+rayon)
                        if x!=xo or y!=yo:
                            changed = True
                        else:
                            print("stuck1")
                        if sqrt((x-xt)**2+(y-yt)**2)<50:
                            print("out")
                            cases[id_case(x,y)].remove(j)
                            canvas.coords(l[j][7],-200,-200,-200,-200)
                            del l[j]
                        moves[j].append((x,y))
                        to_write+="("+str(j)+","+str(x)+","+str(y)+"),"
                        continue
                    y=5
                    to_save = []
                    to_keep=[]
                    new_fam = [[(l[s][0],l[s][1],s) for s in i]]
                    not_moved = deepcopy(new_fam)
                    
                    
                    
                    if len(i)>1:
                        for p in range(y):
                            k = 30                            
                            notes = []
                            for s in new_fam:
                                famille=[[] for i in range(k)]
                                for c in range(k):
                                    for d in s:                 
                                        if not(running):
                                            exit()
                                        xa,ya =d[0],d[1]                                        
                                        scale = int(max(10,20*exp(-0.05*len(s))))   
                                        scale=50
                                        possibles = []
                                        xo,yo=xa-3*scale/5,ya-scale
                                        
                                        for a in range(int(scale/5)):
                                            for j in range(int(scale/5)):
                                                if deplacement_possible(xa,ya,xo+5*a,yo+10*j,famille,d[2]):
                                                    possibles.append((xo+5*a,yo+10*j,d[2]))
                                        taille = len(possibles)
                                        if taille!=0:
                                            chosen = randint(0,taille-1)
                                            famille[c].append(possibles[chosen])
                                        else:
                                            famille[c].append((xa,ya,d[2]))
                                for j in famille:
                                    if j!=[]:
                                        notes.append((new_cout(j),j))
                                        
                                mins=get_k_min(notes,4)
                                to_save.append((mins[0][0],mins[0][1]))
                                to_save.append((mins[1][0],mins[1][1]))
                                to_save.append((mins[2][0],mins[2][1]))
                                to_save.append((mins[3][0],mins[3][1]))
                            saved = get_k_min(to_save,4)
                            new_fam=[saved[0][1],saved[1][1],saved[2][1],saved[3][1]]
                        select = new_fam[randint(0,len(new_fam)-1)]
                        new_fam=select
                        a = new_cout(not_moved[0])
                        b=new_cout(select)
                        if a<b:
                            for r in select:
                                xr,yr=r[0],r[1]
                                create_mark(xr,yr,"blue")
                                xo,yo=l[r[2]][0],l[r[2]][1]
                                create_mark(xo,yo,"red")
                            select = not_moved[0]
                        index = 0
                        for j in i:
                            xo,yo=deepcopy(l[j][0]),deepcopy(l[j][1])
                            l[j][0]=select[index][0]
                            l[j][1]=select[index][1]
                            x,y = l[j][0],l[j][1]
                            index+=1
                            cases[id_case(xo,yo)].remove(j)
                            cases[id_case(x,y)].append(j)
                            canvas.coords(l[j][7],x-rayon,y-rayon,x+rayon,y+rayon)
                            if x!=xo or y!=yo:
                                changed = True
                            else:
                                print("stuck2")
                            if sqrt((x-xt)**2+(y-yt)**2)<50:
                                print("out")
                                cases[id_case(x,y)].remove(j)
                                canvas.coords(l[j][7],-200,-200,-200,-200)
                                del l[j]
                            moves[j].append((x,y))
                            to_write+="("+str(j)+","+str(x)+","+str(y)+"),"
                        
                l_amas = []
                tour+=1
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
    print(deplacement_possible(x,y,x,y,[],0))        
            
            

move().start()

canvas.bind("<Button-1>",ClickScreen)

fen.mainloop()
running=False
move()._stop()
