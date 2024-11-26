#!/usr/bin/env python3
"""
fichier principal pour la detection des inclusions.
ce fichier est utilise pour les tests automatiques.
attention donc lors des modifications.
"""
import sys
from tycat import read_instance
from numpy import inf
from time import time

from geo.tycat import tycat
from geo.point import Point
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

def areas_sorted(n_polygones,polygones):
    areas=[]
    for i in range(0,n_polygones):
        areas.append([abs(polygones[i].area()),i])
    mergeSort(areas)
    return areas
def trouve_inclusions(polygones):
    """
    renvoie le vecteur des inclusions
    la ieme case contient l'indice du polygone
    contenant le ieme polygone (-1 si aucun).
    (voir le sujet pour plus d'info)
     
    """

    n_polygones=len(polygones)                  #number of polygones O(n_polygones)
    inclusions=[]
    for k in range(0,n_polygones):
        inclusions.append(-1)
    for i in range(0,n_polygones):              #Loop over polygones to get the inclusions of each one of them
        possible_polygones=single_polygone_inclusions(i,polygones,n_polygones)
        single_inclusion(i,possible_polygones,polygones,inclusions)

    return inclusions

#duration_segments=0
#duree_boucle=0
#Done, Use of function point_projects_in_segment(x,y,x1,y1,x2,y2)
def point_in_polygone(p, index_polygone, polygones,i):

    #duree=time()-t_0
    #duration_segments+=duree
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

     
#Done, Use of function point_in_polygone(p, index_polygone, polygones)
"""
To change update_list()
"""
def update_list(p,polygones,possible_polygones,i):
    new_polygones=[]
    polygones_cpt=0
    for j in range(0,len(possible_polygones)):     #Loop over possible polygones
        if point_in_polygone(p, possible_polygones[j], polygones,i):
            new_polygones.append(possible_polygones[j])
            polygones_cpt+=1
    return new_polygones,polygones_cpt

#Done, use of update_list
"""
Takes as parameters : (polygones, n_polygones, i, j) --> (O(1),... O(1))
- The list of polygones : 'polygones'                   
- The number of polygones : 'n_polygones'               
- Checks if polygone i is included in polygone j
"""
def single_polygone_inclusions(i,polygones,n_polygones):          
    possible_polygones=list(range(0,i))+list(range(i+1,n_polygones))
    for p in polygones[i].points:
        # Update the possible_polygones list
        possible_polygones,polygones_cpt = update_list(p,polygones,possible_polygones,i)
        if polygones_cpt==0:
            return []
    return possible_polygones

#Done
"""   
- In the end we find a list of polygones that contain the i-th polygone
to find the smallest, we iterate over that list and use the quadrants, to compare
       
- With N_inc mean number of inclusions, we need O(N_inc) for each polygone to find the one with
the smallest quadrant
"""
#duration_2=0
def single_inclusion(i,possible_polygones,polygones,inclusions):
    #global duration_2
    #t_0=time()
    if len(possible_polygones)>0:
        index_min_polygone=0                        #Initialization of the index of the polygone with the smallest quadrant
        min_area=inf
        for q in range(0,len(possible_polygones)):          #Find the polygone with the smallest quadrant.
            index_loop_polygone=possible_polygones[q]       #Index of the polygone in the loop
            #polygones[possible_polygones[q]]  #polygone in the loop
            loop_area=abs(polygones[possible_polygones[q]].area())
            if loop_area<=min_area:
                index_min_polygone=index_loop_polygone      #update the index of the polygone with the smallest quadrant
                min_area=loop_area      
        inclusions[i]=index_min_polygone  
    #duree=time()-t_0
    #duration_2+=duree
    

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
        inclusions = trouve_inclusions(polygones)
        times.append(1000*(time()-t))
        print(times[i])
    print("parameter is ",parameter)
    return times

