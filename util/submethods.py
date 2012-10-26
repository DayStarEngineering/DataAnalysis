# Jed Diller
# 10/8/12
# subtraction methods

import numpy as np

# ----------------------- Dark Column Subtraction ----------------------
# darkcolsub(): subtraction done using dark row information captured
# in DayStar images. The columns of the dark rows (16 rows per half) are
# averaged and that average is subtracted from the entire column on half
# of the image
# returns a numpy ndarray of the same size
# image has to be loaded before subtraction methods can be called
def darkcolsub(imgArray):

    if type(imgArray) == np.ndarray:
        if imgArray.shape == (2192,2592):
        
            # useful index numbers
            imgTstart = 0          # image rows top start
            imgTend = 1080         # image rows top end
            DRTstart = 1080       # dark rows top start
            DRTend = DRTstart+16  # dark rows top end
            DRBstart = DRTend   # dark rows bottom start
            DRBend = DRBstart+16  # dark rows bottom end
            imgBstart = DRBend   # image rows bottom start
            imgBend = 2160+32      # image rows bottom start 
            DCstart = 16          # columns of dark rows start
            DCend = DCstart+2560  # columns of dark rows end
            
            # get top dark row column averages
            DRCTavgs = np.ones((1,DCend-DCstart), dtype=np.uint16)
            temp = np.ones((1,16),dtype=np.uint16)

            i = 0
            for col in xrange(DCstart,DCend):
                j = 0
                for row in xrange(DRTstart,DRTend):
                    temp[0][j] = imgArray[row][col]
                    j = j+1
                DRCTavgs[0][i] = int(np.average(temp))
                i = i+1

            # get bottom dark row column averages
            DRCBavgs = np.ones((1,DCend-DCstart), dtype=np.uint16)

            i = 0
            for col in xrange(DCstart,DCend):
                j = 0
                for row in xrange(DRBstart,DRBend):
                    temp[0][j] = imgArray[row][col]
                    j = j+1
                DRCBavgs[0][i] = int(np.average(temp))
                i = i+1

            # subtract for columns of top image area
            i = 0
            for col in xrange(DCstart,DCend):
                for row in xrange(imgTstart,imgTend):
                    newval = imgArray[row][col] - DRCTavgs[0][i]
                    imgArray[row][col] = newval
                i = i+1

            # subtract for columns of bottom image area
            i = 0
            for col in xrange(DCstart,DCend):
                for row in xrange(imgBstart,imgBend):
                    newval = imgArray[row][col] - DRCBavgs[0][i]
                    imgArray[row][col] = newval
                i = i+1
            
            # return subtracted image
            return imgArray
        else:
            raise RuntimeError('darkcolsub(): 2192x2592 image required.')
                
    else:
        raise RuntimeError('numpy ndarray input required. Try using loadimg() first.')


# ----------------------- Column Mean Subtraction ----------------------
def colmeansub(imgArray):

    if type(imgArray) == np.ndarray:
        if imgArray.shape == (2160,2560):
            # useful index numbers
            TRstart = 0          # image rows top start
            TRend = 1080         # image rows top end
            BRstart = TRend   # image rows bottom start
            BRend = 2160      # image rows bottom start 
            Cstart = 0          # columns of dark rows start
            Cend = 2560  # columns of dark rows end
            
            topAvgs = np.ones((1,2560),dtype=np.uint16)
            bottAvgs = np.ones((1,2560),dtype=np.uint16)

            # top and botton column averages
            for col in range(Cstart,Cend):
                topAvgs[0][col] = int(np.average(imgArray[TRstart:TRend][:,col:col+1]))
                bottAvgs[0][col] = int(np.average(imgArray[BRstart:BRend][:,col:col+1]))      
            
            # subtract for columns of top image area
            def subtract_uint16(a, b):
                '''Subtraction to avoid overflow problems and negatives. If the difference a-b 
                is less than 0 it is assigned the value 0.'''
                A = int(a) # signed int32
                B = int(b) # signed int32
                if A-B < 0:
                    return (np.uint16(0)) # return 0
                else:
                    return (a-b)
            
            for col in xrange(Cstart,Cend):
                for row in xrange(TRstart,TRend):
                    imgArray[row][col] = subtract_uint16(imgArray[row][col], topAvgs[0][col])
                for row in xrange(BRstart,BRend):
                    imgArray[row][col] = subtract_uint16(imgArray[row][col], bottAvgs[0][col])
            
            # return subtracted image
            return imgArray

        else:   
           raise RuntimeError('colmeansub(): image must be 2160x2560')                
    else:
        raise RuntimeError('numpy ndarray input required. Try using loadimg() first.')
        
    
# ----------------------- Column 2 Sigma Subtraction ----------------------
def colsigsub(imgArray):

    if type(imgArray) == np.ndarray:
        if imgArray.shape == (2160,2560):
            # useful index numbers
            TRstart = 0          # image rows top start
            TRend = 1080         # image rows top end
            BRstart = TRend   # image rows bottom start
            BRend = 2160      # image rows bottom start 
            Cstart = 0          # columns of dark rows start
            Cend = 2560  # columns of dark rows end
            
            sigmult = 2 # 2 sigma
            
            # allocate arrays 
            topAvgs = np.ones((1,2560),dtype=np.uint16)
            bottAvgs = np.ones((1,2560),dtype=np.uint16)

            # top and bottom column average in simga range
            print 'getting sigma averages...'
            for col in range(Cstart,Cend):
                
                print 'getting col', col, 'mean and std...'
                
                topcol = imgArray[TRstart:TRend][:,col:col+1]
                bottcol = imgArray[BRstart:BRend][:,col:col+1]
                
                topmean = int(np.average(topcol))
                bottmean = int(np.average(bottcol))
                topstd = int(np.std(topcol))
                bottstd = int(np.std(bottcol))
                
                # if in sigma range, add to array
                topsum = 0
                bottsum = 0
                topcount = 0
                bottcount = 0
                
                print 'getting col', col, 'mean in', sigmult, 'sigma range...'
                
                for row in range(0,1080): 
                    if topcol[row][0] in range(topmean-sigmult*topstd, topmean+sigmult*topstd+1):
                        topsum = topsum + int(topcol[row][0])
                        topcount = topcount + 1
                    if bottcol[row][0] in range(bottmean-sigmult*bottstd, bottmean+sigmult*bottstd+1):
                        bottsum = bottsum + int(bottcol[row][0])
                        bottcount = bottcount + 1

                # average applicable values
                topAvgs[0][col] = topsum/topcount
                bottAvgs[0][col] = bottsum/bottcount
            
            # subtract for columns of top image area
            print 'subtracting averages...'
            def subtract_uint16(a, b):
                '''Subtraction to avoid overflow problems and negatives. If the difference a-b 
                is less than 0 it is assigned the value 0.'''
                A = int(a) # signed int32
                B = int(b) # signed int32
                if A-B < 0:
                    return (np.uint16(0)) # return 0

                else:
                    return (a-b)
            
            for col in xrange(Cstart,Cend):
                for row in xrange(TRstart,TRend):
                    imgArray[row][col] = subtract_uint16(imgArray[row][col], topAvgs[0][col])
                for row in xrange(BRstart,BRend):
                    imgArray[row][col] = subtract_uint16(imgArray[row][col], bottAvgs[0][col])
            
            # return subtracted image
            return imgArray

        else:   
           raise RuntimeError('colsigsub(): image must be 2160x2560')                
    else:
        raise RuntimeError('numpy ndarray input required. Try using loadimg() first.')
        
        
        
        
    
