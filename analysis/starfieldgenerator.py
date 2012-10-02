#
# Star Field Generator
# DayStar 2012
# By: Kevin Dinkel
#

# Imports:
from pylab import *
from numpy import *
from scipy import *
import math as math
from scipy.special import jv
from scipy.stats import poisson
from scipy.optimize import fsolve
import random as rand
import storeimages as st

# Globals
bitres = 11.0         # [0:2^bitres-1] is the range of adc values
FOV = 7.0*3600.0      # arcseconds (ST5000 max FOV)
welldepth = 30000.0   # photoelectron depth
exposure = 0.5       # seconds

################### Helper Functions: ##############################
# Retrieve empty 0-value frame of size xpix,ypix
def emptyframe(xpix,ypix):
	x,y=indices((xpix,ypix))
	return (zeros((xpix,ypix)),x,y)

# Generate background frame:
def genbackground(I_b,xpix,ypix):
	field,_,_ = emptyframe(xpix,ypix)
	for i in range(xpix):
		for j in range(ypix):
			field[i][j] = I_b
	return field

# Star magnitudes as defined by wiki:
# Function derived as (2.5^x)^-1 -> where x is the magnitude
# magnitude = [1.0,0.40,0.16,0.063,0.025,0.01,0.004,0.0016,0.00063,0.00025,0.00010] # http://en.wikipedia.org/wiki/Apparent_magnitude
# 0 mag defined at 100% -> mags decrease logrithmically from 1 to zero
def normstarmag(mag):
	return (2.5**mag)**-1.0

# Wrapper to display star field
def showfield(fignum,field):
	figure(fignum)
	gray()
	imshow(field, cmap=None, norm=None, aspect=None, interpolation='nearest',
		vmin=0, vmax=2**bitres, origin='lower')
	#imshow(field)
	colorbar()
	show()

# Normalize a field to val
def normalize(field):
	xpix,ypix=shape(field)
	maximum  = 0;
	for i in range(xpix):
		m = max(field[i])
		if maximum < m:
			maximum = m
	return (field/maximum)
	
# Normalize data to welldepth
def WDnormalize(field):
	return (field/welldepth)

# Calculate signal-to-noise ratio:
def SNR(I_o,I_b,pixSub):
	return I_o/sqrt(I_o + I_b*pixSub)

# Calculate signal-to-noise ratio:

def SNR_ADC(I_o,I_b,pixSub):
	return ADC(I_o)/sqrt(ADC(I_o) + ADC(I_b)*pixSub)
'''
def SNR_ADC(I_o,I_b,pixSub):

	# Form star to calculate SNR
	rad = sqrt(pixSub)/2.0
	xpix = ypix = int(math.floor(rad*5.0))
	xo = yo = xpix/2.0
	field = stargenNormB(I_o, I_b, xpix, ypix, xo, yo, rad)

	# Convert to Digital and Calculate SNR
	O = 0;
	for i in range(xpix):
		for j in range(ypix):
			O += ADC(field[i][j])

	print O	
	print ADC(I_o)

	B = ADC(I_b)
	
	return SNR(O,B,pixSub)
'''
def starSNR(field,xo,yo,rad,xb,yb,radb):

	# Get background:
	xpix = arange(math.floor(xb-radb),math.ceil(xb+radb),1)
	ypix = arange(math.floor(yb-radb),math.ceil(yb+radb),1)
	B = 0
	for i in xpix:
		for j in ypix:
			B += field[i][j]
	B /= (len(xpix)*len(ypix))

	# Get signal:
	xpix = arange(math.floor(xo-rad),math.ceil(xo+rad),1)
	ypix = arange(math.floor(yo-rad),math.ceil(yo+rad),1)
	O = 0
	for i in xpix:
		for j in ypix:
			O += field[i][j] - B
	
	print O
	print B
	print rad2pixSub(rad)
	return SNR(O,B,rad2pixSub(rad))	

# Calculate I_o from SNR and I_b:
def func(Io,Ib,sig2noise,pixSub):
	return sig2noise*sqrt(Io+Ib*pixSub)-Io
def getSigFromSNR(sig2noise,Ib,pixSub):
	guess = sig2noise*sqrt(Ib*pixSub)
	return fsolve(func,guess,args=(Ib,sig2noise,pixSub))
	
# Return a field normalized to the bit resolution
def bitnorm(field):
	xpix,ypix=shape(field)
	bitfield,_,_ = emptyframe(xpix,ypix)
	for i in range(xpix):
		for j in range(ypix):
			bitfield[i][j] = ADC(field[i][j])
	return bitfield

# Public function to set bit-resolution of image prior to working
def setbitres(bits):
	global bitres
	bitres = bits

