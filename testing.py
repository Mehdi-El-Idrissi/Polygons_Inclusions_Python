#!/usr/bin/env python3

from geo.polygon import Polygon
from geo.point import Point
from geo.quadrant import Quadrant
from geo.tycat import tycat
import matplotlib.pyplot as plt 
import numpy as np
from math import cos, sin, pi, sqrt
import random

import main_test
import main_test_opti_without_swatting
import main_test_version_nulle
import argparse


ratio_circle=0.95
ratio_regular=0.95
retrecissement=0.95

class OriPolygon(Polygon):
    def __init__(self,origin,side,points,minRadius,name):
        self.origin=origin
        self.points=points
        self.side=side
        self.name=name
        self.minRadius=minRadius
    def createInside(self,code,n=6):
        newSide=self.minRadius*retrecissement
        newOrigin=self.origin
        newPolygone=0
        if code==0:
            newPolygone=createSquare(newOrigin,newSide/1.5)
        elif code==1: 
            newPolygone=createTriangle(newOrigin,newSide)
        elif code==2:
            newPolygone=createCircle(newOrigin,newSide,n)
        elif code==3:
            newPolygone=createRegular(newOrigin,newSide,n)
        return newPolygone

def createSquare(origin,side):  #Origin is a point, side is a float
    a=side*2
    pointList=[]
    for point in [[-1,-1],[-1,1],[1,1],[1,-1]]:
            p=origin+Point([point[0]*side,point[1]*side])
            pointList.append(p)
    square=OriPolygon(origin,side,pointList,side,"Square")
    return square

def createTriangle(origin,side):        #Side means the distance from origin
    p1=origin+Point([0,side])
    p2=origin+Point([side,-side])
    p3=origin+Point([-side,-side])
    pointList=[p1,p2,p3]
    triangle=OriPolygon(origin,side,pointList,side,"Triangle")
    return triangle

def createCircle(origin,side,n):
    pointList = [origin+Point([cos(c*pi/n)*side, sin(c*pi/n)*side]) for c in range(2*n)]
    circle=OriPolygon(origin,side,pointList,side,"Circle")
    return circle


def createRegular(origin,side,n):
    pointList=[]
    minRadius=side
    for c in range(0,2*n):
        ratio=random.uniform(0.5,1)
        pointList.append(origin+Point([cos(c*pi/n)*side*ratio, sin(c*pi/n)*side*ratio])) 
        if(ratio*side<minRadius):
            minRadius=ratio*side
    regular=OriPolygon(origin,side,pointList,minRadius,"Regular")
    return regular
                                      
            
def createPolygone(origin,side,choice,n=6):
    if choice==0:
        polygone=createSquare(origin,side)
        return polygone
    elif choice==1: 
        polygone=createTriangle(origin,side)
        return polygone
    elif choice==2:
        polygone=createCircle(origin,side,n)
        return polygone
    else :
        polygone=createRegular(origin,side,n)
        return polygone

"""
    Code polygones randomly with certain control on some attributes :
        n_polygones : number of polygones in total
        n_points : number of points for each polygone (this is controlled by the circle)
        n_inclusions : mean number of inclusions
        side : the maximum parameter of polygones ( maximum width for example )
        
        - we chose non uniform probability law to chose between the circle, square and triangle
                with pc, ps, and pt the probabilities
        - we chose a geometric probability law to add inclusions with parameter p_inc
        - For displacement we start with the 0 origin, then we slide by the "side * 2" with a 
        uniform distribution in a place where there is no polygone : how to know if there is 
        no polygones ? 
            1 - Chose location randomly between -side*4 or +side*4 in x or y direction
            2 - Compute bounding quadrant with an origin that is the maximum side
            3 - Check all preexisting Big Polygones, if the bounding quadrant intersects the 
            quadrant of one of the Big Polygones change location, how to change
                a - Check if directions x and y on side are all taken
                    i - if yes : increase side and do the same starting from 3
                        if not : take position 
            
"""



