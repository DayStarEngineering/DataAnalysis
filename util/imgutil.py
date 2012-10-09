# Jed Diller
# 10/5/12
# Image utilities to load, display, save images

import Image
import numpy
from struct import *

# ------------------------------- Load Image ---------------------------------
# loadimg(): loads a tiff, dat, or array into memory
# returns 2D list of 16 bit integers
def loadimg(picIn):    

    # Is it a picture or list?
    # It's a picture
    if type(picIn) is str:

        # Is it a tif or a dat?
        imgtype = filetype(picIn)
        #print imgtype
        # TIF file type
        if (imgtype == 'tif'):   
            picOut = tif2list(picIn)            
            return picOut
        # Dat file type    
        elif (imgtype == 'dat'):
            picOut = readDat(picIn)
            return picOut
        # TIFF file type, read is a RGB, can't find fix yet
        elif (imgtype == 'tiff'):
            raise RuntimeError('Compressed RGB TIFF format not supported by loadimg().')
        # Uknown type    
        else:
            raise RuntimeError('Unsupported image file type for loadimg().')

    # It's a list
    elif type(picIn) is list:
        picOut = picIn
        return picOut        
    else:
        raise RuntimeError('Variable type not supported by loadimg().')


# ----- loadimg() supporting functions ---------

# check image file type
def filetype(file):
    return file.split(".")[-1]

# tif2list():convert PixelArray of loaded Image to a list 
def tif2list(picIn):
    tif = Image.open(picIn)
    numCols = tif.size[0] #cols, x
    numRows = tif.size[1] #rows, y
    pixels = tif.load()
    listImg = []
    for row in range(0,numRows):
        listImg.append([])
        for col in range(0,numCols):
            listImg[row].append(pixels[col,row])
    return listImg

# readDat(): reads dat file as stream of 16 bit unsigned integers
# assumes 2592*2192*2 bytes in dat file
# scales to 16 bits values for displaying purposes
def readDat(filename):
    numRows = 2192
    numCols = 2592
    bytenum = 2
    totalBytes = 11363328 # 2592*2192*2 16 bit ints
    scaling = 32 # 2^16/2^11
    endian = '@H'
    image = []

    # find number of bytes in file
    f = open(filename,"rb")
    bytesInFile = len(f.read())
    f.close()

    if bytesInFile == totalBytes:
        f = open(filename, 'rb')
        for row in range(0,numRows):
            image.append([])
            for col in range(0,numCols):
                value = unpack(endian,f.read(bytenum))[0]*scaling
                image[row].append(value)
        f.close()
        return image
    else:
        raise RuntimeError('Not a DayStar dat file. Not a 2592x2192 image.')
        
# -----------------------------Display Image-------------------------------------
# dispimg()
# displays image loaded with loadimg()
# diplays tiff, dat, or array
# not sure if worth it with so many platforms


# ----------------------------- Save Image --------------------------------------
# saveimg(): saves list image to given path, filename as a TIF
# filename must end with '.tif'
def saveimg(listIn, outfile):
    if type(listIn) is list:
        tifImage = list2tif(listIn)
        tifImage.save(outfile,'tiff')
    else:
        raise RuntimeError('Not a list for arg 2 of saveimg(filename,listin).')

# --------saveimg() supporting functions---------
# list2tif() returns an Image with a PixelArray equivalent of the given list
def list2tif(listIn):
    
    if type(listIn) is list:
        numRows = len(listIn) 
        numCols = len(listIn[0])
        
        if numRows == 2192 and numCols == 2592:
            mode = 'I;16'
            size = [numCols, numRows]
            tif = Image.new(mode,size)
            tifpix = tif.load()
            
            for row in range(0,numRows):
                for col in range(0,numCols):
                    tifpix[col,row] = int(listIn[row][col])
            return tif
        else:
            raise RuntimeError('List is not 2592x2192.')
        
    else:
        raise RuntimeError('Argument is not a list.')        


        
