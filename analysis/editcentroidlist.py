# Jed Diller
# edits lists of centroids
# correlating stars between frames, projecting 2D position to 3D
# return lift of 2 cols of (x,y) points left frame 1 right frame 2 w/ row correlating to point
# 10/24/12

import math
import numpy as np
import copy as cp

def matchstars(centlistA,centlistB,searchradius=25):
    '''starrcorr(): Returns a list of tuples containing two (x,y) touples for matched star 
    positions between frames A and B. The left (x,y) tuple is for frame A, right for frame B
    >>> a = correlateframes(centlistA,centlistB)
    >>> print a[0]
    >>> ((xA,yA),(xB,yB)) # but with numbers''' 
    
    # checks
    if centlistA == [] or centlistB == []: 
        raise RuntimeError('No matched stars between frames, centlistA or centlistB is empty')
            
    if type(centlistA[0]) is not tuple and type(centlistB[0]) is not tuple:            
        raise RuntimeError('matchstars(): type tuple expected inside centroid lists')
        
    # go through list A one at a time, remove matched stars from B
    matchedlist = []
    Bcopy = cp.deepcopy(centlistB) # use copy of centlistB so as not to edit original list
    
    for posA in centlistA:
        matchindex = matchsearch(posA,Bcopy,searchradius) # look for a match in centlistB
        if matchindex: # if there's a match remove matched pos in B and continue on in A
            matchedlist.append((posA,Bcopy[matchindex]))
            Bcopy.remove(Bcopy[matchindex])
                            
    return matchedlist
    
# Supporting funcitons
def matchsearch(posA,centlistB,r):
    '''matchsearch(): returns the index of the position in list B in the rearch radius and 
    closest to posA'''
    index = 0
    matches = []
    currmin = r+1
    currindex = 0
    winningindex = None
    
    for posB in centlistB: 
        x1,y1 = posA
        x2,y2 = posB
        d = dist(x1,x2,y1,y2) 
        
        if d <= r:              # if in search radius
            if d < currmin:     # if distance less than previous match it becomes the new winner
                currmin = d
                winningindex = index
            
        index = index + 1
        
    return winningindex
                        
            
def dist(x1,x2,y1,y2):
    '''Calculates distance between two x,y points'''
    sq1 = (x1-x2)*(x1-x2)
    sq2 = (y1-y2)*(y1-y2)
    return (math.sqrt(sq1 + sq2))
    

# ----------------- 2D to 3D ----------------------
def project3D(centlist,vpix=2160,hpix=2560,plate_scale=6.5,f=150000):
    '''project3D(): given list of centroid pairs ((xA,yA),(xB,yB)) matched between frames, 
    returns list of 3D tuples pairs ((xA,yA,zA),(xB,yB,zB))
    vpix = vertical pixels
    hpix = horizontal pixels
    plate_scale = microns/pixel
    f = focal length in microns
    '''
        
    def pos2Dto3D((xi,yi)):
        '''pos2Dto3D(): returns (x,y,z) given (x,y)'''
        
        # CMOS center
        xp = plate_scale*hpix/2; #x-center [microns]
        yp = plate_scale*vpix/2; #y-center [microns]
        
        ff = f*f
        x = (xp-xi)
        xx = x*x
        y = (yp-yi)
        yy = y*y
        C = 1/math.sqrt(ff + xx + yy)
        
        xv = C*x
        yv = C*y
        zv = C*f

        return xv,yv,zv

    return map(pos2Dto3D,centlist)

'''
# Test this shit
A = [(500,500),(600,600),(700,700),(100,100),(0,0),(1,1),(2560/2,1080)]
B = [(499,499),(550,550),(601,601),(101,101),(701,701),(1,1),(0.1,0.1),(2560/2+1,1081)]
C = matchstars(A,B)
print "A",A
print "B",B
print "C",C
print "len C =", len(C)
print ""

D = project3D(C)
print "D",D
print "len D =",len(D)
'''

