# Jed Diller
# Script to test subtraction methods
# 12/10/12

import script_setup
from util import imgutil as imgutil
from util import submethods as submethods

datpic = '../testimgdir/img_1348355543_717188_00015_00000_0.dat'
outfile = '../testimgdir/subdimg.tif'

datimg = imgutil.loadimg(datpic)

subdimg = submethods.darkcolsub(datimg)

imgutil.saveimg(subdimg,outfile)


