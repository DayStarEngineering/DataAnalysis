#
# File name: centroid.py
# Authors: Kevin Dinkel, Nick Truesdale
# Created: 10/15/2012
# Edited: 10/25/2012
#
# Description: This file contains functions for locating stars in an image and finding
# their centroids. The main script  
#
# Function List:
#   hist_median(image)
#   fMAD(image)
#   frobomad(image, thresh=3)
#   findstars(input_image, k_thresh=3, k_sigma=3, min_pix_per_star=5, max_pix_per_star=50, 
#             oblongness=2, mean=None, std=None, debug=False)
#   iwcentroid(...)
#   gcentroid

# -------------------------
# --- IMPORT AND GLOBAL ---
# -------------------------

# Imports for functions
import sys
import numpy as np
import scipy as sci
from scipy import optimize
import copy as cp
import time

# -----------------
# --- FUNCTIONS ---
# -----------------

def hist_median(image):
    ''' 
    Histogram median finding method. A faster median finding
    method for images of discrete size and integer values.
    Method derived by: Andrew Zizzi & Kevin Dinkel
    Implemented by: Kevin Dinkel
    '''
    n = np.size(image)/2
    bins = np.bincount(image.ravel().astype(int))
    
    ind = 0
    while n > 0:
        n -= bins[ind]
        ind += 1
    
    return float(ind-1)

#-----------------------------------------------------------------------------------------------    
def fMAD(image):
    ''' 
    Returns the Medians and Median Absolute Deviation of an array
    using the fast histogram median finding method for images.
    '''
    m = hist_median(image)
    dif = abs(image - m)
    s = hist_median(dif)

    return(m, s)

#-----------------------------------------------------------------------------------------------
def frobomad(image, zvalue=3):
    '''
    Fast and robust estimation of the mean and absolute value of an image.
    Uses fMAD and the histogram median method for speed.
    '''
    
    #STEP 1: Start by getting the median and MAD as robust proxies for the mean and sd.
    m,s = fMAD(image)
    sd = 1.4826 * s

    if (sd < 1.0e-14):
        return(m,sd)
    else:
    
		#STEP 2: Identify outliers, recompute mean and std with pixels that remain.
		gdPix = np.where(abs(image - m) < zvalue*sd)
		m1 = np.mean(image[gdPix])
		sd1 = np.std(image[gdPix])
		
		#STEP 3: Repeat step 2 with new mean and sdev values.
		gdPix = np.where(abs(image - m1) < (zvalue*sd1))
		m2 = np.mean(image[gdPix])
		sd2 = np.std(image[gdPix])
		
		return(m2, sd2)
		
