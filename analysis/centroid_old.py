#
# Centroiding Script
# DayStar 2012
# By: Andrew Zizzi
#

# Imports:
from pylab import *
import numpy as np
import copy as cp
import starfieldgenerator as sfg
import chzphot as ch

######## identifyStars #########
def identifyStars(I,numPix,bg):
	m,n = I.shape
	XYI = []
	
	# Determine background threshold
	limit = int(floor(bg+bg**(0.5)))
	#print 'limit = '+str(limit)
	
	# Calculate min and max pixel threshold for a star
	#minthresh = floor(numPix/4.0) #1/4 star area
	#maxthresh = floor(numPix*2.0) #2 times star area
	#print 'min = '+str(minthresh)+' max = '+str(maxthresh)
	
	# Identify and explore possible stars
	for i in range(m):
		for j in range(n):
			if I[i][j] > limit:
				# Beware: I is pass by reference
				xyi,numNodes = dfs(I,i,j,limit,minthresh,maxthresh)
				if numNodes == -1: #ignore point sources
					continue
				XYI.append(xyi)
	
	return XYI

######## identifyStars2 #########
def identifyStars2(I,method):
	m,n = I.shape
	XYI = []
	
	# Search entire image for background threshold
	if method == 1:
		limit = int(floor(np.mean(I) + np.std(I)))
	elif method == 2:
		limit = int(floor(np.mean(I)))
	elif method == 3:
		limit = int(floor(np.mean(I) - np.std(I)))
	elif method == 4:
		# MAD
		med = np.median(I)
		limit = med + np.median(abs(I[:,:]-med))
	elif method == 5:
		mn,std = ch.robomad(I,5)
		limit = mn + 2.5*std
	else:
		print 'Invalid method: ' + str(method)
		limit = 0
	# NEED TO DEFINE A MINIMUM LIMIT AND NEVER GO BELOW THAT
	#print 'limit = '+str(limit)
	
	# Set min and max pixel threshold for a star
	minthresh = 7 #need 3x3 minimum
	maxthresh = 100 #use 10x10 maximum
	
	# Identify and explore possible stars
	for i in range(m):
		for j in range(n):
			if I[i][j] > limit:
				# Beware: I is pass by reference
				xyi,numNodes = dfs(I,i,j,limit,minthresh,maxthresh)
				if numNodes == -1: #ignore invalid sources
					continue
				XYI.append(xyi)
	
	return XYI

######## dfs #########
def dfs(I,s,t,limit,minthresh,maxthresh):
	# Create stack and push source node (s,t)
	stack = [[s, t]]
	ind = 0 #stack index pointer
	# Store source info as (x,y,intensity)
	xyi = [[s,t,I[s][t]]]
	# Mark source
	I[s][t] = 0 #limit
	# Begin exploration
	numNodes = 1
	intensity = I[s][t]
	while ind > -1 and numNodes < maxthresh:
		# Pop last element into node (s,t)
		s = stack[ind][0]
		t = stack[ind][1]
		ind -= 1
		# Explore every edge from node (s,t)
		neighb = [[s-1,t],[s,t-1],[s,t+1],[s+1,t]]
		for i in range(4):
			j = neighb[i][0]
			k = neighb[i][1]
			try:
				if I[j][k] > limit: #if not marked
					if j > 0 and k > 0: #don't wrap by negatives
						# Push node
						ind += 1
						stack.append([])
						stack[ind] = [j,k]
						# Store node info
						xyi.append([j,k,I[j][k]])
						# Mark node
						numNodes += 1
						intensity += I[j][k]
						I[j][k] = 0 #limit
			except IndexError: #j or k > num pixels
				continue
	# Determine if the patch has the desired number of pixels
	if numNodes < minthresh:
		#if numNodes > minthresh/2:
		#	print str(numNodes) + '/' + str(minthresh)
		numNodes = -1
	
	return xyi,numNodes

######## IWC #########
def IWC(xyi,p):
	counts = 0 #operations
	# Zero out XIW and IW
	XIW = [0,0]
	IW = 0
	for i in range(len(xyi)):
		# This level indicates a series of x,y,intensities
		x = xyi[i][0]
		y = xyi[i][1]
		if p == 1:
			ncounts = 5
		else:
			ncounts = 6
		intensity_p = xyi[i][2]**p #1 op
		# Sum elements
		XIW[0] += x*intensity_p #2 ops
		XIW[1] += y*intensity_p #2 ops
		IW += intensity_p #1 op
		counts += ncounts
	centroid = [XIW[0]/IW,XIW[1]/IW] #2 ops
	return centroid,counts+2

