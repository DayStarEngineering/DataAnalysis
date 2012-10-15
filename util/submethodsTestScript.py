# Jed Diller
# Script to test subtraction methods
# 12/10/12

from imgutil import loadimg, saveimg
from colsub import darkcolsub

datpic = 'img_1348355543_717188_00015_00000_0.dat'
datimg = loadimg(datpic)
subdimg = darkcolsub(datimg)
saveimg(subdimg,'subdimg.tif')