def randomList(n_polygones_lim,n_circles,side):
    polygones=[]
    bigPolygones=[]
    n_polygones=0
    n_big_polygones=0
    origin=Point([0,0])
    state=0     #If state = 0 means that we 're not in inclusions
    i=0
    while n_polygones<n_polygones_lim :
        i+=1
        choice_shape=random.uniform(0,1)
        if choice_shape<ps:
            choice_shape=0
        elif choice_shape>=ps and choice_shape<ps+pt :
            choice_shape=1
        elif choice_shape>=pt and choice_shape<1-pr :
            choice_shape=2
        elif choice_shape>=1-pr:
            choice_shape=3
        #State machine of 2 states
        if state == 0 :
             
            """
            Random walk over one step 
            """
            stop_walk=0
            step=side
            amorti=0.3
            polygone = None     #Initilization of polygone
            while stop_walk==0 :
                choice_walk=random.choice([(-1,-1),(-1,1),(1,-1),(1,1)])      #Chose random direction
                # print("choice_walk",choice_walk)
                origin+=Point([choice_walk[0]*step*amorti,choice_walk[1]*step*amorti])    #advance to that direction with 
                bounding_quadrant_0=Quadrant([origin.coordinates[0]-side,origin.coordinates[1]-side],[origin.coordinates[0]+side,origin.coordinates[1]+side])
                if n_big_polygones!=0 :
                    
                    for i in range(0,n_big_polygones):                              #loop over all existing polygones
                        bounding_quadrant_=bigPolygones[i].bounding_quadrant()     #Compute bounding quadrant of each polygone
                        if bounding_quadrant_.intersect(bounding_quadrant_0) :  #check if intersection with created one
                            stop_walk=0                                         #Repeat operation as position is not available
                            step*=2                                     #increase size of the s
                            # print("failed")
                            break
                        else :
                            stop_walk=1    
                else : 
                    stop_walk=1
            if choice_shape==2 or choice_shape==3 :
                polygone=createPolygone(origin,side,choice_shape,n_circles)       #Create polygone
            else :
                polygone=createPolygone(origin,side,choice_shape) 
            polygones.append(polygone)
            print(n_polygones)
            bigPolygones.append(polygone)
            n_polygones+=1
            n_big_polygones+=1
            state=1
        elif state == 1:
            choice_inc=random.uniform(0,1)
            if choice_inc<p_inc:
                polygone=polygones[n_polygones-1].createInside(choice_shape,n_circles)
                polygones.append(polygone)
                print(n_polygones)
                n_polygones+=1
            else :
                state=0
    return polygones
        
def polygones_to_txt(polygones,file):
    f=open(file,'w');
    n_polygones=len(polygones)
    for i in range(0,n_polygones):
        pointList=(polygones[i]).points
        for p in pointList :
            index=repr(i)
            f.write(index)
            f.write(" ")
            x=repr(p.coordinates[0])
            f.write(x)
            f.write(" ")
            y=repr(p.coordinates[1])
            f.write(y)
            f.write('\n')
    f.close()  
    
    
"""
Default Parameters
"""
p_inc=0.7

#Shape probabilities
ps=0.2 
pc=0.1
pt=0

n_polygones=100     #Number of Polygones
n_circles=4         #Number of Points in circles or random shaped polygones
side=4              #Size of polygone(distance from origin to points)

parser = argparse.ArgumentParser()
parser.add_argument("--n_polygones", help="Give the number of polygones",
                    type=int)
parser.add_argument("--n_circles",help="Number of points in circles and regular polygones",type=int)
parser.add_argument("--side",help="Mean size of segment in polygone (from origin)",type=float)
parser.add_argument("--ps",help="Probability",type=float)
parser.add_argument("--pt",help="Probability",type=float)
parser.add_argument("--pc",help="Probability",type=float)
parser.add_argument("--p_inc",help="Probability",type=float)
parser.add_argument("--file_name",help="Nom du fichier créé")

