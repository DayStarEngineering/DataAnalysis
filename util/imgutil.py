# Jed Diller
# 10/5/12
# Image utilities to load, display, save images

import numpy as np
from libtiff import TIFF
import grayconv
from pylab import *

# ------------------------------- Load Image ---------------------------------
# loadimg(): loads a tiff, dat, or array into memory
# returns numpy array of 16 bit integers
def loadimg(filename,arg2=None):    
    '''loadimg(): Loads *.tif and *.dat files and returns them as numpy nmarrays.
    Requires: numpy, libtiff, and pyFITS.
    JD, DayStar, 10/10/12'''
    
    # Is it a picture?
    if type(filename) == str:
        
        imgtype = filetype(filename) # what type of file is it?
        # TIF file type
        if (imgtype == 'tif'):   
            imgout = loadtif(filename)
            return imgout
        
        # Dat file type    
        elif (imgtype == 'dat'):
            if arg2 == None:
                imgout = loaddat(filename)
            else:
                imgout = loadfulldat(filename) 
            return imgout

        elif (imgtype == 'fits'):
            print 'Fits not yet supported.'
        
        # TIFF file type, read is a RGB, can't find fix yet
        elif (imgtype == 'tiff'):
            raise RuntimeError('Compressed RGB TIFF format not supported by loadimg().')

        # Uknown type    
        else:
            raise RuntimeError('Unsupported image file type for loadimg().')
    else:
        raise RuntimeError('Variable type not supported by loadimg().')


# ----- loadimg() supporting functions ---------

# graycode
def gimg2bimg(imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    
    for row in xrange(0,rows):
        for col in xrange(0,cols):    
            imgArray[row][col] = grayconv.g2btable[imgArray[row][col]]
    return imgArray

# check image file type
def filetype(file):
    return file.split(".")[-1]

def loaddat(filename):
    '''loaddat(): Loads the image pixel data from a *.dat file created by DAYSTAR 
    into a numpy array.
    This routine ASSUMES that the row size is 2560 + 32 overscan pixels = 2592.
    It ASSUMES that the number of rows is 2160 + 32 = 2192. It assumed 16 bits
    per pixel. Values are scaled from 11 bit to 16 bit units and converted from 
    uint16 gray code to uint16 binary. A cropped 2160x2560 image is returned.
    JD, DayStar, 10/15/12'''
    fileopen = open(filename, mode='rb') # Open the file in binary read mode.
    
    xdim = 2560 + 32
    ydim = 2160 + 32
    nPix = xdim*ydim
    pixT = 'uint16' # Could be 'uint16' for unsigned shorts.
    
    data = np.fromfile(fileopen, pixT, nPix)# load the data following the header
    data.shape = (ydim, xdim)               # reshape the data stream as a 2-D array
    data = cropimg(data)                    # crop image to 2160x2560
    data = data*32                          # scale 11 bit uints to 16 bit for diplaying
    data = gimg2bimg(data)                  # gray to binary conversion
    fileopen.close
    return data

def loadfulldat(filename):
    '''loaddatfull(): Loads the image pixel data from a *.dat file created by DAYSTAR 
    into a numpy array.
    This routine ASSUMES that the row size is 2560 + 32 overscan pixels = 2592.
    It ASSUMES that the number of rows is 2160 + 32 = 2192. It assumed 16 bits
    per pixel. Values are scaled from 11 bit to 16 bit units and converted from 
    uint16 gray code to uint16 binary. Full 2192x2592 image is returned.
    JD, DayStar, 10/15/12'''
    fileopen = open(filename, mode='rb') # Open the file in binary read mode.
    
    xdim = 2560 + 32
    ydim = 2160 + 32
    nPix = xdim*ydim
    pixT = 'uint16' # Could be 'uint16' for unsigned shorts.
    
    data = np.fromfile(fileopen, pixT, nPix)# load the data following the header
    data.shape = (ydim, xdim)               # reshape the data stream as a 2-D array
    data = data*32                          # scale 11 bit uints to 16 bit for diplaying
    data = gimg2bimg(data)                  # gray to binary conversion
    fileopen.close
    return data


def loadtif(filename):
    '''loadtif(): Loads *.tif file and returns a numpy ndarray. Uses libtiff functions.
    JD, DayStar, 10/10/12'''
    tif = TIFF.open(filename, mode='r')  # open tif file
    data = tif.read_image()             # read in pixel values as numpy ndarray
    TIFF.close(tif)
    return data

def cropimg(imgArray):
    '''croping(): crops the dark rows and cols of a 2592x2192 image and returns the 
    2560x2160 image area'''
    top = imgArray[0:1080][:,16:2560+16]
    bott = imgArray[1080+32:2160+32][:,16:2560+16]
    img = np.vstack([top,bott])
    return img

# -----------------------------Display Image-------------------------------------
def dispimg(imgArray, viewfactor=None):
    '''dispimg(): uses pylab, imshow to display a numpy ndarray. viewfactor multiplies
    the entire image by the viewfactor.'''    
    if type(imgArray) is np.ndarray:
        if viewfactor == None:
            figure()
            gray()
            imshow(imgArray, cmap=None, norm=None, aspect=None,
                        interpolation='nearest', origin='upper')
            colorbar()    
            show()

        elif viewfactor != None and type(viewfactor) == int:
            figure()
            gray()
            imshow(imgArray*viewfactor, cmap=None, norm=None, aspect=None,
                                    interpolation='nearest', origin='upper')
            colorbar()    
            show()
    else:
        raise RuntimeError('dispimg(): input must be type np.ndarray')


# ----------------------------- Save Image --------------------------------------
# saveimg(): saves list image to given path, filename as a TIF
# filename must end with '.tif'
def saveimg(imgArray, outfile):
    '''saveimg(): Save a numpy ndarray image as a .tif or .fits file
    JD, DayStar, 10/10/12'''
    
    if type(imgArray) is np.ndarray:
        if filetype(outfile) == 'tif':
            imgArray = np.rot90(imgArray)   # have to rotate for correct orientation
            tif = TIFF.open(outfile, mode='w')
            tif.write_image(imgArray)
            TIFF.close(tif)
        elif filetype(outfile) == 'fits':
            print 'Fits not yet supported.'
        else:
            raise RuntimeError('saveimg(): output filetype must be .tif or .fits')
    else:
        raise RuntimeError('saveimg(): input must be type np.ndarray')
    








        
