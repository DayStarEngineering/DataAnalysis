# Jed Diller
# correlating stars between frames
# return lift of 2 cols of (x,y) points left frame 1 right frame 2 w/ row correlating to point
# 10/24/12

import math

def matchstars(centlistA,centlistB,searchradius = None):
    '''starrcorr(): Returns a list of tuples containing two (x,y) touples for matched star 
    positions between frames A and B. The left (x,y) tuple is for frame A, right for frame B
    >>> a = correlateframes(centlistA,centlistB)
    >>> print a[0]
    >>> ((xA,yA),(xB,yB)) # but with numbers''' 
    
    if type(centlistA[0]) is not tuple and type(centlistB[0]) is not tuple:            
        raise RuntimeError('correclateframes()')

    if searchradius == None:
        searchradius = 50   # default search radius
        
    # go through list A one at a time, remove matched stars from B
    matchedlist = []
    Bcopy = centlistB # use copy of centlistB so as not to edit original list
   
    for posA in centlistA:
        matchindex = matchsearch(posA,centlistB,searchradius) # look for a match in centlistB
        if matchindex != None: # if there's a match remove matched pos in B and continue on in A
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
    