#-----------------------------------------------------------------------------------------------
def findstars(input_image, zreject=3, zthresh=3, min_pix_per_star=6, max_pix_per_star=50, oblongness=1.5, mean=None, std=None, debug=False):
    '''
    Given an image, this function will return a set of approximate star centers and their widths in the following form:
    
    [((x1_center,y1_center),(x1_width,y1_width)), 
     ((x2_center,y2_center),(x2_width,y2_width)), ... etc. ] 
    
    There are many optional parameters that you can provide to aid in the star
    finding process:
             zreject = any pixel values > zreject*sigma, will be discarded from the background 
                       estimation as outliers. sigma (std of image) is calculated with frobomad
             zthresh = any pixel values < zthresh*sigma will be regarded as too dim to be part of a star
    min_pix_per_star = minimum # of pixels you consider to be in a valid star
    max_pix_per_star = maximum # of pixels you consider to be in a valid star
          oblongness = xwidth/ywidth of bright blob must be < oblongness to be considered a valid star
                       (ywidth is numerator if bigger), this makes sure stars are round
                mean = use this mean as the robust estimation for the background instead of calculating it
                 std = use this standard deviation as the robust estimateion for the background standard deviation
                       instead of calculating it
    '''
    def _findStars(limit):
        '''
        Find stars based on calculated background limit.
        '''
        def dfs((s,t)):
            '''
            Run depth first search on a bright pixel at coordinates (s,t). We explore
            around a bright pixel to see if we have a star.
            '''
            # Neighborhood generator:
            def neighbors((i, j)):
                '''
                This generator yields the location of the next dfs neighbor around a pixel
                located at (i,j)
                '''
                yield (i+1,j)
                yield (i+1,j-1)
                yield (i,j-1)
                yield (i-1,j-1)
                yield (i-1,j)
                yield (i-1,j+1)
                yield (i,j+1)
                yield (i+1,j+1)
            
            # Initialize stack and star coordinates:
            stack = [(s, t)]
            x = [s]
            y = [t]
            value = [image[s,t]]
            #star = [((s,t),image[s,t])]

            # Run DFS:
            while stack:
                pixel = stack.pop()
                neighborhood = neighbors(pixel)
                for neighbor in neighborhood:
                    try:
                        if image[neighbor] > limit:
                            stack.append(neighbor)
                            x.append(neighbor[0])
                            y.append(neighbor[1])
                            value.append(image[neighbor])
                            #star.append((neighbor,image[neighbor]))
                            image[neighbor] = 0
                            
                    except IndexError:
	                    continue
		                
            # Is this blob too small or too big to be a star?
            n = len(x)
            if n < min_pix_per_star or n > max_pix_per_star:
                return []
                
            # Is the blob round enough?
            xsize = float(np.ptp(x))
            ysize = float(np.ptp(y))
            try:
                if xsize > ysize:
                    if xsize/ysize > oblongness:
                        return []
                else:
                    if ysize/xsize > oblongness:
                        return []
            except ZeroDivisionError:
                return []
            
            return zip(zip(y,x),value)
        
        def cog(star):
            '''
            Internal intensity weighted center of gravity method. This is used to find the 
            approximate center of a star.
            '''
        
            xi = np.array([float(p[0][0]) for p in star])
            yi = np.array([float(p[0][1]) for p in star])
            wi = np.array([float(p[1]) for p in star])
            n = sum(wi)
            xc = sum(xi*wi)/n
            yc = sum(yi*wi)/n
            wx = np.ptp(xi)
            wy = np.ptp(yi)
            return (xc,yc),(wx,wy)
    
        star_centers = []
        cnt = 0
        tic = time.clock()
        
        # Find pixels locations greater than limit:
        locations = (image > limit).nonzero()
        locations = zip(*locations) # transpose
        
        # Run dfs on all of these good pixels:
        for xy in locations:
            if image[xy] > limit:
                blob = dfs(xy)
                if blob:
                    star_centers.append(cog(blob))

        return star_centers
               
    # First. lets make a local copy of our image:
    image = cp.deepcopy(input_image)
    
    # Get the robust mean and standard deviation:
    tic = time.clock()
    if mean is None or std is None:
        robomean,robostd = frobomad(image,zreject)
    if mean is None:
        mean = robomean 
    if std is None:
        std = robostd
    toc = time.clock()
    
    if debug:
        print 'frobomad: ' + str(toc - tic) + ' s'
        print 'robust mean: ' + str(mean) + ' robust std: ' + str(std)
    
    # Define the star limit:
    limit = mean + zthresh*std
    if limit < 1:
        limit = 1
    if debug:
        print 'limit: ' + str(limit)
    
    # Identify stars in the frame:
    tic = time.clock()
    centroid_guesses = _findStars(limit)
    toc = time.clock()
    
    if debug:
        print 'find stars: ' + str(toc - tic) + ' s'
    
    # Return the results:
    return centroid_guesses

#-----------------------------------------------------------------------------------------------
def imgcentroid(image, centers, method="iwc"):
    '''
    This function uses one of the centroiding methods to improve the list of centroids
    given by centers in the given image.
    '''
    
    # Initialize list of refined centroids
    star_list = []
    
    for star in centers:
        (centroid, width) = star           
        
        # Use the first centroid to test      
        (frame, (xframe,yframe), frame_centroid) = subframe(image, centroid, width)
                        
        # Get centroid
        if method is "cog":
            (xstar,ystar) = iwcentroid(frame, 1)
        elif method is "iwc":
            (xstar,ystar) = iwcentroid(frame, 2)
        elif method is "gauss":
            (xstar,ystar) = gcentroid(frame, frame_centroid)
        else:
            raise RuntimeError("Bad method. Choices are ""cog"", ""iwc"" and  ""gauss""") 
        
        star_list.append( (xstar + xframe, ystar + yframe) )
        
    return star_list        
                
