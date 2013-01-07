# Jed Diller
# analysis plots

import pylab as pl
import numpy as np
import matplotlib.pyplot as plt
        
def starpaths(image, centroids, quiet=False, fname=False, radius=10):
    '''
    Plot the path of stars on top of an image
    '''
    fig = pl.figure()
    fig = pl.gray()
    fig = pl.imshow(image, cmap=None, norm=None, aspect=None,
                interpolation='nearest', vmin=0, vmax=2048, origin='upper')

    for centlist in centroids:
        for pos in centlist:
            circ = pl.Circle(tuple(pos), radius, ec='r', fill=False)
            fig = pl.gca().add_patch(circ)
    
    if not quiet:
        fig = pl.show()
    if fname:
        pl.savefig(fname)

def colorgen():
    color = ['b','c','r','g','m','y']
    while True:
        for c in color:
            yield c

def starnum(numstars, quiet=False, fname=False):
    '''
    Plot the number of stars as a function of
    frame number
    '''
    fig = plt.figure()
    plt.plot(numstars, 'r-')
    plt.ylabel('Number of Stars')
    plt.xlabel('Frame Number')
    plt.title('Number of Stars Centroided Per Frame')
    
    if not quiet:
        plt.show()
    if fname:
        plt.savefig(fname)
    
