###################################################################################
# Must import this for every script in this directory in order to use our modules!!
###################################################################################
import script_setup

###################################################################################
# Import modules from analysis (the correct way to do it):
###################################################################################
from analysis import centroid as centroid
from db import RawData as database
from analysis import submethods as sm
from util import imgutil as imgutil
import pylab as pl

# ----------------- Plot Different Centroid Methods on Same Star-------------------------------
print 'saving plots of centroid methods on same star'
db = database.Connect()
name = db.select('select raw_fn from rawdata where burst_num = 172 limit 1').raw_fn.tolist()[0]
img = imgutil.loadimg(name,from_database=True)
# find good star
centers = centroid.findstars(img)
print centers
goodstar = []
goodstar.append(centers[10])
#goodstar = list((tuple(centers[10])) # good centroid at about 1417,275

(x,y) = goodstar[0][0]
(w,h) = goodstar[0][1]

centroid_iwc   = centroid.imgcentroid(img, goodstar, method="iwc")
centroid_cog   = centroid.imgcentroid(img, goodstar, method="cog")
centroid_gauss = centroid.imgcentroid(img, goodstar, method="gauss")
        
(frame, (xframe,yframe), frame_centroid) = sm.windowsub(img, (x,y), (w,h), neg=True, scale=1)

cents = []
cents.append((centroid_iwc[0][0]-xframe,centroid_iwc[0][1]-yframe)) 
cents.append((centroid_cog[0][0]-xframe,centroid_cog[0][1]-yframe)) 
cents.append((centroid_gauss[0][0]-xframe,centroid_gauss[0][1]-yframe)) 
print cents

pl.figure()
pl.gray()
pl.imshow(frame, cmap=None, norm=None, aspect=None,
            interpolation='nearest', vmin=0, vmax=2048, origin='upper')

radius = 1 
#iwc            
color = 'r'
circ = pl.Circle(cents[0], radius, ec=color, fc=color, fill=False)
pl.gca().add_patch(circ)
#cog            
color = 'g'
circ = pl.Circle(cents[1], radius, ec=color, fc=color, fill=False)
pl.gca().add_patch(circ)
#cog            
color = 'b'
circ = pl.Circle(cents[2], radius, ec=color, fc=color, fill=False)
pl.gca().add_patch(circ)

# actually display it
pl.show()
