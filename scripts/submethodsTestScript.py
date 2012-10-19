# Jed Diller
# Script to test subtraction methods
# 12/15/12

import script_setup
from util import imgutil as imgutil
from util import submethods as submethods

import numpy as np

datpic = '../testimgdir/img_1348355543_717188_00015_00000_0.dat'
DRCMoutfile = '../testimgdir/DRCMsubdimg.tif'   # dark row column average subtraction
CMoutfile = '../testimgdir/CMsubdimg.tif'       # column average subtraction

# load
img = imgutil.loadimg(datpic)
fullimg = imgutil.loadimg(datpic,'full')

# do subtractions
DRCMimg = submethods.darkcolsub(fullimg)
CMimg = submethods.colmeansub(img)

# display images
imgutil.dispimg(DRCMimg)
imgutil.dispimg(CMimg,10) # displayed with view factor of 10

# save images
#imgutil.saveimg(DRCMimg,DRCMoutfile)
#imgutil.saveimg(CMimg,CMoutfile)