# Get ADC value for analog signal (photoelectrons -> counts)
def ADC(sig):
	if sig > welldepth:
		return math.floor(2**bitres-1)
	else:
		return math.floor((sig/welldepth)*(2.0**bitres))

# Covert between pixSub and rad
def rad2pixSub(rad):
	#return math.ceil(pi*rad**2.0)
	return (rad*2.0)**2

def pixSub2rad(pixSub):
	# return sqrt(pixSub/pi)
	return sqrt(pixSub)/2.0

################### Gaussian Star Generation: ######################
# returns sigma corresponding to: FWHM = sigma*2*sqrt(2*ln(2)) 
def getsigmafromradius(radius):
	FWHM = radius*2.0
	return FWHM/(2.0*sqrt(2.0*math.log(2.0)))
	return radius*2.0/3.0

# Calculate sigma from width:
'''
def func2(sigma,w,I_o,I_b):
	return 8.0*log(Io/(2*pi*sqrt(I_b))) - 16.0*log(sigma) - w**2/sigma**2
def width2sigma(w,I_o,I_b):
	guess = sqrt(w**2/(8.0*log(Io/(2*pi*sqrt(I_b))) - 16.0*log(w/3.0)))
	return fsolve(func2,guess,args=(w,I_o,I_b))
'''
def func2(sigma,r,I_o,I_b):
	Amin = I_b + sqrt(I_b)
	return I_o/(2.0*pi*sigma**2.0)*exp(-r**2.0/(8.0*sigma**2.0)) - Amin

def rad2sigma(r,I_o,I_b):
	guess = sqrt(r**2.0/(8.0*log(I_o/(2.0*pi*sqrt(I_b))) - 16.0*log(r/3.0)))
	return fsolve(func2,guess,args=(r,I_o,I_b))

# Returns the maximum of a gaussian distribution of a specified sigma
def maxgauss(sigma):
	return sqrt(2.0*pi*sigma**2.0)**-1.0

# Returns 2D gaussian distribution
# A = amplitude
# xo,yo = center of distribution
# sigma_x = distribution in the xdirection
# sigma_y = distribution in the ydirection
def gengauss(A,xpix,ypix,xo,yo,sigma_x,sigma_y):
	_,x,y=emptyframe(xpix,ypix)
	xp = (x-xo)**2.0/(2.0*sigma_x**2.0)
	yp = (y-yo)**2.0/(2.0*sigma_y**2.0)
	exponent = -(xp+yp)
	return A*exp(exponent)

'''
# Returns the gaussian distribution of a specified sigma centered at x,y
def gengauss(x,y,sigma):
	_,xi,yi=emptyframe()
	r = sqrt((xi-x)**2.0 + (yi-y)**2.0)
	g = (1.0/sqrt(2.0*pi*sigma**2.0))*exp(-(r/(2.0*sigma**2.0))**2.0)
	return g
'''
# Returns the gaussian distribution of a specified width centered at x,y
#'''
def gennormgauss(I_o,xpix,ypix,xo,yo,sigma):
	_,x,y=emptyframe(xpix,ypix)
	E = -((x-xo)**2.0+(y-yo)**2.0)/(2.0*sigma**2.0)
	A = I_o / (2.0*pi*sigma**2)
	return A*exp(E)
'''
def gennormgauss(I_o,xpix,ypix,xo,yo,sigma_x,sigma_y):
	field,_,_=emptyframe(xpix,ypix)
	for i in range(xpix):
		for j in range(ypix):
			field[i,j] = normpdf(sqrt((xo-i)**2.0+(yo-j)**2.0),0.0,sqrt(sigma_x**2+sigma_y**2))
	return field*I_o
'''

# Generate star from gaussian
# I_o = intensity of star as point source (photoelectrons)
# xo,yo = center of star (pixels)
# radius = radius of star (pixels)
def stargenB(I_o,xpix,ypix, xo, yo, radius):
	sigma = getsigmafromradius(radius)
	return gengauss(I_o,xpix,ypix,xo,yo,sigma,sigma)
	
# Generate star in location x,y of defined SNR and radius
def stargenA(sig2noise,I_b,xpix,ypix,xo,yo,radius):
	I_o = getSigFromSNR(sig2noise,I_b,pixSub)
	sigma =	rad2sigma(radius,I_o,I_b)
	return gengauss(I_o,xpix,ypix,xo,yo,sigma,sigma)

# Generate star from gaussian
# I_o = intensity of star as point source (photoelectrons)
# xo,yo = center of star (pixels)
# radius = radius of star (pixels)
def stargenNormB(I_o,I_b,xpix,ypix, xo, yo, radius):
	sigma =	rad2sigma(radius,I_o,I_b)
	return gennormgauss(I_o,xpix,ypix,xo,yo,sigma)
	
