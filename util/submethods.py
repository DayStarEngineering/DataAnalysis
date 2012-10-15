# Jed Diller
# 10/8/12
# subtraction methods

import numpy as np

# ----------------------- Dark Column Subtraction ----------------------
# darkcolsub(): subtraction done using dark columns information captured
# in DayStar images. The columns of the dark rows (16 rows per half) are
# averaged and that average is subtracted from the entire column on half
# of the image
# returns a list of the same size
# image has to be loaded before subtraction methods can be called
def darkcolsub(imgArray):

    if type(imgArray) == np.ndarray:
        # useful index numbers
        imgTstart = 0          # image rows top start
        imgTend = 1079         # image rows top end
        DRTstart = 1080       # dark rows top start
        DRTend = DRTstart+16  # dark rows top end
        DRBstart = DRTend+1   # dark rows bottom start
        DRBend = DRBstart+16  # dark rows bottom end
        imgBstart = DRBend+1   # image rows bottom start
        imgBend = 2160+32-1      # image rows bottom start 
        DCstart = 16          # columns of dark rows start
        DCend = DCstart+2560-1  # columns of dark rows end

        
        # get top dark row column averages
        DRCTavgs = np.ones((1,DCend-DCstart), dtype=np.uint8)
        temp = np.ones((1,16),dtype=np.uint8)

        i = 0
        for col in xrange(DCstart,DCend):
            j = 0
            for row in xrange(DRTstart,DRTend):
                temp[0][j] = imgArray[row][col]
                j = j+1
            DRCTavgs[0][i] = int(np.average(temp))
            i = i+1
        print DRCTavgs

        # get bottom dark row column averages
        DRCBavgs = np.ones((1,DCend-DCstart), dtype=np.uint8)

        i = 0
        for col in xrange(DCstart,DCend):
            j = 0
            for row in xrange(DRBstart,DRBend):
                temp[0][j] = imgArray[row][col]
                j = j+1
            DRCBavgs[0][i] = int(np.average(temp))
            i = i+1

        print DRCBavgs

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
        raise RuntimeError('numpy ndarray input required. Try using loadimg() first.')


# ----------------------- Column Mean Subtraction ----------------------
# def colmeansub(imgIn):
    
