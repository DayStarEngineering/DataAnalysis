# Jed Diller
# Script to load and save a tiff and dat file
# 10/8/12

import script_setup
from util import imgutil as imgutil
# from util import *

# image in paths
#tifpicIN = '../testimgdir/img_1348355543_717188_00015_00000_0_gray.tif'
datpicIN = '../testimgdir/img_1348355543_717188_00015_00000_0.dat'
#image out path
#tifpicOUT = '../testimgdir/tifpicsaved.tif'
datpicOUT = '../testimgdir/datpicsaved.tif'

#loadedtif = imgutil.loadimg(tifpicIN)
loadeddat = imgutil.loadimg(datpicIN)

# display loaded dat
#imgutil.dispimg(loadedtif)
imgutil.dispimg(loadeddat)

# try out new centroids display
cents = [(0,0),(100.0,100.0),(500.5,500.5),(700,700),(1200,1200),(1500.5,1500.5),(2000,2000)]
radius = 50
imgutil.circstars(loadeddat,cents,radius)


# test new load with optional cropping
#fulldat = imgutil.loadimg(datpicIN,'full')
#imgutil.dispimg(fulldat)

# save loaded pictures
#imgutil.saveimg(loadedtif,tifpicOUT)
#imgutil.saveimg(loadeddat,datpicOUT)
