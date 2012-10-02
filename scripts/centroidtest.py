#
# Star Field Generator
# DayStar 2012
# By: Kevin Dinkel
#

import starfieldgenerator as stfgen
import centroid as cntrd
from pylab import *
from numpy import *
import copy as cp

# Star Fraction:
star_frac = 1.0/10.0

############## Testing Functions: #################################
# Centroiding wrapper to access different centroiding methods
def centroid(xyi,method,field_noBG,numPix):
	
	# Determine centroid method to use:
	if method == 0:
		cent,time = cntrd.IWC(xyi,method+1) # IWC: p = 1
	elif method == 1:
		cent,time = cntrd.IWC(xyi,method+1) # IWC: p = 2
	elif method == 2:
		cent,time = cntrd.IWC(xyi,method+1) # IWC: p = 3
	elif method == 3:
		cent,time = cntrd.IWC(xyi,method+1) # IWC: p = 4
	elif method == 4:
		cent,time = cntrd.gauss(field_noBG,xyi,numPix)
	elif method == 5:
		cent,time = cntrd.parabolic(field_noBG,xyi,numPix)
	elif method == 6:
		cent,time = cntrd.eCntrd(field_noBG,xyi,numPix)
	else:
		print "No such method!"
		return (-1,-1),-1
	
	# Return centroid and time:
	return cent,time

def getandfindstar(I_o, I_b, pixSub):
	# Generate star in center of field and copy it:
	field,s2n,real_cent=stfgen.starcenterB(I_o, I_b, pixSub)
	I = cp.deepcopy(field)
	
	# Find Star:
	xyi = cntrd.identifyStars(I,pixSub,stfgen.ADC(I_b))
	
	# Ensure only a single star was found:
	if len(xyi) > 1 or len(xyi) < 1:
		return field,s2n,real_cent,[[-1]]
		
	return field,s2n,real_cent,xyi
		
# Test range of methods
def centroidallmethods(I_o, I_b, pixSub, methods):

	# Allocate Memory
	time = []
	comp_cent = []
	error = []
	
	# Get star nodes:
	field,s2n,real_cent,xyi = getandfindstar(I_o, I_b, pixSub)
	
	# Ensure a single star was found:
	if xyi[0][0] != -1:
		
		# Copy the field and subtract the background
		noBG = cntrd.sbtrctBG(field,stfgen.ADC(I_b))
		
		# Iterate over all centroiding methods:
		for i in range(len(methods)):
			# Centroid star:
			cc,t = centroid(xyi[0],methods[i],noBG,int(pixSub**0.5))
			comp_cent.append(cc), time.append(t)
		
			# Make sure a valid centroid was calculated:
			if comp_cent[i][0] == -1:
				error.append(-1)
			else:
				error.append(centerror(comp_cent[i],real_cent))
	
	else: # return -2 if 1 star not found
		for i in range(len(methods)):
			error.append(-2)
			time.append(-2)
	
	# Return results:
	return field,s2n,real_cent,comp_cent,error,time

def centroidallmethods_stat(numtimes,I_o, I_b, pixSub, methods):
	
	# Allocate memory:
	numMethods = len(methods)
	error = listoflists(numMethods,[])
	time = listoflists(numMethods,[])
	
	# Call each centroiding method x numtimes:
	for i in range(numtimes):
		_,s2n,_,_,e,t = centroidallmethods(I_o, I_b, pixSub, methods)
		for j in range(numMethods):
			if( e[j] >= 0 ):
				error[j].append(e[j])
			if( t[j] >= 0 ):
				time[j].append(t[j])
			
	# Average and STD data:
	data = []
	for j in range(numMethods): 
		data.append({'error':(average(error[j]),std(error[j])),'time':(average(time[j]),std(time[j]))})
	
	# Return data:
	return data,s2n

