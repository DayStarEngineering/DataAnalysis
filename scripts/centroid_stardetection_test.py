
import starfieldgenerator as sfg
import centroid as cntrd
import numpy as np
import chzphot as ch
import copy as cp
from pylab import *

######## testSNlimit #########
def runtest(method):
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
	# Centroiding methods
	methods = [0, 1, 2, 3, 4, 5]
	
	# Select object intensities from list above
	# 4th-8th mag at day (6000 K)
	Io = [2869185.9871,1142243.5151,454735.3339,181033.3971,72070.6935]
	
	# Create exposure times
	exptime = [1.0/5000.0, 1.0/2500.0, 1.0/1000.0, 1.0/500.0, 1.0/250.0, \
		1.0/125.0, 1.0/60.0, 1.0/30.0, 1.0/15.0, 1.0/10.0]
	
	# Define blur
	pixSub = [3.0,3.5,4.0,4.5,5.0,5.5,6.0,6.5,7.0,7.5,8.0,8.5,9.0,9.5,10.0]
	for i in range(len(pixSub)):
		pixSub[i] **= 2
	
	# Directory for test data
	path = "/home/andrew/svn/src/dev/data/"
	
	# Number of trials
	numtrials = 15
	
	# Variables for printing out test progress
	lenExp = len(exptime)
	totaltests = lenExp*len(Io)
	
	for i in range(len(Io)):
		# Open results file for this Io
		fname = path + "stardetection_test4_" + str(int(math.floor(Io[i]))) + \
			"_" + str(int(math.floor(Ib))) + ".csv"
		print 'file name ' + str(fname)
		text_file = openfile(fname,methods)
		for j in range(len(exptime)):
			print 'test '+str(i*lenExp+j+1)+'/'+str(totaltests)
			# Correct object and background intensities
			I_o = Io[i]*exptime[j]
			I_b = Ib*exptime[j]
			print 'Io ' + str(I_o) + ' Ib ' + str(I_b)
			# Initialize ratios of stars seen
			ratio = zeros((1,len(pixSub)))
			ratio = ratio[0] #kill the unnecessary outer list
			# Initialize centroiding data structure
			data = []
			for x in range(len(methods)):
				data.append([0,0])
			# Initialize data structure to hold info for every star
			star = []
			for x in range(len(pixSub)):
				star.append(cp.deepcopy(data))
			# Run all trials
			for k in range(numtrials):
				print 'trial '+str(k+1)+'/'+str(numtrials)
				# Generate image
				I,snr = sfg.showallPixSubfield(pixSub,I_o,I_b)
				#I2 = cp.deepcopy(I)
				# Determine median and background limit
				med = median(I)
				#limit,_ = ch.robomad(I,5)
				# Subtract the background from the image
				noBG = cntrd.sbtrctBG(I,med)
				# Copy the image and identify possible stars
				starxyi = cntrd.identifyStars2(cp.deepcopy(I),method)
				# Examine all possible stars
				if len(starxyi) <= len(pixSub):
					for x in range(len(starxyi)):
						cent,_ = cntrd.IWC(starxyi[x],2)
						if (cent[0]+0.3) > cent[1] and (cent[0]-0.3) < cent[1]:
							# Calculate the real centroid
							real_cent = int(floor(cent[0]+0.3))
							# Determine which stars were identified and centroided
							cent[0] = (cent[0]-30)/20
							cent[1] = (cent[1]-30)/20
							cent = int(floor(cent[0]+0.3))
							ratio[cent] += 1
							# Define radius of subregion for this star
							numPix = pixSub[cent]
							subR = ceil(numPix**0.5)+4
							for y in range(len(methods)):
								cc,t = centroid(starxyi[x],methods[y],I,noBG,subR)
								# Make sure a valid centroid was calculated
								if cc[0] == -1:
									star[cent][y][0] = nan #d^2
									star[cent][y][1] = nan #counts
								else:
									star[cent][y][0] = centerror(cc,real_cent)
									star[cent][y][1] = t
			# Average the results
			for x in range(len(ratio)):
				ratio[x] /= float(numtrials)
			for x in range(len(pixSub)):
				for y in range(len(methods)):
					if star[x][y][0] == 0:
						star[x][y][0] = nan
					else:
						star[x][y][0] /= float(numtrials)
						star[x][y][0] = sqrt(star[x][y][0]) #RMS error
					if star[x][y][1] == 0:
						star[x][y][1] = nan
					else:
						star[x][y][1] /= float(numtrials) #average counts
			# Write results to file
			writeout(text_file,pixSub,exptime[j],snr,ratio,star)
		# Close results file for this Io
		text_file.close()
	# Finished

########### Write results to file ############
def writeout(text_file,pixSub,exptime,snr,ratio,star):
	for i in range(len(pixSub)):
		if snr[i] == 0:
			snr[i] = 'NaN'
		line = str(pixSub[i])+', '+str(exptime)+', '+str(snr[i])+', '+str(ratio[i])
		# data[0] = RMS error in pixels, data[1] = average counts
		data = star[i]
		# Add columns for each method
		for j in range(len(data)):
			line += ', '+str(data[j][0])+', '+str(data[j][1])
		text_file.write(line+'\n')

########### Initialize results file ###########
def openfile(fname,methods):
	text_file = open(fname, 'w')
	head = '% S/N Test: ' + fname + '\n'
	text_file.write(head)
	head2 = '% [Blur], [Exposure Time], [S/N], [Ratio]'
	for i in range(len(methods)):
		head2 += ', [M'+str(i)+' RMS], [M'+str(i)+' counts]'
	text_file.write(head2+'\n')
	return text_file

######### Get error ##############
def centerror(comp_cent,real_cent):
	return (real_cent - comp_cent[0])**2+(real_cent - comp_cent[1])**2

##### Centroiding wrapper to access different centroiding methods ######
def centroid(xyi,method,field,field_noBG,subR):
	# Determine centroid method to use
	if method == 0:
		cent,time = cntrd.roboCoG(field,xyi,subR) #CoG on raw image
	elif method == 1:
		cent,time = cntrd.roboCoG(field_noBG,xyi,subR) #CoG on (raw-med) image
	elif method == 2:
		cent,time = cntrd.roboIWC(field,xyi,subR) #IWC on raw image
	elif method == 3:
		cent,time = cntrd.roboIWC(field_noBG,xyi,subR) #IWC on (raw-med) image
	elif method == 4:
		cent,time = cntrd.parabolic(field_noBG,xyi,subR) #Para on (raw-med)
	elif method == 5:
		cent,time = cntrd.gauss(field_noBG,xyi,subR) #Gauss on (raw-med)
	else:
		print "No such method!"
		return (-1,-1),-1
	
	# Return centroid and time:
	return cent,time

######## genplots #########
def genplots(method):
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
	exptime = 1.0/30.0
	
	# Define blur
	pixSub = [3.0,3.5,4.0,4.5,5.0,5.5,6.0,6.5,7.0,7.5,8.0,8.5,9.0,9.5,10.0]
	for i in range(len(pixSub)):
		pixSub[i] **= 2
	
	# Correct object and background intensities
	Io *= exptime
	Ib *= exptime
	print 'Io ' + str(Io) + ' Ib ' + str(Ib)
	# Generate image
	I,snr = sfg.showallPixSubfield(pixSub,Io,Ib)
	I2 = cp.deepcopy(I)
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
method = 5
runtest(method)
#genplots(method)