# Generate star in location x,y of defined SNR and radius
def stargenNormA(sig2noise,I_b,xpix,ypix,xo,yo,radius):
	sigma = getsigmafromradius(radius)
	I_o = getSigFromSNR(sig2noise,I_b,pixSub)
	sigma =	rad2sigma(radius,I_o,I_b)
	return gennormgauss(I_o,xpix,ypix,xo,yo,sigma)
	
################### Noise Generation: ######################
# Generate a poisson random variable centered around lamda:
def poissonrandnum(lamda,length):
	if lamda == 0:
		return 0
	else:
		return poisson.rvs(lamda,0,size = length)

# Iterative poisson random number generator:
def poissonrandnum_it(lamda):
	L = exp(-lamda)
	k = 0
	p = 1
	while p > L:
		k += 1
 		p = p * rand.random()
 	return k-1

# add shot noise to image:
def addshotnoise(field):
	xpix,ypix=shape(field)
	for i in range(xpix):
		for j in range(ypix):
			field[i][j] = poissonrandnum(field[i][j],1)
			if field[i][j]<0:
				field[i][j] = 0
		print str((i+1)*100.0/xpix)+"% complete"
	return field
	
################# Test Functions ###################:
# Generate random field of stars with noise:
'''
def randfieldgen(xpix,ypix,num):
	field = genbackground(10,xpix,ypix)
	locations = []
	sig2noise = []
	radius = []
	for i in range(num):
		locations.append((rand.random()*xpix,rand.random()*ypix))
		sig2noise.append((rand.random()*17.0))
		radius.append((rand.random()*min((xpix,ypix))/(100.0) + min((xpix,ypix))/(200.0)))
		field = field + stargenA(xpix,ypix,locations[i][0],locations[i][1],sig2noise[i],radius[i])
	return bitnorm(addshotnoise(field)), locations, sig2noise,radius
'''
def randfieldgen(xpix,ypix,I_o,I_b):
	field = genbackground(I_b,xpix,ypix)
	locations = []
	sig2noise = []
	radius = []
	for i in range(len(I_o)):
		locations.append((rand.random()*xpix,rand.random()*ypix))
		radius.append((5*rand.random()+5))
		field = field + stargenNormB(I_o[i],I_b,xpix,ypix,locations[i][0],locations[i][1],radius[i])
		print "star " + str(i+1) + " of " + str(len(I_o))
	return bitnorm(addshotnoise(field)), locations,radius
	
# Generate all star magnitudes in succession and display:
def showallSNRfield(pixSub,I_b):
	radius = pixSub2rad(pixSub)
	field = genbackground(I_b,220,220)
	locations = []
	sig2noise = []
	for i in range(17):
		location = (30+10*i,30+10*i)
		sig2noise = i+1
		field += stargenA(sig2noise,I_b,220,220,location[0],location[1],radius)
	field = bitnorm(addshotnoise(field))
	return field

# Generate all star magnitudes in succession and display:
def showallPixSubfield(pixSub,I_o,I_b):
	xpix = 60+len(pixSub)*20
	field = genbackground(I_b,xpix,xpix)
	snr = zeros(len(pixSub))
	for i in range(len(pixSub)):
		location = (30+20*i,30+20*i)
		radius = pixSub2rad(pixSub[i])
		try:
			field += stargenNormB(I_o,I_b,xpix,xpix,location[0],location[1],radius)
		except TypeError: #occurs when fsolve fails in rad2sigma()
			continue
		snr[i] = SNR_ADC(I_o,I_b,pixSub[i])
	field = bitnorm(addshotnoise(field))
	return field,snr
	
# Generate star in center of frame that is of radius 1/2 size of frame with defined bit resolution:
def starcenterA(sig2noise,dimensions,starfraction):
	width = min((dimensions[0],dimensions[1]))/(starfraction**-1)
	center = [dimensions[0]/2.0,dimensions[1]/2.0]
	star = addshotnoise(stargenA(dimensions[0],dimensions[1],center[0],center[1],sig2noise,width/2.0)+genbackground(10,dimensions[0],dimensions[1]))
	return bitnorm(star),center

