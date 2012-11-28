#
# Script name: master_script.py
# Author: Kevin Dinkel
# Created: 10/2/2012
# Description: This script takes a list of filenames, finds & centroids stars in 
# the files, calculates an attitude quaternion with each file, and utimately produces
# plots of roll, pitch, and yaw of the DayStar system over time.
#

###################################################################################
# Must import this for every script in this directory in order to use our modules!!
###################################################################################
import script_setup

###################################################################################
# Import modules from analysis (the correct way to do it):
###################################################################################
from analysis import centroid as centroid
from analysis import editcentroidlist as starmatcher
from analysis import qmethod as qmethod
from analysis import plots as plots
from analysis import submethods as sm
from analysis import tracking
from analysis import flatfield
from util import imgutil as imgutil
from db import RawData as database
from itertools import izip, islice
import cPickle as pickle
import time
import numpy as np
import pylab as pl
import copy as cp

###################################################################################
# Functions
###################################################################################
def getCentroids(fnames):
    '''
    From a list of filenames, load the filenames, clean up the images, find stars
    in the images, and return a list of centroids and the number of stars found in
    each image.
    '''
    
    n = len(fnames)
    centroids = []
    numstars = []
    for count,fname in enumerate(fnames):
        # Display status:
        print 'Loading and centroiding filename ' + str(count+1) + ' of ' + str(n) + '.'
        
        # Load the image:
        image = imgutil.loadimg(fname,from_database=True)
        
        # Clean up image:
        image = flatfield.NormalizeColumnGains(image,Plot=0)
        
        # Find stars in image:
        centers = centroid.findstars(image)
        
        # Get centroids:
        centroids.append(centroid.imgcentroid(image,centers))
        
        # store number of stars centroided per frame
        numstars.append(len(centroids[count]))
        
    return centroids,numstars
 
def getQuaternions(centroids):
    '''
    From a list of centroids found in successive image files, return a list of quaternions
    representing the rotations between the image files
    '''
    print 'Matching stars.'
    matched_centroids = []
    centroid_pairs = []
    nummatchstars = []
    search_radius = 75
    for count,(centlistA,centlistB) in enumerate(izip(centroids, islice(centroids, 1, None))):
        
        print 'Comparing centroid list: ' + str(count+1) + ' to ' + str(count+2) + '.'
        pair = starmatcher.matchstars(centlistA,centlistB,search_radius)
        centroid_pairs.append(pair)
        matched_centroids.append(zip(*pair)[0])
        
        nummatches = len(centroid_pairs[count])
        if nummatches == 0:
            raise RuntimeError('Frames ' + str(count+1) + ' and ' + str(count+2) + ' not matched.')
        else:    
            nummatchstars.append(nummatches)

    print 'Mean number of matched stars:', np.mean(nummatchstars)

    print 'Find quaternions.'
    quats = []
    for (count,matched) in enumerate(centroid_pairs):
        # Project 2d vectors into 3d space:
        Vi2d,Vb2d = zip(*matched)
        Vi = starmatcher.project3D(Vi2d)
        Vb = starmatcher.project3D(Vb2d)
        # Run the Q-Method:
        quats.append(qmethod.qmethod(Vi,Vb))
     
    return quats,matched_centroids,nummatchstars

###################################################################################
# Set-up
###################################################################################
pl.close('all')

###################################################################################
# Main
###################################################################################
# Analysis Details:
# Daytime Burst: 15 (low gain)
# Nighttime Burst: 172 = 30ms (avg=15), 175 = 50ms (avg=32), 181 works too

# Which plots do you want brah?
plot = True

# Get desired filenames from database:
print 'Loading filenames from database.'
db = database.Connect()
fnames = db.select('select raw_fn from rawdata where burst_num = 172 limit 50').raw_fn.tolist()
#fnames = db.find('raw_fn','burst_num = 175 limit 5').raw_fn.tolist()

        
print 'Starting analysis.'
tic = time.clock()

# Get centroids from each file:
centroids,numstars = getCentroids(fnames)
    
print 'Mean number of stars found: ', np.mean(numstars)

# Pickle the found centroids for safekeeping :)
# To load later: centroids = pickle.load( open( "saved_centroids.p", "rb" ) )
pname = "saved_centroids_" + time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime()) + ".pk"
pickle.dump( centroids, open( pname, "wb" ) )
centroids = pickle.load( open( pname, "rb" ) )

# Get quaternions from our centroids:
quats,matched_centroids,nummatchstars = getQuaternions(centroids)


print 'Find roll, pitch, and yaw variances.'
# Get the roll, pitch, yaw variances:
delta_t = 0.1 # s
motion_frequency = 1.5 # Hz
var_r,var_p,var_y = tracking.FindVariance(quats,delta_t=delta_t,motion_frequency=motion_frequency,plot=plot)
toc = time.clock()
print 'RPY Variances: ',var_r,var_p,var_y
print 'Total time: ' + str(toc - tic) + ' s'
 
#############################################################
# Plots:
#############################################################
if plot:
    image0 = imgutil.loadimg(fnames[0],from_database=True)
    plots.starnum(numstars)
    plots.starnum(nummatchstars)
    plots.starpaths(image0,centroids)
    plots.starpaths(image0,matched_centroids)
    
