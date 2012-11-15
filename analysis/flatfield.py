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
from analysis import centroid as centroid
import time
# Get the mode   from collections import Counter
#                Counter(col).most_common(1)[0][0]

def test_Normalize_proc(Method="mean"):
    "Use this to test the procedural differences in image normalization"
    fn = "/Users/zachdischner/Desktop/StarTest_9_9_2012/Gray/img_1347267746_089087_00006_00017_0_gray.tif"
    fn = "/Users/zachdischner/Desktop/img_1348370245_127071_00175_00000_1.dat"
    img=imgutil.loadimg(fn,load_full=1)
#    imgutil.dispimg(img,viewfactor=4.)
    print "Using " + Method + " Method for normalization"
    print ""
    print "Original image mean and standard deviation:  %s    and    %s  " % (np.mean(img),np.std(img))

    i2 = NormalizeColumnGains(img,Plot=1,JustDark=1,Method=Method)
    pylab.title('Just Dark Row Normalization Using ' + Method )
    print "Just using Dark rows, image size is: "
    print i2.shape
    print "Dark Row based image mean and standard deviation:  %s    and    %s  " % (np.mean(i2),np.std(i2))


    i3 = NormalizeColumnGains(img,Plot=1,Method=Method)
    pylab.title('Using Dark row and Whole Image Using ' + Method )



    print "Now using the entire image, image size is: "
    print i3.shape

#    imgutil.dispimg(i3,viewfactor=4.)
#    pylab.title('DR + Image Norm ')
    print "DR + Image Column mean and standard deviation:  %s    and    %s  " % (np.mean(i3),np.std(i3))


    ## DR and Row and Column Normalization
#    t=time.time()
#    img=imgutil.loadimg(fn)
#    i4 = NormalizeColumnGains(img)
#    # Also do row normalization
#    i4 = NormalizeColumnGains(img,Plot=1,Rows=1)
#    pylab.title('Using DR + Column + Row Using ' + Method )
#    print "Took %s seconds" % (time.time()-t)
#    print "Now using the entire image, image size is: "
#    print i4.shape

#    imgutil.dispimg(i4,viewfactor=4.)

#    print "DR + Row + Col Rmean and standard deviation:  %s    and    %s  " % (np.median(i4),np.std(i4))


    pylab.figure()
    pylab.subplot(2,2,1)
    pylab.imshow(np.multiply(img[0::5,0::5],4), cmap=None, norm=None, aspect=None, interpolation='nearest', vmin=0, vmax=2048, origin='upper')
    pylab.title('Original Image')

    pylab.subplot(2,2,2)
    pylab.imshow(np.multiply(i2[0::5,0::5],4), cmap=None, norm=None, aspect=None, interpolation='nearest', vmin=0, vmax=2048, origin='upper')
    pylab.title('DR and Col Using ' + Method)


    pylab.subplot(2,2,3)
    pylab.imshow(np.multiply(i3[0::5,0::5],4), cmap=None, norm=None, aspect=None, interpolation='nearest', vmin=0, vmax=2048, origin='upper')
    #    imgutil.dispimg(i2,viewfactor=4)
    pylab.title("Dark Row normalization Using " + Method )

#    pylab.subplot(2,2,4)
#    pylab.imshow(np.multiply(i4[0::5,0::5],4), cmap=None, norm=None, aspect=None, interpolation='nearest', vmin=0, vmax=2048, origin='upper')
#    pylab.title('Dr and Col and Row Norm ')


    return i3

def NormalizeColumnGains(imgArray,target=None,PlotAll=None,Plot=1,JustDark=0,Rows=0,Method="Mean"):
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
            imgTstart = 0           # image rows top start
            DRTend = 1080+16        # dark rows top end
            DRBstart = DRTend       # dark rows bottom start            
            imgBend = 2160+32       # image rows bottom start


            imgTop = DarkColNormalize(imgArray[imgTstart:DRTend,:],top=1,Plot=PlotAll,Method=Method)   # No Dark Columns, Just Dark Rows and pic
            print "imgTop shape",imgTop.shape
            imgBottom = DarkColNormalize(imgArray[DRBstart:imgBend,:],Plot=PlotAll,Method=Method)
            print "imgBottom shape",imgBottom.shape

            # Normalize Both Images to the same gain setting
            if target is None: # May want to change this to include all the options
                target=np.mean([np.mean(imgTop),np.mean(imgBottom)])
            topFactor = target/np.mean(imgTop)
            bottomFactor = target/np.mean(imgBottom)

            NormImg = np.append(imgTop*topFactor,imgBottom*bottomFactor,axis=0)

            # Return just the dark or both?
            if not JustDark:
                NormImg = NormalizeColumnGains(NormImg,target=target)
