# Jed Diller
# Script to test subtraction methods
# 12/15/12

import script_setup
from util import imgutil as imgutil
from util import submethods as submethods

datpic = '../testimgdir/img_1348355543_717188_00015_00000_0.dat'
DRCMoutfile = '../testimgdir/DRCMsubdimg.tif'   # dark row column average subtraction
CMoutfile = '../testimgdir/CMsubdimg.tif'       # column average subtraction

# load
datimg = imgutil.loadimg(datpic)

# do subtractions
DRCMimg = submethods.darkcolsub(datimg)
CMimg = submethods.colmeansub(datimg)

# save images
imgutil.saveimg(DRCMimg,DRCMoutfile)
imgutil.saveimg(CMimg,CMoutfile)

