# Jed Diller
# 10/5/12
# Image utilities to load, display, save images

import numpy as np
from libtiff import TIFF

# ------------------------------- Load Image ---------------------------------
# loadimg(): loads a tiff, dat, or array into memory
# returns numpy array of 16 bit integers
def loadimg(filename):    
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
            imgout = loaddat(filename)
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

# check image file type
def filetype(file):
    return file.split(".")[-1]

def loaddat(filename):
    '''loaddat(): Loads the image pixel data from a *.dat file created by DAYSTAR into a numpy array.
    This routine ASSUMES that the row size is 2560 + 32 overscan pixels = 2592.
    It ASSUMES that the number of rows is 2160 + 32 = 2192. It assumed 16 bits
    per pixel.
    EFY, SwRI, 3-JUN-2012
    JD, DayStar, 10/10/12'''
    fileopen = open(filename, mode='rb') # Open the file in binary read mode.
    
    xdim = 2560 + 32
    ydim = 2160 + 32
    nPix = xdim*ydim
    pixT = 'uint16' # Could be 'uint16' for unsigned shorts.
    
    data = np.fromfile(fileopen, pixT, nPix)# load the data following the header
    data.shape = (ydim, xdim)               # reshape the data stream as a 2-D array
    data = np.flipud(data)                  # flip upside down and...
    data = np.rot90(data)                   # rotate for correct orientation
    data = data*32                          # scale 11bits to 16bits for diplaying
    fileopen.close
    return data

def loadtif(filename):
    '''loadtif(): Loads *.tif file and returns a numpy ndarray. Uses libtiff functions.
    Image has to the be flipped and rotated 90 deg to be correctly oriented.
    JD, DayStar, 10/10/12'''
    tif = TIFF.open(filename, mode='r')  # open tif file
    data = tif.read_image()             # read in pixel values as numpy ndarray
    data = np.flipud(data)              # flip upside down and...
    data = np.rot90(data)               # rotate for correct orientation
    TIFF.close(tif)
    return data

# -----------------------------Display Image-------------------------------------
# dispimg()
# displays image loaded with loadimg()
# diplays tiff, dat, or array
# not sure if worth it with so many platforms


# ----------------------------- Save Image --------------------------------------
# saveimg(): saves list image to given path, filename as a TIF
# filename must end with '.tif'
def saveimg(imgArray, outfile):
    '''saveimg(): Save a numpy ndarray image as a .tif or .fits file
    JD, DayStar, 10/10/12'''
    
    if type(imgArray) is np.ndarray:
        if filetype(outfile) == 'tif':
            tif = TIFF.open(outfile, mode='w')
            tif.write_image(imgArray)
            TIFF.close(tif)
        elif filetype(outfile) == 'fits':
            print 'Fits not yet supported.'
        else:
            raise RuntimeError('saveimg(): output filetype must be .tif or .fits')
    else:
        raise RuntimeError('saveimg(): input must be type np.ndarray')
    
        
