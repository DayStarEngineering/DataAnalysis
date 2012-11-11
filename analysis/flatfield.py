__author__ = 'zachdischner'

"""
    Purpose: This file contains methods for cleaning up DayStar images.
             *  Gain Normalization
             *  Vignette Removal
             *  Background/Noise Subtraction?
"""

import numpy as np
import pylab as pylab
import math
from util import imgutil
from collections import Counter
# Get the mode   from collections import Counter
#                Counter(col).most_common(1)[0][0]

def test_Normalize():
    fn = "/Users/zachdischner/Desktop/StarTest_9_9_2012/Gray/img_1347267746_089087_00006_00017_0_gray.tif"
    fn = "/Users/zachdischner/Desktop/img_1348370245_127071_00175_00000_1.dat"
    img=imgutil.loadimg(fn,load_full=1)
    imgutil.dispimg(img,viewfactor=4.)
    pylab.title('Original Image')
    print "Original image median and standard deviation:  %s    and    %s  " % (np.median(img),np.std(img))

    i2 = NormalizeColumnGains(img,Plot=1,JustDark=1)
    pylab.title('Just Dark Row Normalization')
    print "Just using Dark rows, image size is: "
    print i2.shape
    print "Dark Row based image median and standard deviation:  %s    and    %s  " % (np.median(i2),np.std(i2))

    i3 = NormalizeColumnGains(img,Plot=1)
    pylab.title('Using Dark row and Whole Image Median')

    imgutil.dispimg(i2,viewfactor=4)
    pylab.title("Dark Row median normalization")

    print "Now using the entire image, image size is: "
    print i3.shape

    imgutil.dispimg(i3,viewfactor=4.)
    pylab.title('DR + Image Norm ')
    print "DR + Whole image median and standard deviation:  %s    and    %s  " % (np.median(i3),np.std(i3))

    # img is a numpy array

    img=imgutil.loadimg(fn)
    i4 = NormalizeColumnGains(img,Plot=1)
    pylab.title('Using Image Median')
    print "Now using the entire image, image size is: "
    print i4.shape

    imgutil.dispimg(i4,viewfactor=4.)
    pylab.title('Image Norm ')
    print "Just Whole image median and standard deviation:  %s    and    %s  " % (np.median(i4),np.std(i4))
    return i4

def NormalizeColumnGains(imgArray,target=None,PlotAll=None,Plot=1,JustDark=0):
    """
        Purpose: Normalize an image array to remove column gain bias. Designed for DayStar images.

        Inputs:

        Outputs:

        Example:
    """
#    img2=numpy.append(img,img,axis=0)

    if type(imgArray) == np.ndarray:
        if imgArray.shape == (2192,2592):       #Assumes this is a raw DayStar image
        # useful index numbers
            imgTstart = 0         # image rows top start
            imgTend = 1079        # image rows top end
            DRTstart = 1079       # dark rows top start
            DRTend = DRTstart+16  # dark rows top end
            DRBstart = DRTend     # dark rows bottom start
            DRBend = DRBstart+16  # dark rows bottom end
            imgBstart = DRBend    # image rows bottom start
            imgBend = 2159+32     # image rows bottom start
            DCstart = 16          # columns of dark rows start
            DCend = DCstart+2559  # columns of dark rows end


            imgTop = DarkColNormalize(imgArray[imgTstart:DRTend+1,:],top=1,Plot=PlotAll)   # No Dark Columns, Just Dark Rows and pic
            imgBottom = DarkColNormalize(imgArray[DRBstart:imgBend,:],Plot=PlotAll)

            #Normalize Both Images to the same gain setting
            if target is None:
                target=np.mean([np.median(imgTop),np.median(imgBottom)])
            topFactor = target/np.median(imgTop)
            bottomFactor = target/np.median(imgBottom)

            NormImg = np.append(imgTop*topFactor,imgBottom*bottomFactor,axis=0)

            # Return just the dark or both?
            if not JustDark:
                NormImg = NormalizeColumnGains(NormImg,target=target,PlotAll=PlotAll,Plot=Plot)

        else:
            NormImg = ImgColNormalize(imgArray)


        if Plot:
            PlotComparison(imgArray,NormImg,title="Full Image Gain Normalization")
        return NormImg
    else:
        raise RuntimeError('numpy ndarray input required. Try using loadimg() first.')

