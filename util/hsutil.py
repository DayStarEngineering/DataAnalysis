import numpy as np
from pylab import *
import datetime as dt
import os

# Globals:
def load(name):
    ''' This function loads a health and status file or entire directory of files into a 2-D array given a filename '''
    if(os.path.isfile(name)):
        hs = np.loadtxt(name)
        return hs
    elif(os.path.isdir(name)):
        hs = np.empty(shape=(1,48));
        for file in os.listdir(name):
            print hs
            print np.loadtxt(str(name + file))
            np.column_stack((hs,np.loadtxt(str(name + file))))
        return hs
    else:
        return []
    
def plotme(hs,colnum):
    ''' This function plots health and status data given a colnum '''
    t = []
    for time in hs[:,0]:
        date = dt.datetime.fromtimestamp(time)
        t.append(date.hour + date.minute/60.0 + date.second/3600.0)
    print t
        
    plot(t,hs[:,colnum], linewidth=2.0)
    show()