# Statistically run test over ranges of parameters for multiple trials:
def runtest(numtimes, I_o, I_b, pixSub, methods):
	
	# Define lengths:
	lenP = len(pixSub)
	
	# Allocate memory:
	numMethods = len(methods)
	data = listoflists(numMethods,listoflists(lenP,[]))
	snr  = listoflists(lenP,[])
	
	# Iterate through all tests:
	print '%d total tests will be run.' % (lenP)
	for i in range(lenP):			
		# Run centroiding method:
		print 'Running test %d of %d...' % (i,lenP)
		temp_data,snr[i] = centroidallmethods_stat(numtimes, I_o, I_b, pixSub[i], methods)
		
		# Store data:
		for k in range(numMethods):
			data[k][i] = temp_data[k]
	
	# Return data:
	print 'All tests finished successfully!'
	return data,snr
		
#################### Helper Functions:###################
# Get empty list of empty lists of size 'length'
def listoflists(length,alist):
	data = []
	for i in range(length):
		data.append(cp.deepcopy(alist))
	return data

# Get error:
def centerror(comp_cent,real_cent):
	return sqrt((real_cent[0] - comp_cent[0])**2+(real_cent[1] - comp_cent[1])**2)

# Display resulting centroid:
def showcentroid(fignum,field,real_cent,comp_cent):
	hue = ['y.','g.','r.','m.']
	m,n = field.shape
	hold(True)
	stfgen.showfield(fignum,field)
	plot(real_cent[0],real_cent[1],'b.')
	for i in range(len(comp_cent)):
		string = 'Method %d' % i
		plot(comp_cent[0],comp_cent[1],hue[i], label=string)
	axis([0,m-1,0,n-1])
	xlabel('x')
	ylabel('y')
	legend()

# Write results to file:
def writeout(fname,data,snr,pixSub):
	text_file = open(fname, "w")
	head = "% Centroid Test: " + fname + "\n"
	text_file.write(head)
	text_file.write("% [METHOD], [subPix], [SNR], [ERROR_AVE], [ERROR_STD], [OPS_AVE], [OPS_STD]\n")
	
	numMethods,numTests = shape(data)
	for i in range(numMethods):
		for j in range(numTests):
			line = str(i)+", "+str(pixSub[j])+", "+str(snr[j])+", " \
				+str(data[i][j]['error'][0])+", " \
				+str(data[i][j]['error'][1])+", " \
				+str(data[i][j]['time'][0])+", "  \
				+str(data[i][j]['time'][1])       \
				+"\n"
			text_file.write(line)
	text_file.close()
	
# Print results:
def printresults(method,s2n,realcent,compcent,error,time):
	for i in range(len(method)):
		print "********* Method: %d ***********" % method[i]
		print "SNR:               %0.10f       " % s2n
		print "Actual Centroid:   %0.10f,%0.10f" % (realcent[0],realcent[1])
		print "Computed Centroid: %0.10f,%0.10f" % (compcent[i][0],compcent[i][1])
		print "Error:             %0.10f       " % error[i]
		print "Operations:        %d           " % time[i]
		print "                                "

# Print statistical results:
def printstatresults(method,data):
	for i in range(len(method)):
		print "********* Method: %d ***********" % method[i]
		print "Error (ave): %0.10f " % data[i]['error'][0]
		print "      (std): %0.10f " % data[i]['error'][1]           
		print "Ops   (ave): %0.10f " % data[i]['time'][0]
		print "      (std): %0.10f " % data[i]['time'][1]
		print "                                "

# Print full run of results:
def printrunresults(method,data,s2n,pixSub):
	for i in range(len(s2n)):
		print "################################"
		print "Star over %0.2f pixels          " % pixSub[i]
		print "SNR: %0.10f                     " % s2n[i]
		print "################################"
		printstatresults(method,(data[0][i],data[1][i],data[2][i],data[3][i]))
		print "################################"		
		print "                                "	

