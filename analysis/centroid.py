import chzphot as chzphot
import numpy as np
import copy as cp
        
def centroid(input_image, k_thresh=4, k_sigma=4, min_pix_per_star=5, max_pix_per_star=50):
    
    def findStars(limit):
    
        def dfs((s,t)):
        
            def neighbors((i, j)):
                return [(i+1,j),(i+1,j-1),(i,j-1),(i-1,j-1),(i-1,j),(i-1,j+1),(i,j+1),(i+1,j+1)]
                
            stack = [(s, t)]
            star = [((s,t),image[s,t])]
            
            while stack:
                #Pop last element into node (s,t)
                #print 'stack: ' + str(stack)
                pixel = stack.pop()
                #print 'popped: ' + str(pixel)
                
                neighborhood = neighbors(pixel)
                #print 'neighborhood: ' + str(neighborhood) + str(len(neighborhood))
                
                for neighbor in neighborhood:
                    #print neighbor
                    #print image[neighbor]
                    try:
                        if image[neighbor] > limit:
                            stack.append(neighbor)
                            star.append((neighbor,image[neighbor]))
                            image[neighbor] = 0
                    except IndexError:
	                    continue
		                
            # Is this star too small?
            #print len(star)
            if len(star) < min_pix_per_star or len(star) > max_pix_per_star:
                return []
                
            return star
        
        def cog(star):
            n = 0.0
            x_center = 0.0
            y_center = 0.0
            for pixel in star:
                x,y = pixel[0]
                value = pixel[1]
                x_center += value*x
                y_center += value*y
                n += value
            x_center /= n
            y_center /= n
            return (x_center,y_center)
    
        star_centers = []
        for (x,y), pixel in np.ndenumerate(image):
            if pixel > limit:
                blob = dfs((x,y))
                if blob:
                    star_centers.append(cog(blob))
        return star_centers
               
    # First. lets make a local copy of our image:
    image = cp.deepcopy(input_image)
    
    # Get the robust mean and standard deviation:
    mean,std = chzphot.robomad(image,k_thresh)
    print 'robust mean: ' + str(mean) + ' robust std: ' + str(std)
    
    # Define the star limit:
    limit = mean + k_sigma*std
    print 'limit: ' + str(limit)
    
    # Identify stars in the frame:
    centroid_guesses = findStars(limit)
    
    # Improve our centroids on the stars found:
     

    # Return the results:
    return centroid_guesses
    