#Plot de Tests
parser.add_argument("--test_parameter",help="si on va faire des tests")

#Number of values
parser.add_argument("--range_n_polygones",help="range of values of n_polygones",type=int)
parser.add_argument("--range_n_circles",help="range of values of n_polygones",type=int)
parser.add_argument("--range_p_inc",help="range of values of n_polygones",type=int)
parser.add_argument("--range_ps",help="range of values of n_polygones",type=int)
parser.add_argument("--range_pc",help="range of values of n_polygones",type=int)


#Max values
parser.add_argument("--max_n_polygones",help="range of values of n_polygones",type=int)
parser.add_argument("--max_n_circles",help="range of values of n_polygones",type=int)
parser.add_argument("--max_p_inc",help="range of values of n_polygones",type=float)
parser.add_argument("--max_ps",help="range of values of n_polygones",type=float)
parser.add_argument("--max_pc",help="range of values of n_polygones",type=float)


#Min values
parser.add_argument("--min_n_polygones",help="range of values of n_polygones",type=int)
parser.add_argument("--min_n_circles",help="range of values of n_polygones",type=int)
parser.add_argument("--min_p_inc",help="range of values of n_polygones",type=float)
parser.add_argument("--min_ps",help="range of values of n_polygones",type=float)
parser.add_argument("--min_pc",help="range of values of n_polygones",type=float)

parser.add_argument("--range_main",help="range for main",type=int)
args=parser.parse_args()
range_n_polygones=15
range_n_circles=1
range_p_inc=15
range_ps=15
range_pc=15


max_n_polygones=10000
max_n_circles=1000
max_p_inc=1
max_ps=1
max_pc=1


min_n_polygones=10
min_n_circles=4
min_p_inc=0
min_ps=0
min_pc=0

if(args.min_n_polygones):
    min_n_polygones=args.min_n_polygones
if(args.min_n_polygones):
    min_n_circles=args.min_n_circles
if(args.min_n_polygones):
    min_p_inc=args.min_p_inc
if(args.min_n_polygones):
    min_n_ps=args.min_ps
if(args.min_n_polygones):
    min_pc=args.min_pc

if(args.max_n_polygones):
    max_n_polygones=args.max_n_polygones
if(args.max_n_polygones):
    max_n_circles=args.max_n_circles
if(args.max_n_polygones):
    max_p_inc=args.max_p_inc
if(args.max_n_polygones):
    max_ps=args.max_ps
if(args.max_n_polygones):
    max_pc=args.max_pc

if(args.range_n_polygones):
    range_n_polygones=args.range_n_polygones
if(args.range_n_circles):
    range_n_circles=args.range_n_circles
if(args.range_p_inc):
    range_p_inc=args.range_p_inc
if(args.range_ps):
    range_ps=args.range_ps
if(args.range_pc):
    range_pc=args.range_pc

#Test on the polygones number