def DarkColNormalize(imgArray,top=0,target=None,Plot=None):
    """
        Purpose: Normalize image array based on dark columns.

        Inputs: imgArray -numpy array- image array
                top      -bool {optional}- Indicates if this is a "top" oriented image array. For top sensor half,
                          dark rows come after the information image array. Otherwise, this assumes the dark rows
                          come first.
    """
    rows,cols = imgArray.shape
    if top == 0:
        darkrows = imgArray[0:16,:]
    else:
        darkrows = imgArray[rows-16:rows,:]

    # Get target normalization
    if target is None:
        target = np.median(imgArray)

    # Get normalization factor
    norm_factor = []
    for col in range(0,cols):
        norm_factor.append(target/np.median(darkrows[:,col]))

    # Apply Normalization Factor
    new_imgArray = imgArray*norm_factor

    if Plot:
        if top:
            PlotComparison(imgArray,new_imgArray,title="Top Sensor Half")
        else:
            PlotComparison(imgArray,new_imgArray,title="Bottom Sensor Half")


    # Cut off dark rows and columns and return
    if top:
        final_image = new_imgArray[0:rows-16,16:cols-16]
    else:
        final_image = new_imgArray[15:rows-1,16:cols-16]
    return final_image



def ImgColNormalize(imgArray,target=None):
    "THIS WONT WORK UNLESS LOOKING AT SOMETHING FLAT"
    """
    Purpose: Normalize image array based on dark columns.

    Inputs: imgArray -numpy array- image array
            target   -desired norm level {optional}- Set this to the gain you wished the image normalized to. Otherwise
                      the overall image median is used by default.
    """
    rows,cols = imgArray.shape

    # Get target normalization
    if target is None:
        target = np.median(imgArray)

    # Get normalization factor
    norm_factor = []
    for col in range(0,cols):
        norm_factor.append(target/np.median(imgArray[:,col]))

    # Apply Normalization Factor
    new_imgArray = imgArray*norm_factor

    return new_imgArray

def mode(col):
    return Counter(col).most_common(1)[0]

def smooth(data,winsize=10):
    window=np.ones(int(winsize))/float(winsize)
    data2=np.convolve(data,window,'same')




def PlotComparison(old_img,new_img,title="Title"):
    """
        Purpose: Generate a 2x2 plot showing image statistics to compare before/after gain normalization

        Inputs: -old_img {numpy array}- Original pre-normalized image
                -old_img {numpy array}- Original pre-normalized image
    """
    rows,cols=new_img.shape
    oldstd=[]
    newstd=[]
    oldmed=[]
    newmed=[]
    for col in range(0,cols):
        oldstd.append(np.std(old_img[:,col]))
        newstd.append(np.std(new_img[:,col]))
        oldmed.append(np.median(old_img[:,col]))
        newmed.append(np.median(new_img[:,col]))

    randcol=pylab.randint(0,cols,800)
    randrow=pylab.randint(0,rows,800)

    pylab.figure(num=None, figsize=(13, 7), dpi=80, facecolor='w', edgecolor='k')
    pylab.title(title)

    #Standard Deviation Comparison
    pylab.subplot(2,2,1)
    pylab.plot(oldstd)
    pylab.plot(newstd)
    pylab.legend(['Before Normalization \sigma','After Normalization \sigma'])
    pylab.xlabel('Column')
    pylab.ylabel('USELESS Standard Deviation')

    pylab.subplot(2,2,3)
    pylab.plot(oldmed)
    pylab.plot(newmed)
    pylab.legend(['Before Normalization Median','After Normalization Median'])
    pylab.xlabel('Column')
    pylab.ylabel('Median')

    #fourrier signal
    pylab.subplot(2,2,2)
    pylab.hist(old_img[randrow,randcol],bins=75)
    pylab.xlabel('Hist')
    pylab.ylabel('Old Rand Selection Intensity')

    pylab.subplot(2,2,4)
    pylab.hist(new_img[randrow,randcol],bins=75)
    pylab.xlabel('Hist')
    pylab.ylabel('New Rand Selection Intensity')

