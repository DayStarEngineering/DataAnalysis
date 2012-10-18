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

# test new load with optional cropping
fulldat = imgutil.loadimg(datpicIN,'full')
imgutil.dispimg(fulldat)

# save loaded pictures
#imgutil.saveimg(loadedtif,tifpicOUT)
#imgutil.saveimg(loadeddat,datpicOUT)