# Generate star in center of frame that is of radius 1/2 size of frame with defined bit resolution: 
#
# Inputs:
# I_o = signal of star (photoelectrons/image)
# I_b = ave signal of background (photoelectrons/pix/image)
# pixSub = # of pixels gaussian star is spread over ~= 3*sigma
#
# Outputs:
# star = the bit normalized FITS star image with noise added
# s2n = the signal to noise ratio of the star
# center = the centroid coordinates of the star in the frame
#
def starcenterB(I_o, I_b, pixSub):
	
	ratio = 3
	multHR = 11
	'''
	# Contruct highres image of star
	diamHR = sqrt(pixSub) * multHR       # calculate diameter of HR image
	res = int(ceil(diamHR) * ratio)      # calculate resolution of HR image
	center = [res/2.0,res/2.0]           # calculate center of HR star
	
	# Generate high res star:
	starHR = stargen(1, res, res, center[0], center[1], diamHR/2.0)
	'''
	# Set parameters for lowres star
	diam = sqrt(pixSub)                  # diameter of star in pixels
	res = int(ceil(diam) * ratio)        # calculate resolution of image
	center = [res/2.0,res/2.0]           # calculate center of star
	'''
	# Integrate over highres image to get lowres image
	star,_,_ = emptyframe(res,res)
	for i in range(res):
		for j in range(res):
			for l in range(multHR):
				for m in range(multHR):
					star[i][j] += starHR[l+multHR*i][m+multHR*j]
			star[i][j] = star[i][j]/(multHR**2)
	'''
	# Generate star:
	star = stargenB(I_o, res, res, center[0], center[1], diam/2.0)
	
	# Add noise and background:
	star = addshotnoise(star + genbackground(I_b,res,res))
	
	# Calculate SNR of star:
	s2n = I_o/sqrt(I_o + I_b*pixSub)  # SNR of star
		
	# Return bit normalized star, s2n, centroid
	return bitnorm(star),s2n,center

########### Write results to file ############
def writeout(text_file,I):
	m,n = I.shape
	for i in range(m):
		for j in range(n):
			text_file.write(str(int(I[i][j]))+'\n')

########### Write centroid results to file ############
def writeout_centroids(text_file,cntrd):
	for i in range(len(cntrd)):
		text_file.write(str(cntrd[i][0])+"\t"+str(cntrd[i][1])+'\n')

########### Read in image #################
def readimage(fname,I):
	m,n = I.shape
	text_file = open(fname, 'r')
	for i in range(m):
		for j in range(n):
			I[i][j] = text_file.readline()
	text_file.close()
	return I
	
########### Initialize results file ###########
def openfile(fname):
	text_file = open(fname, 'w')
	return text_file
		
###################### MAIN: #######################
'''
# Defines:
numstars   = 20            # num of stars in field
dimensions = (15,15)       # xpix,ypix
snr = 6                    # signal to noise ratio
starfraction = 1.0/3.0     # fraction of star filling the frame

# All intensities are for a 1 sec exposure
Ib = 335824.8442        # intensity of background at day
Ib = 1000.0				# approximate background at night

# 4th Mag @ Day:
Io4 = 2869185.9871      # intensity of object (6000 K)
# 5th Mag @ Day:
Io5 = 1142243.5151      # intensity of object (6000 K)

# 6th Mag @ Day:
Io6 = 454735.3339       # intensity of object (6000 K)

# 7th Mag @ Day:
Io7 = 181033.3971       # intensity of object (6000 K)

# 8th Mag @ Day:
Io8 = 72070.6935        # intensity of object (6000 K)

# Set-up:
close('all')
'''
'''
# Show centered star based on intensities:
starA,s2n,centerS = starcenterB(Io, Ib, 7**2)
print centerS
print s2n
showfield(1,starA)
'''
'''
# Show centered star based on s2n
starB,centerB = starcenterA(snr,dimensions,starfraction)
showfield(2,starB)
'''
'''
pixSub = 30
# Show all SNR field:
field = showallSNRfield(pixSub,Ib)
showfield(1,field)
'''
'''
pixSub = array([1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9.5,10])
#pixSub = [10]
#pixSub = array([3,3.5,4,4.5,5])
for i in range(len(pixSub)):
	pixSub[i] **= 2
field,snr = showallPixSubfield(pixSub,Io,Ib)
showfield(1,field)
print snr
'''
'''
num4 = 2
num5 = 3
num6 = 9
num7 = 29
num8 = 77

Io = zeros(120)

# Form Star List:
for i in range(num4):
	Io[i] = exposure*Io4
for i in range(num5):
	Io[i+num4] = exposure*Io5
for i in range(num6):
	Io[i+num4+num5] = exposure*Io6
for i in range(num7):
	Io[i+num4+num5+num6] = exposure*Io7
for i in range(num8):
	Io[i+num4+num5+num6+num7] = exposure*Io8

Ib *= exposure

# Show random star field:
xpix = 2560
ypix = 2160
field,locations,radius = randfieldgen(xpix,ypix,Io,Ib)

fname = "/home/andrew/big_image.txt"
image_file = openfile(fname)
writeout(image_file,field)
image_file.close()
fname = "/home/andrew/centroid_locations.txt"
text_file = openfile(fname)
writeout_centroids(text_file,locations)
text_file.close()

showfield(1,field)
'''
I,_,_ = emptyframe(2560,2160)
I = readimage("/home/andrew/big_image.txt",I)
showfield(2,I)