#-----------------------------------------------------------------------------------------------
def iwcentroid(frame, p=2):
    '''
    IWC is Intensity Weighted Centroiding. The method calculates the center of mass of
    the star defined by the coordinates (x0,y0) in the subset of the image defined by 
    frame. The integer p is the intensity weight; p=2 is the default, p=1 would be the
    normal center of mass. 
    '''   
     
    # Get indices of subframe
    Y,X = np.indices(frame.shape)

    # Get values of subframe and raise them to the p
    values = frame**p
    valsum = values.sum()
    
    # Weighted center of mass
    xf = (X*values).sum() / valsum
    yf = (Y*values).sum() / valsum
    
    return (xf,yf)

#-----------------------------------------------------------------------------------------------
def gcentroid(frame, (x0,y0)):
    '''
    Uses the two center coordinates of a Gaussian fit as the centroid estimate.
      p = (amp, xcenter, ycenter, xwidth, ywidth) 
    '''
    
    # Estimate Gaussian width
    row = frame[int(x0),:]
    col = frame[:,int(y0)]
    xwidth = np.sqrt( abs( (np.arange(col.size)-y0)**2*col ).sum()/col.sum() )
    ywidth = np.sqrt( abs( (np.arange(row.size)-x0)**2*row ).sum()/row.sum() )
    
    # Initial guess for Gaussian parameters
    guess = (frame.max(), x0, y0, xwidth, ywidth) 
    
    # Error function
    errfun = lambda p: np.ravel(gaussian(*p)(*np.indices(frame.shape)) - frame)
    
    # Optimize with least squares fit
    p, success = sci.optimize.leastsq(errfun, guess)
    (_, xf, yf, _, _) = p
    
    return (xf,yf)

#-----------------------------------------------------------------------------------------------
def gaussian(amp, xcent, ycent, wx, wy):
    '''
    Returns a function G(x,y), where G is a Gaussian defined by the amplitude, x/y 
    center values, and x/y widths.
    '''  
    return lambda y,x: amp*np.exp( -0.5*( ((xcent-x)/wx)**2 + ((ycent-y)/wy)**2 ) )

#-----------------------------------------------------------------------------------------------
def subframe(image, (x0,y0), (xwidth, ywidth), scale=1):
    '''
    This function takes an image and, given a star location and te width of the light 
    pattern, finds the subframe that surrounds the star without going outside the image
    boundaries.
    '''    
    # Image boundaries
    (ybound, xbound) = image.shape
        
    # Width to use
    xw = int(scale*xwidth)
    yw = int(scale*ywidth)

    # Calculate boundaries (upper boundary is one greater than actual index)
    xlow = int(x0) - xw
    ylow = int(y0) - yw
    xhi = int(x0) + xw + 1
    yhi = int(y0) + yw + 1
    
    # Ensure boundaries lie within image
    if xlow < 0: xlow = 0
    if ylow < 0: ylow = 0
    if xhi > xbound: xhi = xbound
    if yhi > ybound: yhi = ybound
     
    # Define frame from indices
    frame = image[ylow:yhi, xlow:xhi]
    
    # Define centroid coordinates relative to the frame
    xcent = x0 - xlow
    ycent = y0 - ylow
     
    return frame, (xlow, ylow), (xcent, ycent)

# ------------
# --- MAIN ---
# ------------

def main():

    # Enable import from other dirs in DataAnalysis
    sys.path.append("../")

    # Addtl imports for main script
    from util import imgutil as imgutil
    from util import submethods as subm

    # Load the image:
    image = imgutil.loadimg('/home/kevin/Desktop/img_1348368011_459492_00146_00000_1.dat')
        
    # Get a good estimation for the background level and variance:
    (mean,std) = frobomad(image)

    # Do column subtraction:
    image = subm.colmeansub(image)

    # Find star centroids:
    centroids = findstars(image,std=std,debug=True)
    
    # Refine centroids using three methods 
    iwc = imgcentroid(image, centroids, "iwc")
    gauss = imgcentroid(image, centroids, "gauss")
    
    print "---"
    for each in centroids:
        print each
    
    print "---"
        
    for each in iwc:
        print each
        
    print "---"
    for each in gauss:
        print each 
      
    # Display image:
    imgutil.dispimg(image,5)

    # Display image with stars circled:
    imgutil.circstars(image,iwc + gauss,1)
    
    return 0
    
    
# -------------------
# --- Run as Main --- 
# -------------------
if __name__ == "__main__":
	sys.exit(main())
	
