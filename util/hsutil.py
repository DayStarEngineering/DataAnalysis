import numpy as np
import pylab as plab
import datetime as dt
import os

# Globals:
def load(name):
    ''' This function loads a health and status file or entire directory of files into a 2-D array given a filename '''
    
    def loadhs(fname):
        hs1 = np.loadtxt(fname, dtype='string', usecols = range(0,37))
        hs2 = np.loadtxt(fname, dtype='string', usecols = range(38,48) )
        
        # Convert to hex to decimal:
        for (x,y), value in np.ndenumerate(hs2):
            hs2[x,y] = int(value,16);
        #print hs2
        return hstack([hs1,hs2])
    
    if(os.path.isfile(name)):
        hs = loadhs(name)
        return hs
    elif(os.path.isdir(name)):
        hs = [];
        for file in os.listdir(name):
            print str(name + file)
            hs.append(loadhs(str(name + file)))
        return vstack(hs)
    else:
        return []
    
def plot(hs,colnum):
    ''' This function plots health and status data given a colnum '''
    t = []
    for time in hs[:,0]:
        date = dt.datetime.fromtimestamp(float(time))
        t.append(date.hour + date.minute/60.0 + date.second/3600.0)
    
    plab.figure()
    plab.plot(t,hs[:,colnum], linewidth=2.0)
    plab.xlabel('Time (hr)');
    plab.show()

