# File: IMG_TEST.PY
# Author: Nick Truesdale 
# Date: Oct 29, 2012
#
# Description:


# Imports
import sys
sys.path.append("../")

# More imports
import numpy as np
import copy as cp

# Addtl imports for main script
from util import imgutil as imgutil
from analysis import submethods as sm
from analysis import centroid as centroid

# Load the image:
image = imgutil.loadimg('/home/sticky/Daystar/img_1348368011_459492_00146_00000_1.dat')
image2 = imgutil.loadimg('/home/sticky/Daystar/img_1348355543_717188_00015_00000_0.dat')

img = sm.colmeansub(image)
img2 = sm.colmeansub(image2)

imgutil.dispimg(img,3)
imgutil.dispimg(img2,3)




