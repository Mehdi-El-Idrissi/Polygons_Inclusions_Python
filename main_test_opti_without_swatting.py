#!/usr/bin/env python3
"""
fichier principal pour la detection des inclusions.
ce fichier est utilise pour les tests automatiques.
attention donc lors des modifications.
"""
import sys
from tycat import read_instance
from time import time
from geo.tycat import tycat
from geo.point import Point
from geo.tycat import tycat
from geo.polygon import Polygon
from geo.quadrant import Quadrant
from geo.segment import Segment

def mergeSort(myList):
    if len(myList) > 1:
        mid = len(myList) // 2
        left = myList[:mid]
        right = myList[mid:]

        # Recursive call on each half
        mergeSort(left)
        mergeSort(right)

        # Two iterators for traversing the two halves
        i = 0
        j = 0
        
        # Iterator for the main list
        k = 0
        
        while i < len(left) and j < len(right):
            if left[i][0] <= right[j][0]:
              # The value from the left half has been used
              myList[k] = left[i]
              # Move the iterator forward
              i += 1
            else:
                myList[k] = right[j]
                j += 1
            # Move to the next slot
            k += 1

        # For all the remaining values
        while i < len(left):
            myList[k] = left[i]
            i += 1
            k += 1

        while j < len(right):
            myList[k]=right[j]
            j += 1
            k += 1

#Sort polygones 
            
def sort_polygones(n_polygones: int,polygones: list):
    #t=time()

    # sorted_areas_with_keys : will contain sorted "indexes" of polygones with areas dim=[N,2]
    sorted_areas_with_keys=[]    
    # sorted_polygones is the polygones list sorted by increasing area
    sorted_polygones=[]      
    # sorted_keys_to_keys[i] = j means polygones[i]=sorted_polygones[j]   
    sorted_keys_to_keys=[0]*n_polygones                                       

    # Create sorted_areas_with_keys 
    for i in range(0,n_polygones):          #O(n)
        #Simplify ith polygone :
        # iter_p=iter(polygones[i].points)
        # p1=next(iter_p,None)
        # points_Pi=[p1]
        # p2=next(iter_p,None)
        # while True:
        #     p3=next(iter_p,None)
        #     if p3==None :
        #         points_Pi.append(p2)
        #         break
        #     test=(p2-p1).cross_product(p3-p2)       #see if they have same direction
        #     if test==0:
        #         while test==0:         #while they have the same direction and p3 different than none
        #             p1=p2 
        #             p2=p3
        #             p3=next(iter_p,None)
        #             if p3==None :
        #                 points_Pi.append(p2)
        #                 break
        #             test=(p2-p1).cross_product(p3-p2)
        #         if test!=0:                         # If we found a point not in the same direction
        #             points_Pi.append(p2)
        #     else :
        #         points_Pi.append(p2)        # no segment had the same direction
        #     p1=p2                   #increment the ps
        #     p2=p3
        #     if p2==None:
        #         break
        # polygones[i].points=points_Pi
        sorted_areas_with_keys.append([abs(polygones[i].area()),int(i)])    
    mergeSort(sorted_areas_with_keys)            # O(n log n)

    # Create sorted_keys_to_keys : list of integers and sorted_polygones : list of integers
    for i in range(0,n_polygones):
        sorted_keys_to_keys[i]=sorted_areas_with_keys[i][1]

        sorted_polygones.append(polygones[sorted_areas_with_keys[i][1]])
    #duree=time()-t
    #print("sort_polygones",duree)
    return sorted_polygones,sorted_keys_to_keys

def find_bounding_quadrants(sorted_polygones: list,n_polygones: int):
  
    min = [0]*n_polygones 
    max = [0]*n_polygones
    for i in range(0,n_polygones):
        min[i],max[i]=(sorted_polygones[i].bounding_quadrant()).get_arrays()   

    return min,max
#def Pseudo_Hash(sorted_polygones:list,n_polygones:int):
time_trouve_inclusions=0
def trouve_inclusions(polygones: list,sorted_keys_to_keys,bounding_quadrants):

    """
    renvoie le vecteur des inclusions
    la ieme case contient l'indice du polygone
    contenant le ieme polygone (-1 si aucun).
    (voir le sujet pour plus d'info)
    """
    duree=0
    # Polygones is the sorted list of polygones by areas
    n_polygones=len(polygones)                  #number of polygones O(n_polygones)
    inclusions=[-1]*n_polygones
    
    for i in range(n_polygones-1,-1,-1):              #Loop over polygones to get the inclusions of each one of them
        # i is the index in the sorted list
        sorted_key_inclusion=get_inclusion_ith_polygone(i,polygones,n_polygones,bounding_quadrants)    # sorted_key_inclusion is the index of the smallest polygone (in the sorted list)                                                              # containing polygones[i] 
        if sorted_key_inclusion!=-1:
            inclusions[sorted_keys_to_keys[i]]=sorted_keys_to_keys[sorted_key_inclusion]                      # Convert from 

    return inclusions


