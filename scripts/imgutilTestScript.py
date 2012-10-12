# Jed Diller
# Script to load and save a tiff and dat file
# 10/8/12

import script_setup
from util import imgutil as imgutil
# from util import *

# image in paths
tifpicIN = 'C:/Users/Jed/Documents/DayStarSummer/PythonScripts/img_1348355543_717188_00015_00000_0_gray.tif'
datpicIN = 'C:/Users/Jed/Documents/DayStarSummer/PythonScripts/img_1348355543_717188_00015_00000_0.dat'
#image out path
tifpicOUT = 'C:/Users/Jed/Documents/DayStarSummer/PythonScripts/tifpicsaved.tif'
datpicOUT = 'C:/Users/Jed/Documents/DayStarSummer/PythonScripts/datpicsaved.tif'

loadedtif = imgutil.loadimg(tifpicIN)
loadeddat = imgutil.loadimg(datpicIN)

imgutil.saveimg(loadedtif,tifpicOUT)
imgutil.saveimg(loadeddat,datpicOUT)
