import chzphot as chzphot
import numpy as np
import copy as cp
import time

    
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
    
def fMAD(image):
    ''' 
    Returns the Medians and Median Absolute Deviation of an array
    using the fast histogram median finding method for images.
    '''
    m = hist_median(image)
    dif = abs(image - m)
    s = hist_median(dif)

    return(m, s)

def frobomad(image, thresh):
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
		gdPix = np.where(abs(image - m) < thresh*sd)
		m1 = np.mean(image[gdPix])
		sd1 = np.std(image[gdPix])
		
		#STEP 3: Repeat step 2 with new mean and sdev values.
		gdPix = np.where(abs(image - m1) < (thresh*sd1))
		m2 = np.mean(image[gdPix])
		sd2 = np.std(image[gdPix])
		
		return(m2, sd2)
		
def centroid(input_image, k_thresh=4, k_sigma=6, min_pix_per_star=5, max_pix_per_star=50):
    
    def findStars(limit):
    
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
            star = [((s,t),image[s,t])]
            
            # Run DFS:
            while stack:
                pixel = stack.pop()
                neighborhood = neighbors(pixel)
                for neighbor in neighborhood:
                    try:
                        if image[neighbor] > limit:
                            stack.append(neighbor)
                            star.append((neighbor,image[neighbor]))
                            image[neighbor] = 0
                    except IndexError:
	                    continue
		                
            # Is this blob too small or too big to be a star?
            if len(star) < min_pix_per_star or len(star) > max_pix_per_star:
                return []
                
            return star
        
        def cog(star):
            xi = np.array([float(p[0][0]) for p in star])
            yi = np.array([float(p[0][1]) for p in star])
            wi = np.array([float(p[1]) for p in star])
            n = sum(wi)
            xc = sum(xi*wi)/n
            yc = sum(yi*wi)/n
            return (xc,yc)
    
       
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
    mean,std = frobomad(image,k_thresh)
    toc = time.clock()
    print 'frobomad: ' + str(toc - tic)
    print 'robust mean: ' + str(mean) + ' robust std: ' + str(std)
    
    # Define the star limit:
    limit = mean + k_sigma*std
    print 'limit: ' + str(limit)
    
    # Identify stars in the frame:
    centroid_guesses = findStars(limit)
    
    # Improve our centroids on the stars found:

    # Return the results:
    return centroid_guesses


