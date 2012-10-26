#
# File name: centroid.py
# Authors: Nick Truesdale, Kevin Dinkel
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

# Enable import from other dirs in DataAnalysis
import sys
sys.path.append("../")

# Addtl imports for main script
from util import imgutil as imgutil
from util import submethods as subm

# Imports for functions
import chzphot as chzphot
import numpy as np
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

    def _findStars(limit):
    
        def dfs((s,t)):
        
            # Neighborhood generator:
            def neighbors((i, j)):
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
def iwcentroid(frame, (x0,y0), p=2):
    '''
    IWC is Intensity Weighted Centroiding. The method calculates the center of mass of
    the star defined by the coordinates (x0,y0) in the subset of the image defined by 
    frame. The integer p is the intensity weight; p=2 is the default, p=1 would be the
    normal center of mass. 
    '''
         
     
    # Get indices of subframe
    X,Y = indices(frame.shape)

    # Get values of subframe and raise them to the p
    values = image[ylow:yhi, xlow:xhi]**p
    valsum = values.sum()
    
    # Weighted center of mass
    xf = (X*values).sum() / valsum + xlow
    yf = (Y*values).sum() / valsum + ylow
    
    return (xf,yf)

#-----------------------------------------------------------------------------------------------
def gcentroid(image, (x0,y0), radius, width):
    '''
    Uses the two center coordinates of a Gaussian fit as the centroid estimate.
      p = (amp, xcenter, ycenter, xwidth, ywidth) 
    '''
    
    
    width_x = sqrt(abs((arange(col.size)-y)**2*col).sum()/col.sum())
    width_y = sqrt(abs((arange(row.size)-x)**2*row).sum()/row.sum())

    
    # Initial guess for Gaussian parameters
    guess = (frame.max(), x0, y0, width, width) 
    
    # Error function
    errfun = lambda p: ravel(gaussian(*p)(*indices(frame.shape)) - frame)
    
    
    # Optimize with least squares fit
    p, success = sci.optimize.leastsq(errfun, guess)
    (_, xf, yf, _, _) = p
    
    
    return (xf,yf)

#-----------------------------------------------------------------------------------------------
def gaussian(amp, xcent, ycent, wx, wy):
    '''
    Returns a G(x,y), where G is a Gaussian defined by the amplitude, x/y 
    center values, and x/y widths.
    '''
    wx = float(wx)
    wy = float(wy) 
    
    return lambda x,y: amp*exp(-(((xcent-x)/wx)**2+((ycent-y)/wy)**2)/2)


#-----------------------------------------------------------------------------------------------
def subframe(image, (x0,y0), width):
    '''
    This function takes an image and, given a star location and radius, finds the indices
    for the subframe that surrounds the star without going outside the image boundaries.
    '''
    
    # Radius from center
    radius = 0.5*width
    
    # Image boundaries
    (xbound, ybound) = image.shape
    
    print (xbound, ybound)
    
    # Calculate boundaries
    xlow = np.floor(x0 - radius)
    ylow = np.floor(y0 - radius)
    xhi = np.ceil(x0 + radius)
    yhi = np.ceil(y0 + radius)

    print (xlow, xhi, ylow, yhi)

    # Ensure boundaries lie within image
    if xlow < 0: xlow = 0
    if ylow < 0: ylow = 0
    if xhi > xbound: xhi = xbound
    if yhi > xbound: yhi = ybound
     
    # Define frame from indices
    frame = image[ylow:yhi, xlow:xhi]
     
    return frame, (xlow, ylow)

# ------------
# --- MAIN ---
# ------------

def main():

    import sys
    sys.path.append("../")

    # Load the image:
    image = imgutil.loadimg('/home/sticky/Daystar/img_1348368011_459492_00146_00000_1.dat')
    
    # Get a good estimation for the background level and variance:
    (mean,std) = frobomad(image)

    # Do column subtraction:
    image = subm.colmeansub(image)

    # Find star centroids:
    centroids = findstars(image,std=std,debug=True)

    # Use the first centroid to test
    for each in centroids:
        print each
       
    (y0, x0) = centroids[1]
    frame, (xf,yf) = subframe(image, (x0,y0), 14)
    
    print frame

    # Display image:
    imgutil.dispimg(image,5)

    # Display image with stars circled:
    #imgutil.circstars(image,centroids,25)
    
    return 0
    
    
# -------------------
# --- Run as Main --- 
# -------------------
if __name__ == "__main__":
	sys.exit(main())
	
