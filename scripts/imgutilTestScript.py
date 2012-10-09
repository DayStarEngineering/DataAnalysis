# Jed Diller
# Script to load and save a tiff and dat file
# 10/8/12

import script_setup
from util import imgutil as imgutil
# from util import *

tifpic = 'img_1348355543_717188_00015_00000_0_gray.tif'
datpic = 'img_1348355543_717188_00015_00000_0.dat'

imgutil.saveimg(imgutil.loadimg(tifpic),'tifpicsaved.tif')
imgutil.saveimg(imgutil.loadimg(datpic),'datpicsaved.tif')

