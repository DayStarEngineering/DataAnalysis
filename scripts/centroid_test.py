#
# Script name: centroid_test.py
# Author: Kevin Dinkel
# Created: 10/2/2012
# Description: This script centroids some stars.
#
###################################################################################
# Must import this for every script in this directory in order to use our modules!!
###################################################################################
import script_setup

###################################################################################
# Import modules from analysis (the correct way to do it):
###################################################################################
from analysis import centroid as centroid
from util import imgutil as imgutil
from util import submethods as subm
from db import RawData as database
from analysis import flatfield

###################################################################################
# Main
###################################################################################
# Load the image:
db = database.Connect()
fnames = db.select('select raw_fn from rawdata where burst_num = 172 limit 2').raw_fn.tolist()
fname = fnames[0]
print 'Opening: ' + fname
image = imgutil.loadimg(fname,from_database=True)

# Clean-up the image:
image = flatfield.NormalizeColumnGains(image,Plot=0,Wiener=1)

# Find star centroids:
(centers) = centroid.findstars(image,zreject=3, zthresh=3.15, min_pix_per_star=6, max_pix_per_star=60, oblongness=1.5,debug=True)
centroids = centroid.imgcentroid(image,centers)

# Display image with stars circled:
if centroids:
    imgutil.circstars(image,centroids,20,viewfactor=1)
else:
    print 'Oopsies... we found ZERO centroids. Now how do you feel?'
