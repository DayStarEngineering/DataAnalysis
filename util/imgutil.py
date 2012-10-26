# Jed Diller
# 10/5/12
# Image utilities to load, display, save images

import numpy as np
from libtiff import TIFF
import pylab as pl

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
            print imgtype
            raise RuntimeError('Unsupported image file type for loadimg().')
    else:
        raise RuntimeError('Variable type not supported by loadimg().')


# ----- loadimg() supporting functions ---------

# graycode
def gimg2bimg(imgArray,numbits=11):
    for i in xrange(1,numbits):
        imgArray = np.bitwise_xor(imgArray,np.right_shift(imgArray,i))
    return imgArray

def bimg2gimg(imgArray):
    return np.bitwise_xor(np.right_shift(imgArray,1),imgArray)

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
def dispimg(imgArray, viewfactor=1):
    '''dispimg(): uses pylab, imshow to display a numpy ndarray. viewfactor multiplies
    the entire image by the viewfactor.'''    
    try:
        pl.figure()
        pl.gray()
        pl.imshow(np.multiply(imgArray,viewfactor), cmap=None, norm=None, aspect=None, \
                                interpolation='nearest', vmin=0, vmax=2048, origin='upper')
        pl.colorbar()  
        pl.show()
    except: 
        raise RuntimeError('dispimg(): input must be type np.ndarray and viewfactor must be an int')

# -----------------------------Display Image with Cenroids Cirled ------------------------------
def circstars(imgArray,centlist,radius=None,color=None,viewfactor=1):
    '''circstars(): Displays an image imgArray with circles (with specified radius) overlayed 
    at the positions given in centlist. The standard color is red, 'r'.'''
        
    # check: image numpy ndarray, centlist list of tuples or lists
    if type(imgArray) != np.ndarray:
        raise RuntimeError('circstars(): arg 1 must be type np.ndarray')
    
    if type(centlist[0]) is not tuple and type(centlist[0]) is not list:            
        raise RuntimeError('circstars(): arg 2 must be type list or tuple')
    
    # set defaults 
    if color == None:
        color = 'r'
    if radius == None:
        radius = 10 # default radius
            
    # plot the image 
    pl.figure()
    pl.gray()
    pl.imshow(np.multiply(imgArray,viewfactor), cmap=None, norm=None, aspect=None,
                interpolation='nearest', vmin=0, vmax=2048, origin='upper')
    
    
    # plot circle for each centroid, empty colored circle, positon has to be reversed for plotting 
    for pos in centlist:
        circ = pl.Circle(tuple(pos), radius, ec=color, fill=False)
        pl.gca().add_patch(circ)
    
    # actually display it
    pl.show()


# ----------------------------- Save Image --------------------------------------
# saveimg(): saves list image to given path, filename as a TIF
# filename must end with '.tif'
def saveimg(imgArray, outfile, viewfactor=None):
    '''saveimg(): Save a numpy ndarray image as a .tif or .fits file.
    viewfactor argument is an optional input
    JD, DayStar, 10/10/12'''
    
    if type(imgArray) is np.ndarray:
        if filetype(outfile) == 'tif':
            if viewfactor == None:
                imgArray = np.rot90(imgArray)   # have to rotate for correct orientation
                tif = TIFF.open(outfile, mode='w')
                tif.write_image(imgArray)
                TIFF.close(tif)
            elif viewfactor != None and type(viewfactor) == int:
                imgArray = np.rot90(imgArray)   # have to rotate for correct orientation
                imgArray = imgArray*viewfactor  # multiply image by viewfactor
                tif = TIFF.open(outfile, mode='w')
                tif.write_image(imgArray)
                TIFF.close(tif)
            else:
                 raise RuntimeError('viewfactor must be type int')
            
        elif filetype(outfile) == 'fits':
            print 'Fits not yet supported.'
            
        else:
            raise RuntimeError('saveimg(): output filetype must be .tif or .fits')
    else:
        raise RuntimeError('saveimg(): input must be type np.ndarray')
    
def main():
    # Load stuff:
    import time
    
    # Load the image:
    tic = time.clock()
    image = loadimg('/home/kevin/Desktop/img_1348368011_459492_00146_00000_1.dat')
    toc = time.clock()
    
    print 'Load time: ' + str(toc - tic) + ' s'

    # Display image:
    dispimg(image,1)


if __name__ == "__main__":
    import sys
    sys.exit(main())
    






        
