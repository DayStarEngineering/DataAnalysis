
import starfieldgenerator as sfg
import numpy as np
from pylab import *

######## runtest ##########
def runtest():
	# Clean up
	close('all')
	
	# Initialize star field generator
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
	# 4th-8th mag at day (6000 K)
	Io = [2869185.9871,1142243.5151,454735.3339,181033.3971,72070.6935]
	
	# Exposure time
	exptime = 0.050 #[sec]
	
	# Normalize intensities to the exposure time
	Ib *= exptime
	for i in range(len(Io)):
		Io[i] *= exptime
	
	# Store 1 mag 4 star
	I_o = [Io[0]]
	# Store 2 mag 5 stars
	for i in range(2):
		I_o.append(Io[1])
	# Store 7 mag 6 stars
	for i in range(7):
		I_o.append(Io[2])
	# Store 26 mag 7 stars
	for i in range(26):
		I_o.append(Io[3])
	# Store 64 mag 8 stars
	for i in range(64):
		I_o.append(Io[4])
	
	# Constants for test
	numsubsamples = 200
	step = 100 #for number of pixels in subsample
	xpix = 2160 #dimension of image
	ypix = 2560
	
	# Directory for test data
	path = "/home/andrew/svn/src/dev/data/"
	
	# Open results file for this Io
	fname = path+"median_test2.csv"
	text_file = openfile(fname,numsubsamples,step)
	
	# Initialize row and column spacing
	numrowsandcols = zeros(numsubsamples,dtype=np.int)
	dx = zeros(numsubsamples,dtype=np.int)
	dy = zeros(numsubsamples,dtype=np.int)
	for i in range(numsubsamples):
		pixinsample = (i+1)*step
		numrowsandcols[i] = math.ceil(pixinsample**0.5)
		dx[i] = int(xpix/numrowsandcols[i])
		dy[i] = int(ypix/numrowsandcols[i])
		
	# Initialize subsample median data structure
	medsub = zeros(numsubsamples,dtype=np.int)
	
	# Call star field generator to make the image
	I,_,_ = sfg.randfieldgen(xpix,ypix,I_o,Ib)
	'''
	for i in range(xpix):
		line = ""
		for j in range(ypix):
			line += str(int(I[i][j]))+"\t"
		print line'''
	sfg.showfield(1,I)
	
	# Compute median of image
	med = median(I)
	
	for i in range(numsubsamples):
		# Compute median using subsampling
		subI = [] #image subsample
		for m in range(numrowsandcols[i]):
			row = m*dx[i]
			for n in range(numrowsandcols[i]):
				col = n*dy[i]
				subI.append(I[row][col])
		medsub[i] = median(subI)
	
	# Print results for this image
	writeout(text_file,med,medsub)
	
	# Close results file
	text_file.close()
	
########### Write results to file ############
def writeout(text_file,med,medsub):
	line = str(med)
	for i in range(len(medsub)):
		line += ', '+str(medsub[i])
	text_file.write(line+"\n")

########### Initialize results file ###########
def openfile(fname,numsubsamples,step):
	text_file = open(fname, 'w')
	head = "%[Image Median]\t[Subsample Median] -> ("+ \
	str(numsubsamples)+" subsamples with "+str(step)+" pixel step size)\n"
	text_file.write(head)
	return text_file

####### main ###########
runtest()

