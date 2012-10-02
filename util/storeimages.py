
import starfieldgenerator as sfg
import centroid as cntrd
import numpy as np
import chzphot as ch
import copy as cp
from pylab import *

########### Write results to file ############
def writeout(text_file,I):
	m,n = I.shape
	for i in range(m):
		for j in range(n):
			text_file.write(str(int(I[i][j]))+'\n')

########### Initialize results file ###########
def openfile(fname):
	text_file = open(fname, 'w')
	return text_file

######## genplots #########
def genstarfiles(method):
	close('all')
	bitres = 11
	sfg.setbitres(bitres)
	
	# All intensities are for a 1 sec exposure
	Ib = 335824.8442        # intensity of background at day
	'''
	# 4th Mag @ Day:
	Io = 2869185.9871       # intensity of object (6000 K)
	
	# 5th Mag @ Day:
	Io = 1142243.5151       # intensity of object (6000 K)
	
	# 6th Mag @ Day:
	Io = 454735.3339        # intensity of object (6000 K)
	
	# 7th Mag @ Day:
	Io = 181033.3971        # intensity of object (6000 K)
	
	# 8th Mag @ Day:
	Io = 72070.6935         # intensity of object (6000 K)
	'''
	# Select object intensities from list above (pick one)
	Io = 2869185.9871 #4th mag at day (6000 K)
	
	# Create exposure times
	#exptime = [1/5000,1/2500,1/1000,1/500,1/250,1/125,1/60,1/30,1/15,1/10]
	# Pick one
	exptime = 1.0/60.0
	
	# Define blur
	pixSub = [3.0,3.5,4.0,4.5,5.0,5.5,6.0,6.5,7.0,7.5,8.0,8.5,9.0,9.5,10.0]
	for i in range(len(pixSub)):
		pixSub[i] **= 2
	
	# Correct object and background intensities
	Io *= exptime
	Ib *= exptime
	# Open results file for this Io and Ib
	path = "/home/andrew/svn/src/dev/data/"
	fname = path + "image_" + str(int(Io)) + "_" + str(int(Ib)) + ".txt"
	print 'file name: ' + str(fname)
	text_file = openfile(fname)
	# Generate image
	I,snr = sfg.showallPixSubfield(pixSub,Io,Ib)
	I2 = cp.deepcopy(I)
	# Write image to file
	writeout(text_file,I)
	# Close results file for this Io and Ib
	text_file.close()
	# Identify possible stars
	starxyi = cntrd.identifyStars2(I,method)
	# Brighten all identified pixels
	for x in range(len(starxyi)):
		for y in range(len(starxyi[x])):
			I[starxyi[x][y][0]][starxyi[x][y][1]] = 2**bitres-1
	# Display the original star field
	sfg.showfield(1,I2)
	# Display the altered star field
	sfg.showfield(2,I)

####### Main #########
#method = 5
#genstarfiles(method)