#Done, Use of function point_projects_in_segment(x,y,x1,y1,x2,y2)
def point_in_polygone(p:Point, index_polygone:int, polygones:list):

    x=p.coordinates[0]      # x coordinate of point p
    y=p.coordinates[1]      # y coordinate of point p
    j=index_polygone        # We name j the index for simplification
    
    """ 
    Then we loop over the segments
    The following is a two state process to find if a point intersects a segment
    """
    
    intersection_cpt=0      # Start a counter for number of intersections with segments

    for s in polygones[j].segments():      #Loop over segments of polygone _prevTab[j]_            
        x1,y1=s.endpoints[0].coordinates          
        x2,y2=s.endpoints[1].coordinates
        """
        Here we see if from the point p, in the horizontal direction, we can intersect the segment p1,p2
        """
        if(x==x1 and x==x2 and y==y1 and y==y2):
            #time_point_in_polygone+=time()-t
            return True
        elif(y1!=y2):
            if y>y1 and y<y2 and (y-y1)*(x2-x1)>=-(y2-y1)*(x1-x): 
                intersection_cpt+=1
            elif  y<y1 and y>y2 and (y-y1)*(x2-x1)<=-(y2-y1)*(x1-x): 
                intersection_cpt+=1
            elif y==y1 and x1>x and y2<y:
                intersection_cpt+=1
            elif y==y2 and x2>x and y1<y:
                intersection_cpt+=1
    if intersection_cpt % 2==1:              #if the counter is odd

        return True  #Then the point is in the polygone possible_polygones[j]

#Done, use of update_list
"""
Takes as parameters : (polygones, n_polygones, i, j) --> (O(1),... O(1))
- The list of polygones : 'polygones'                   
- The number of polygones : 'n_polygones'               
- Checks if polygone i is included in polygone j
"""
time_partial_inclusion=0
def get_inclusion_ith_polygone(i: int,polygones: list,n_polygones: int,bounding_quadrants):
    # Case of the biggest polygone 
    if(i==n_polygones-1):
        #time_get_inclusion_ith_polygone+=time()-t
        return -1
    
    min_i,max_i=bounding_quadrants[0][i],bounding_quadrants[1][i]
    #time_partial_inclusion+=time()-t
    min_j=[0,0]
    max_j=[0,0]

    for j in range(i+1,n_polygones):

        min_j[0]=bounding_quadrants[0][j][0]   
        min_j[1]=bounding_quadrants[0][j][1]
        max_j[0]=bounding_quadrants[1][j][0]
        max_j[1]=bounding_quadrants[1][j][1]

        if (min_i[0]>=min_j[0] and min_i[1]>=min_j[1] and max_i[0]<=max_j[0] and max_i[1]<=max_j[1]):
            included=1
            for p in polygones[i].points :
                if not point_in_polygone(p,j,polygones):
                    included=0
                    break
            if included==1:       
                return j
    return -1

def translater(i,polygone):
    points=polygone.points
    n_points=len(points)
    list_points=[]
    for k in range(i+1,n_points):
        list_points.append(points[k])
    for j in range(0,i+1):
        list_points.append(points[j])
    return Polygon(list_points)



def main(ranges,parameter):
    """
    charge chaque fichier .poly donne
    trouve les inclusions
    affiche l'arbre en format texte
    """
    """for fichier in sys.argv[1:]:
        t=time()
        polygones = txt2Poly(fichier)
        print(len(polygones))
 
        n_polygones=len(polygones)
        sorted_polygones,sorted_keys_to_keys,bounding_quadrants,Swats_all=pretraitement(n_polygones,polygones)
        inclusions = trouve_inclusions(sorted_polygones,sorted_keys_to_keys,bounding_quadrants,Swats_all)
        print(inclusions) 
        print("Time {} ms".format((time()-t)*1000))"""
    times=[]
    for i in range(0,ranges):
        t=time()
        suff="T/test"+str(i)+".poly"
        polygones=read_instance(suff)
        n_polygones=len(polygones)
        sorted_polygones,sorted_keys_to_keys=sort_polygones(n_polygones,polygones)
        bounding_quadrants=find_bounding_quadrants(sorted_polygones,n_polygones)
        inclusions = trouve_inclusions(sorted_polygones,sorted_keys_to_keys,bounding_quadrants)
        times.append(1000*(time()-t))
        print(times[i])
    print("parameter is ",parameter)
    return times