###################### MAIN: ############################
# Defines:
'''
# Centroid single star:
field,s2n,realcent,compcent,error,time = centroidallmethods(I_o, I_b, pixSub, method)
showcentroid(1,field,realcent,compcent)
printresults(method,s2n,realcent,compcent,error,time)
'''
'''
# Statistically centroid a over multiple stars of the same parameter:
data,s2n = centroidallmethods_stat(numtimes, I_o, I_b, pixSub, method)
printstatresults(method,data)
print "SNR = " + str(s2n)
'''

# Set-up:
close('all')
stfgen.setbitres(16)

# Test Params:
fstr                 = "/home/kevin/svn/src/dev/data/"
method               = [0,1,2,3,4,5,6]
numtimes             = 300
pixSub               = array([3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9.5,10])
for i in range(len(pixSub)):
	pixSub[i] **= 2
	
# 4th Mag @ Day:
I_o = 12751.9377            # intensity of object
I_b = 1492.5548             # intensity of background

# Statistically centroid a over multiple stars of different parameters:
fname = fstr + "centroid_test_" + str(int(math.floor(I_o))) + "_" + str(int(math.floor(I_b))) + ".csv"
print "*********** 4th Mag @ Day ***********"
data,snr = runtest(numtimes, I_o, I_b, pixSub, method)
#printrunresults(method,data,snr,pixSub)
writeout(fname,data,snr,pixSub)

# 5th Mag @ Day:
I_o = 5076.637844889627     # intensity of object
I_b = 1492.5548             # intensity of background

# Statistically centroid a over multiple stars of different parameters:
fname = fstr + "centroid_test_" + str(int(math.floor(I_o))) + "_" + str(int(math.floor(I_b))) + ".csv"
print "*********** 5th Mag @ Day ***********"
data,snr = runtest(numtimes, I_o, I_b, pixSub, method)
#printrunresults(method,data,snr,pixSub)
writeout(fname,data,snr,pixSub)

# 6th Mag @ Day:
I_o = 2021.5548             # intensity of object
I_b = 1492.5548             # intensity of background

# Statistically centroid a over multiple stars of different parameters:
fname = fstr + "centroid_test_" + str(int(math.floor(I_o))) + "_" + str(int(math.floor(I_b))) + ".csv"
print "*********** 6th Mag @ Day ***********"
data,snr = runtest(numtimes, I_o, I_b, pixSub, method)
#printrunresults(method,data,snr,pixSub)
writeout(fname,data,snr,pixSub)

# 7th Mag @ Day:
I_o = 804.5929              # intensity of object
I_b = 1492.5548             # intensity of background

# Statistically centroid a over multiple stars of different parameters:
fname = fstr + "centroid_test_" + str(int(math.floor(I_o))) + "_" + str(int(math.floor(I_b))) + ".csv"
print "*********** 7th Mag @ Day ***********"
data,snr = runtest(numtimes, I_o, I_b, pixSub, method)
#printrunresults(method,data,snr,pixSub)
writeout(fname,data,snr,pixSub)

# 8th Mag @ Day:
I_o = 320.3142              # intensity of object
I_b = 1492.5548             # intensity of background

# Statistically centroid a over multiple stars of different parameters:
fname = fstr + "centroid_test_" + str(int(math.floor(I_o))) + "_" + str(int(math.floor(I_b))) + ".csv"
print "*********** 8th Mag @ Day ***********"
data,snr = runtest(numtimes, I_o, I_b, pixSub, method)
#printrunresults(method,data,snr,pixSub)
writeout(fname,data,snr,pixSub)

# 8th Mag @ night:
I_o = 320.3142              # intensity of object
I_b = 0.0                   # intensity of background

# Statistically centroid a over multiple stars of different parameters:
fname = fstr + "centroid_test_" + str(int(math.floor(I_o))) + "_" + str(int(math.floor(I_b))) + ".csv"
print "*********** 8th Mag @ Night ***********"
data,snr = runtest(numtimes, I_o, I_b, pixSub, method)
#printrunresults(method,data,snr,pixSub)
writeout(fname,data,snr,pixSub)
