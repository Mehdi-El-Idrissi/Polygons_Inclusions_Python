#!/usr/bin/env python3
"""
fichier principal pour la detection des inclusions.
ce fichier est utilise pour les tests automatiques.
attention donc lors des modifications.
"""
import sys
from tycat import read_instance


from geo.point import Point
from geo.tycat import tycat
from geo.polygon import Polygon
from geo.quadrant import Quadrant
from geo.segment import Segment


def dichotomy_mod(sorted_areas: list,n_polygones: int,area: float):
    a=0
    b=n_polygones-1
    m=(b+a)//2
    while(a!=b):
        m=(b+a)//2
        if(sorted_areas[m][0]<area):
            a=m+1
        elif(sorted_areas[m][0]==area):
            return m
        else:
            b=m
    m=(b+a)//2
    if sorted_areas[m][0]>area:
        return m-1
    elif sorted_areas[m][0]<area:
        return m
    return m

def mergeSort_rev(myList:list,rev_hash:dict):
    if len(myList) > 1:
        mid = len(myList) // 2
        left = myList[:mid]
        right = myList[mid:]

        mergeSort(left)
        mergeSort(right)

        i = 0
        j = 0

        k = 0
        
        while i < len(left) and j < len(right):
            if left[i][0] <= right[j][0]:
              myList[k] = left[i]
              rev_hash[left[i][0]]=k
              i += 1
            else:
                myList[k] = right[j]
                rev_hash[right[j][0]]=k
                j += 1

            k += 1

        while i < len(left):
            myList[k] = left[i]
            rev_hash[left[i][0]]=k
            i += 1
            k += 1

        while j < len(right):
            myList[k]=right[j]
            rev_hash[right[j][0]]=k
            j += 1
            k += 1

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


def swatting(points:list): 

    iter_points=iter(points)
    p0=next(iter_points,None)
    p1=next(iter_points,None)
    Swats=[[p0.coordinates[1],[]]]     
    ys_in={p0.coordinates[1]}

    while p1!=None:
        p0=p1         
        p1=next(iter_points,None)              
        if p0.coordinates[1] not in ys_in:
            ys_in.add(p0.coordinates[1])
            Swats.append([p0.coordinates[1],[]])
    rev_hash={}
    mergeSort_rev(Swats,rev_hash) 
    iter2=iter(points)
    p0=next(iter2,None)
    p1=next(iter2,None)
    stop=0
    while p1!=None:
        y1,y2=p0.coordinates[1],p1.coordinates[1]
        if y1!=y2:
            i_min,i_max=rev_hash[min(y1,y2)],rev_hash[max(y1,y2)]          
            for i in range(i_min,i_max):
                Swats[i][1].append([p0,p1])                               
        if stop==1:
            p1=None
        p0=p1
        if stop==0:
            p1=next(iter2,None)                 
        if(p1==None and stop==0):
            stop=1
            p1=points[0]
    return Swats
    
def pretraitement(n_polygones: int,polygones: list):


    sorted_areas_with_keys=[]    

    sorted_polygones=[0]*n_polygones      

    sorted_keys_to_keys=[0]*n_polygones

    Swats_all=[0]*n_polygones
    min = [0]*n_polygones 
    max = [0]*n_polygones

    for i in range(0,n_polygones):             
        sorted_areas_with_keys.append([abs(polygones[i].area()),int(i)])    
    mergeSort(sorted_areas_with_keys)            

    for i in range(0,n_polygones):              
        sorted_keys_to_keys[i]=sorted_areas_with_keys[i][1]
        sorted_polygones[i]=polygones[sorted_areas_with_keys[i][1]]
        Swats_all[i]=swatting(sorted_polygones[i].points)
        min[i],max[i]=(sorted_polygones[i].bounding_quadrant()).get_arrays()    


    return sorted_polygones,sorted_keys_to_keys,[min,max],Swats_all

def trouve_inclusions(polygones: list,sorted_keys_to_keys:list,bounding_quadrants:list,Swats_all:list):
   
    n_polygones=len(polygones)               
    inclusions=[-1]*n_polygones
    
    for i in range(n_polygones-1,-1,-1):             
        sorted_key_inclusion=get_inclusion_ith_polygone(i,polygones,n_polygones,bounding_quadrants,Swats_all)  
                                                                               
        if sorted_key_inclusion!=-1:
            inclusions[sorted_keys_to_keys[i]]=sorted_keys_to_keys[sorted_key_inclusion]               
    return inclusions
def point_in_polygone(p:Point, index_polygone:int, polygones:list,Swats_all:list):
    x=p.coordinates[0]     
    y=p.coordinates[1]     
    j=index_polygone       
    intersection_cpt=0      
    swat=dichotomy_mod(Swats_all[j],len(Swats_all[j]),y)
    for s in Swats_all[j][swat][1]:
        x1,y1=s[0].coordinates          
        x2,y2=s[1].coordinates
        if(x==x1 and y==y1) or (x==x2 and y==y2):
            return True
        if y>y1 and y<y2 and (y-y1)*(x2-x1)>=-(y2-y1)*(x1-x): 
            intersection_cpt+=1
        elif  y<y1 and y>y2 and (y-y1)*(x2-x1)<=-(y2-y1)*(x1-x): 
            intersection_cpt+=1
        elif y==y1 and x1>x:
            intersection_cpt+=1
        elif y==y2 and x2>x:
            intersection_cpt+=1
    
    if intersection_cpt % 2==1:              
        return True 

    return False

def get_inclusion_ith_polygone(i: int,polygones: list,n_polygones: int,bounding_quadrants:list,Swats_all:list):
    if(i==n_polygones-1):
        return -1
    
    min_i,max_i=bounding_quadrants[0][i],bounding_quadrants[1][i]

    for j in range(i+1,n_polygones):

        if min_i[0]>=bounding_quadrants[0][j][0] and min_i[1]>=bounding_quadrants[0][j][1] and max_i[0]<=bounding_quadrants[1][j][0] and max_i[1]<=bounding_quadrants[1][j][1]:
            included=1
            for p in polygones[i].points :
                if not point_in_polygone(p,j,polygones,Swats_all):
                    included=0
                    break
            if included==1:       
                return j
    return -1

def main():
    """
    charge chaque fichier .poly donne
    trouve les inclusions
    affiche l'arbre en format texte
    """
    for fichier in sys.argv[1:]:
        polygones = read_instance(fichier)
        n_polygones=len(polygones)
        sorted_polygones,sorted_keys_to_keys,bounding_quadrants,Swats_all=pretraitement(n_polygones,polygones)
        inclusions = trouve_inclusions(sorted_polygones,sorted_keys_to_keys,bounding_quadrants,Swats_all)
        print(inclusions) 
    

if __name__ == "__main__":
    main() 

