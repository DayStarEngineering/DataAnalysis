# Jed Diller
# analysis plots

import pylab as pl
import numpy as np
import matplotlib.pyplot as plt

def starpaths(image0,centroids,savename='../../Papers/IEEE/Figures/starpaths.png'):
    fig = pl.figure()
    fig = pl.gray()
    fig = pl.imshow(image0, cmap=None, norm=None, aspect=None,
                interpolation='nearest', vmin=0, vmax=2048, origin='upper')
    radius = 10
    color = 'r'
    for centlist in centroids:
        for pos in centlist:
            circ = pl.Circle(tuple(pos), radius, ec=color, fill=False)
            fig = pl.gca().add_patch(circ)
    #fig = pl.show()
    fig = pl.savefig(savename)

def starnum(numstars,savename='../../Papers/IEEE/Figures/numstars.png'):
    fig = plt.figure()
    plt.plot(numstars, 'r-')
    plt.ylabel('Number of Stars')
    plt.xlabel('Frame Number')
    plt.title('Number of Stars Centroided Per Frame')
    #plt.show()
    plt.savefig(savename)
    plt.close()
    
    
    