#function for iteration
def test_unitary(parameter):
    global n_polygones 
    global n_circles
    global side
    global ps 
    global p_inc 
    global pc 
    

    
    if(parameter=="n_polygones"):
        times=range_n_polygones 
        parameter_min=min_n_polygones
        parameter_max=max_n_polygones
        pas= (parameter_max-parameter_min)/times
        data=np.zeros(times)
        for i in range(0,times):
            print(i)
            data[i]=parameter_min+i*pas
            loop_polygones=randomList(parameter_min+i*pas,n_circles,side)
            suffix=str(i)
            polygones_to_txt(loop_polygones,"T/test"+suffix+".poly")
        return data
    elif(parameter=="n_circles"):
        times=range_n_circles
        parameter_min=min_n_circles
        parameter_max=max_n_circles
        pas= (parameter_max-parameter_min)/times
        data=np.zeros(times)
        print(times)
        for i in range(0,times):
            
            data[i]=int(parameter_min+i*pas)
            loop_polygones=randomList(n_polygones,int(parameter_min+i*pas),side)
            suffix=str(i)
            polygones_to_txt(loop_polygones,"T/test"+suffix+".poly")
        return data
    elif(parameter=="p_inc"):
        times=range_p_inc 
        parameter_min=min_p_inc
        parameter_max=max_p_inc
        pas= (parameter_max-parameter_min)/times
        data=np.zeros(times)
        for i in range(0,times):
            p_inc=parameter_min+i*pas
            data[i]=p_inc
            loop_polygones=randomList(n_polygones,n_circles,side)
            suffix=str(i)
            polygones_to_txt(loop_polygones,"T/test"+suffix+".poly")
        return data
    elif(parameter=="ps"):
        times=range_ps
        parameter_min=min_ps
        parameter_max=max_ps
        pas= (parameter_max-parameter_min)/times
        data=np.zeros(times)
        for i in range(0,times):
            ps=parameter_min+i*pas
            data[i]=ps
            loop_polygones=randomList(n_polygones,n_circles,side)
            suffix=str(i)
            polygones_to_txt(loop_polygones,"T/test"+suffix+".poly")
        return data
    elif(parameter=="pc"):
        times=range_pc
        parameter_min=min_pc
        parameter_max=max_pc
        pas= (parameter_max-parameter_min)/times
        data=np.zeros(times)
        for i in range(0,times):
            pc=parameter_min+i*pas
            data[i]=pc
            loop_polygones=randomList(n_polygones,n_circles,side)
            suffix=str(i)
            polygones_to_txt(loop_polygones,"T/test"+suffix+".poly")
        return data






























file="test_txt_1.poly"
if(args.file_name):
    file=args.file_name
if(args.ps):
    ps=args.ps
if(args.pt):
    ps=args.pt
if(args.pc):
    pc=args.pc
if(args.p_inc):
    p_inc=args.p_inc

pr=1-pc-pt-ps

if(args.n_polygones):
    n_polygones=args.n_polygones
if(args.n_circles):
    n_circles=args.n_circles
if(args.side):
    side=args.side

parameter=0
if args.test_parameter : 
    parameter=args.test_parameter

range_main=0
if args.range_main:
    range_main=args.range_main
data=test_unitary(parameter)
times_v3=main_test.main(len(data),parameter)
times_v2=main_test_opti_without_swatting.main(len(data),parameter)


print(times_v3)
times_v2=np.array(times_v2)
print(times_v2)
times_v3=np.array(times_v3)


plt.figure()
plt.xlabel("Nombre de points")
plt.ylabel("Temps (en ms)")
plt.title("Influence de la probabilité d'inclusion sur notre algorithme \n {} Acquisitions\n nombre de points moyen {} \n nombre de polygones: {}".format(len(data),n_circles,n_polygones))
"""times_v1=main_test_version_nulle.main(len(data),parameterq
times_v1=np.array(times_v1)
print((times_v1))
plt.plot(data,times_v1)"""
plt.plot(data,times_v2)
plt.plot(data,times_v3)
plt.legend(["Méthode des aires","Méthode du partitionnement"])

plt.show()

"""plt.figure()
plt.xlabel("Nombre de polygones")
plt.ylabel("Temps (en ms)")
plt.title("Influence du nombre de polygones sur notre algorithme \n {} Acquisitions\n probabilité d'inclusion \n nombre de points moyen: {}".format(len(data),p_inc,n_circles))
""""""times_v1=main_test_version_nulle.main(len(data),parameter)
times_v1=np.array(times_v1)
print((times_v1))
plt.plot(data,times_v1)""""""
plt.plot(data,times_v2)
plt.plot(data,times_v3)
plt.legend(["Méthode naive","Méthode des aires","Méthode du partitionnement"])

plt.show()"""
