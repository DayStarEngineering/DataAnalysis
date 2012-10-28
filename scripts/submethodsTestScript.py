# Jed Diller
# Script to test subtraction methods
# 12/15/12

import script_setup
from util import imgutil as imgutil
from analysis import submethods as submethods

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
print 'doing subtraction...'
#DRCMimg = submethods.darkcolsub(fullimg)
#CMimg = submethods.colmeansub(img)
#CSMimg = submethods.colsigsub(img)
ix,iy = 1080,1080-10
iw,ih = 4,5
window,(x,y),(cx,cy) = submethods.windowsub(img,(ix,iy),(iw,ih))


# display images
#imgutil.dispimg(DRCMimg)
print 'displaying image...'
#imgutil.dispimg(CMimg,10) # displayed with an optional view factor of 10
imgutil.dispimg(window)
#imgutil.dispimg(img[100:100+int(5*2.5)+1][:,100:100+int(4*2.5)+1])

# save images
#imgutil.saveimg(DRCMimg,DRCMoutfile)
#imgutil.saveimg(CMimg,CMoutfile,10) # saved with an optional view factor of 10

