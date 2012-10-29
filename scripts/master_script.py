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
from util import imgutil as imgutil
from db import RawData as database
from itertools import izip, islice
import cPickle as pickle
import time
import numpy as np
import pylab as pl
###################################################################################
# Main
###################################################################################
# Analysis Details:
# Daytime Burst: 15 (low gain)
# Nighttime Burst: 172 = 30ms (avg=15), 175 = 50ms (avg=32), 181 works too

# Get desired filenames from database:
db = database.Connect()
fnames = db.select('select raw_fn from rawdata where burst_num = 172 limit 3').raw_fn.tolist()
#fnames = db.find('raw_fn','burst_num = 175 limit 5').raw_fn.tolist()
n = len(fnames)

tic = time.clock()
print 'Starting analysis.'
centroids = []
numstars = []
for count,fname in enumerate(fnames):
    # Display status:
    print 'Loading and centroiding filename ' + str(count+1) + ' of ' + str(n) + '.'
    
    # Load the image:
    image = imgutil.loadimg(fname,from_database=True)
    # store 1st image for plotting
    if count == 0:
        image0 = imgutil.loadimg(fname,from_database=True)
    
    # Find stars in image:
    centers = centroid.findstars(image)
    
    # Get centroids:
    centroids.append(centroid.imgcentroid(image,centers))
    
    # store number of stars centroided per frame
    numstars.append(len(centroids[count]))
    
    
print 'numstars:', numstars
print 'avg stars:', np.mean(numstars)

# plot number of star as function of frames, saved to Papers/IEEE/Figures
plots.starnum(numstars)

# COOL PLOT 1
# show first image w/ with centroids from following frames, saved to Papers/IEEE/Figures
plots.starpaths(image0,centroids)


# Pickle the found centroids for safekeeping :)
# To load later: centroids = pickle.load( open( "saved_centroids.p", "rb" ) )
pickle.dump( centroids, open( "saved_centroids_" + time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime()) + ".pk", "wb" ) )

# --------------Match Stars:--------------------- 
print 'Matching stars.'
matched_centroids = []
nummatchstars = []
search_radius = 50
for count,(centlistA,centlistB) in enumerate(izip(centroids, islice(centroids, 1, None))):
    print 'Comparing centroid list: ' + str(count+1) + ' to ' + str(count+2) + '.'
    # finding matches
    matched_centroids.append(starmatcher.matchstars(centlistA,centlistB,search_radius))
    # storing number of matches
    nummatchstars.append(len(matched_centroids[count]))

print 'num matched stars:', nummatchstars
print 'avg num matched stars:', np.mean(nummatchstars)

# plot matched paths
'''
fig = pl.figure()
fig = pl.gray()
fig = pl.imshow(np.multiply(image0,1), cmap=None, norm=None, aspect=None,
            interpolation='nearest', vmin=0, vmax=2048, origin='upper')
radius = 10
color = 'r'
for centlist in matched_centroids:
    for pospair in centlist:
        circ = pl.Circle(tuple(pospair[0]), radius, ec=color, fill=False)
        fig = pl.gca().add_patch(circ)
fig = pl.show()
fig = pl.savefig('../../Papers/IEEE/Figures/matchstarpath_b172_100f.png')
'''
#


# ------------Find quaternions:--------------------------
print 'Find quaternions.'
quats = []
for count,matched in enumerate(matched_centroids):
    # Project 2d vectors into 3d space:
    Vi2d,Vb2d = zip(*matched)
    Vi = starmatcher.project3D(Vi2d)
    Vb = starmatcher.project3D(Vb2d)
    # Run the Q-Method:
    quats.append(qmethod.qmethod(Vi,Vb))

print quats



# -----------Find variance in quaternions - different methods----------------
from analysis import tracking
import pylab
print "Find Variance"
print "Filtering frequency below 1.5Hz"
motion_frequency=1.5
print "Time between images is 0.1 [s]"
delta_t=0.1
print "Showing plots of filtering"
show_plot=1
pylab.close()
var1 = tracking.FindVariance(quats,delta_t=delta_t,motion_frequency=motion_frequency,plot=show_plot)
fig=pylab.figure(1)
fig.savefig('../../Papers/IEEE/Figures/roll_1.5Hz_freq.png')
fig=pylab.figure(2)
fig.savefig('../../Papers/IEEE/Figures/pitch_1.5Hz_freq.png')
fig=pylab.figure(3)
fig.savefig('../../Papers/IEEE/Figures/yaw_1.5Hz_freq.png')

toc = time.clock()
print 'Total time: ' + str(toc - tic) + ' s'



