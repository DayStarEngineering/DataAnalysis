# Jed Diller
# Script to test subtraction methods
# 12/15/12

import script_setup
from util import imgutil as imgutil
from util import submethods as submethods

import numpy as np

# image path setup
datpic = '../testimgdir/img_1348355543_717188_00015_00000_0.dat'
#DRCMoutfile = '../testimgdir/DRCMsubdimg.tif'   # dark row column average subtraction
#CMoutfile = '../testimgdir/CM10xsubdimg.tif'       # column average subtraction
#CSMoutfile = '../testimgdir/CM10xsubdimg.tif'       # column sigma range average subtraction

# load
print 'loading image...'
img = imgutil.loadimg(datpic)
#fullimg = imgutil.loadimg(datpic,'full')

# do subtractions
print 'doing sigma subtraction...'
#DRCMimg = submethods.darkcolsub(fullimg)
CMimg = submethods.colmeansub(img)
#CSMimg = submethods.colsigsub(img)

# display images
#imgutil.dispimg(DRCMimg)
print 'displaying image...'
imgutil.dispimg(CMimg,10) # displayed with an optional view factor of 10

# save images
#imgutil.saveimg(DRCMimg,DRCMoutfile)
#imgutil.saveimg(CMimg,CMoutfile,10) # saved with an optional view factor of 10

