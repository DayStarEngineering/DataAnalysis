# File: IMG_TEST.PY
# Author: Nick Truesdale 
# Date: Oct 29, 2012
#
# Description:

# Initial Imports
import sys, os

# Get the directory above the directory this file is in
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# More imports
import numpy as np
import copy as cp
import time

# Addtl imports for main script
from util import imgutil as imgutil
from analysis import submethods as sm
from analysis import centroid as centroid
from analysis import flatfield as flat

# Load the image:
image1 = imgutil.loadimg('/home/sticky/Daystar/img_1348368011_459492_00146_00000_1.dat')
image2 = imgutil.loadimg('/home/sticky/Daystar/img_1348355543_717188_00015_00000_0.dat', load_full=True)

#img = sm.colmeansub(image)
#img2 = sm.colmeansub(image2)
#img3 = sm.darkcolsub(image2)


#### Nighttime Test ####
t1 = time.time()
img1 = flat.ImgNormalize(image2, Method="robustmean", source="image")

t2 = time.time()
img2 = flat.NormalizeColumnGains(image2, Method="robustmean", JustDark=0)

t3 = time.time()

print t2-t1
print t3-t2

#img3 = sm.colmeansub(img2)
#img4 = sm.colmeansub(image2)

#img3 = np.delete(img3, np.r_[1080:1080+32], 0)

#imgutil.dispimg(image2,2)
imgutil.dispimg(sm.colmeansub(img1),3)
imgutil.dispimg(sm.colmeansub(img2),3)
#imgutil.dispimg(img3,3)