######## Gaussian ##########
def gauss(I,xyi,numPix):
	x = y = 0
	counts = 0
	temp = IWC(xyi,1) #call CoG
	counts += temp[1] #ops from CoG
	# Error in Eliot's gaussian calculation occurs when too few pixels
	try:
		x,y = ch.gcntrd(I,numPix,int(temp[0][0]),int(temp[0][1]))
	except: #seen ValueError
		return [-1,-1],-1
	counts += 8*numPix**2 + 36*numPix + 40 #ops from ch.gcntrd
	centroid = [x,y]
	return centroid,counts

####### Parabolic ##########
def parabolic(I,xyi,numPix):
	x = y = 0
	counts = 0
	temp = IWC(xyi,1) #call CoG
	counts += temp[1] #ops from CoG
	# Encountering an unknown IndexError
	try:
		x,y = ch.parcntrd(I,numPix,int(temp[0][0]),int(temp[0][1]))
	except: #seen ValueError, IndexError
		return [-1,-1],-1
	counts += 8*numPix**2 + 61 #ops from ch.parcntrd
	centroid = [x,y]
	return centroid,counts

####### Eliot Centroid ##########
def roboCoG(I,xyi,numPix):
	x = y = 0
	counts = 0
	temp = IWC(xyi,1) #call CoG
	counts += temp[1] #ops from CoG
	try:
		x,y = ch.cntrd(I,numPix,int(temp[0][0]),int(temp[0][1]))
	except: #seen ValueError
		return [-1,-1],-1
	counts += 8*numPix**2 + 10 #ops from ch.cntrd
	centroid = [x,y]
	return centroid,counts

####### Modified Eliot Centroid ########
def roboIWC(I,xyi,numPix):
	x = y = 0
	counts = 0
	temp = IWC(xyi,1) #call CoG
	counts += temp[1] #ops from CoG
	try:
		x,y = ch.cntrd2(I,numPix,int(temp[0][0]),int(temp[0][1]))
	except: #seen ValueError
		return [-1,-1],-1
	counts += 9*numPix**2 + 10 #ops from ch.cntrd
	centroid = [x,y]
	return centroid,counts

####### Subtract Background ########
def sbtrctBG(I,limit):
	# Copy image
	noBG = cp.deepcopy(I)
	# Subtract out noise level
	m,n = noBG.shape
	for i in range(m):
		for j in range(n):
			noBG[i][j] -= limit
			if noBG[i][j] < 0:
				noBG[i][j] = 0
	return noBG

######## Main #########



'''
bitres = 8.0
pixSub = 25.0

# 4th Mag @ Day:
Io = 12751.9377            # intensity of object
Ib = 1492.5548             # intensity of background

# 6th Mag @ Day:
Io = 2021.5548             # intensity of object
Ib = 1492.5548             # intensity of background

# 7th Mag @ Day:
Io = 804.5929              # intensity of object
Ib = 1492.5548             # intensity of background

# 8th Mag @ Day:
Io = 320.3142              # intensity of object
Ib = 1492.5548             # intensity of background

close('all')
sfg.setbitres(bitres)
field,s2n,center = sfg.starcenterB(Io,Ib,pixSub)
print field
print 'center = ' + str(center) + ' snr = ' + str(s2n)
# Get dimensions
xpix,ypix = field.shape
# Copy the image
field2 = cp.deepcopy(field)

# Subtract out the background from one copy
noBG = sbtrctBG(field,sfg.ADC(Ib))

# Identify pixels in stars
starxyi = identifyStars(field,pixSub,sfg.ADC(Ib))
print starxyi
# Brighten all identified pixels
for i in range(len(starxyi)):
	for j in range(len(starxyi[i])):
		field[starxyi[i][j][0]][starxyi[i][j][1]] = 2**bitres-1

# Display the altered star field
sfg.showfield(1,field)
sfg.showfield(2,field2)

# Run centroiding methods
x = []
data = []
for i in range(len(starxyi)):
	for p in [1,2,3,4,5]:
		temp = IWC(starxyi[i],p)
		x.append(temp)
		if p == 2: #select IWC2 results to display
			data.append(temp)
		print 'IWC' + str(p) + ': ' + str(x[p-1+i*5])
	temp = gauss(noBG,starxyi[i],int(pixSub**0.5))
	print 'Gauss: ' + str(temp)
	temp = parabolic(noBG,starxyi[i],int(pixSub**0.5))
	print 'Para: ' + str(temp)
	temp = eCntrd(noBG,starxyi[i],int(pixSub**0.5))
	print 'Cent: ' + str(temp)

# Need to plot the centroids on top of the image as well
hold(True)
for i in range(len(data)):
	plot(data[i][0][0],data[i][0][1],'r.')

axis([-0.5,xpix-.5,-0.5,ypix-.5]) #implemention based on image dimensions
xlabel('x')
ylabel('y')
'''

