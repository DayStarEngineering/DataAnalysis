# Jed Diller
# Script to load and save a tiff and dat file
# 10/8/12

from utilities import loadimg, saveimg

tifpic = 'img_1348355543_717188_00015_00000_0_gray.tif'
datpic = 'img_1348355543_717188_00015_00000_0.dat'

saveimg(loadimg(tifpic),'tifpicsaved.tif')
saveimg(loadimg(datpic),'datpicsaved.tif')