#                if Rows:
#                    NormImg = NormalizeColumnGains(NormImg,target=target,Rows=Rows)


        else:
            if JustDark:
                print "You ToolBag! You are trying to normalize the dark columns of an image with no dark columns!!!"
                print "flatfield.NormalizeColumnGains   expects a dark column image of size   [2192,2592]"
                print "Image size passed is:   [%s]" % imgArray.shape
            NormImg = ImgColNormalize(imgArray)


        if Plot:
            PlotComparison(imgArray,NormImg,title="Full Image Gain Normalization")
        return NormImg

    else:
        raise RuntimeError('numpy ndarray input required. Try using loadimg() first.')


def DarkColNormalize(imgArray,top=0,target=None,Plot=None,Method="Mean"):
    """
        Purpose: Normalize image array based on dark columns.

        Inputs: imgArray -numpy array- image array
                top      -bool {optional}- Indicates if this is a "top" oriented image array. For top sensor half,
                          dark rows come after the information image array. Otherwise, this assumes the dark rows
                          come first.
    """
    rows,cols = imgArray.shape
    print "rows",rows,"cols",cols
    
    if top == 0:
        darkrows = imgArray[0:16,:]
    else:
        darkrows = imgArray[rows-16:rows,:]

    # Get target normalization (which is median of the top or bottom half including dark rows))
    if target is None:
        target = centroid.frobomad(imgArray)[0]
#        target = np.mean(imgArray)

    # Get normalization factor
    norm_factor=FindNormFactor(target,darkrows,Method=Method)
#    norm_factor = []
#    for col in range(0,cols):
##        norm_factor.append(target/centroid.frobomad(darkrows[:,col])[0])
#        norm_factor.append(target/np.mean(darkrows[:,col]))

    # Apply Normalization Factor
    new_imgArray = imgArray*norm_factor

    if Plot:
        if top:
            PlotComparison(imgArray,new_imgArray,title="Top Sensor Half")
        else:
            PlotComparison(imgArray,new_imgArray,title="Bottom Sensor Half")


    # Cut off dark rows and columns and return
    if top:
#        final_image = new_imgArray[0:rows-16,16:cols-16]
        final_image = imgArray[0:1080][:,16:2560+16]
    else:
#        final_image = new_imgArray[15:rows-1,16:cols-16]
        final_image = imgArray[16:1080+16][:,16:2560+16]
    return final_image


def ImgColNormalize(imgArray,target=None, Rows=0,Method="mean"):
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
        target = centroid.frobomad(imgArray)[0]
#        target = np.mean(imgArray)

    # Get normalization factor
    norm_factor=FindNormFactor(target,imgArray,Method=Method)
#        norm_factor = []
#    if Rows:
#        for row in range(0,rows):
#            norm_factor.append(target/centroid.frobomad(imgArray[row,:])[0])
#            norm_factor.append(target/np.mean(imgArray[row,:]))

#    else:
#        for col in range(0,cols):
#            norm_factor.append(target/centroid.frobomad(imgArray[:,col])[0])
#            norm_factor.append(target/np.mean(imgArray[:,col]))


    # Apply Normalization Factor
    new_imgArray = imgArray*norm_factor

    return new_imgArray


def FindNormFactor(target,imgArray,Method="Mean",Scalar=False):
    """
        Purpose: Find the normilization vector to apply to the image
    """

    rows,cols = imgArray.shape
    norm_factor = []
    for col in range(0,cols):
        if Method.lower() == "mean":
            norm_factor.append(target/np.mean(imgArray[:,col]))
        elif Method.lower() == "median":
            norm_factor.append(target/np.median(imgArray[:,col]))
        elif Method.lower() == "mode":
            norm_factor.append(target/mode(imgArray[:,col])[0])
        elif Method.lower() == "robustmean":
            norm_factor.append(target/centroid.frobomad(imgArray[:,col])[0])
        elif Method.lower() == "gangbang":
            norm_factor.append(target/np.mean([np.median(imgArray[:,col]),centroid.frobomad(imgArray[:,col])[0],np.mean(imgArray[:,col]),mode(imgArray[:,col])[0]]))
        else: # Use Kevin's Frobomad
            print "Invalid normalization method input. Please try using"
            print "mean"
            print "median"
            print "mode"
            print "robustmean"
            print "gangbang"
            print "Just using the Robust Mean By Default"
            norm_factor.append(target/centroid.frobomad(imgArray[:,col])[0])
    return norm_factor


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
        oldmed.append(centroid.frobomad(old_img[:,col])[0])
        newmed.append(centroid.frobomad(new_img[:,col])[0])

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
    pylab.legend(['Before Normalization Rmean','After Normalization Rmean'])
    pylab.xlabel('Column')
    pylab.ylabel('Robust Mean')

    #fourrier signal
    pylab.subplot(2,2,2)
    pylab.hist(old_img[randrow,randcol],bins=75)
    pylab.xlabel('Hist')
    pylab.ylabel('Old Rand Selection Intensity')

    pylab.subplot(2,2,4)
    pylab.hist(new_img[randrow,randcol],bins=75)
    pylab.xlabel('Hist')
    pylab.ylabel('New Rand Selection Intensity')



#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#
#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^
# Jeds section




# Jeds section
#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#
#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#^#
