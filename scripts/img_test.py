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
image = imgutil.loadimg('/home/sticky/Daystar/day1.dat')
#image = imgutil.loadimg('/home/sticky/Daystar/img_1348355543_717188_00015_00000_0.dat', 
#                        load_full=True)
#image = imgutil.loadimg('/home/sticky/Daystar/img_1348370070_656182_00172_00000_1.dat')


# Apply flatfield
img1 = flat.ImgNormalize(image, Method="mean", source="image")
#img1 = flat.ImgNormalize(img1, Method="mean", source="image")
img2 = sm.colmeansub(image)

# Find stars
centers = centroid.findstars(img1, zreject=3, zthresh=3.0, zpeakthresh=4, min_pix_per_star=6, max_pix_per_star=60, oblongness=5,debug=False)


C = centroid.imgcentroid(image,centers)



#img3 = sm.colmeansub(img2)
#img4 = sm.colmeansub(image2)

#img3 = np.delete(img3, np.r_[1080:1080+32], 0)

#imgutil.dispimg(image,1)
#imgutil.dispimg(img1,1)
#imgutil.dispimg(img2,6)

#imgutil.dispimg(sm.bgsub(img1), 6)
#imgutil.dispimg(sm.colmeansub(img1), 6)

imgutil.circstars(sm.colmeansub(img1), C, viewfactor=3)



