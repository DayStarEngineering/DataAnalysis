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

###################################################################################
# Main
###################################################################################
# Load the image:
db = database.Connect()
fnames = db.find('raw_fn','burst_num = 145 and gain = 1').raw_fn.tolist()
fname = fnames[1]
print 'Opening: ' + fname
image = imgutil.loadimg(fname,from_database=True)

# Find star centroids:
(centers) = centroid.findstars(image,debug=True)
centroids = centroid.imgcentroid(image,centers)

# Display image with stars circled:
if centroids:
    imgutil.circstars(image,centroids,1,viewfactor=1)
else:
    print 'Oopsies... we found ZERO centroids. Now how do you feel?'
