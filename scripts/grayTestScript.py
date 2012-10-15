# Jed Diller
# Script to test out gray conversion
# 10/14/12

import script_setup
from util import imgutil as imgutil

# define in and out files
datpicIN = '../testimgdir/img_1348355543_717188_00015_00000_0.dat'
g2bcnvdatOUT = '../testimgdir/grayconvdat2.tif'


ldddat = imgutil.loadimg(datpicIN)
imgutil.saveimg(ldddat,g2bcnvdatOUT)

#cnvdat = imgutil.gimg2bimg(ldddat)
#imgutil.saveimg(cnvdat,g2bcnvdatOUT)

