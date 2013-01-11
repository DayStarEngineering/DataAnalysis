__author__ = 'zachdischner'


from db import RawData as database
from analysis import flatfield
from util import imgutil as imgutil
import os
import numpy as np
import pylab as pl

def main():

    print 'Loading filenames from database.'
    db = database.Connect()
    fnames = db.select('select raw_fn from rawdata WHERE(gain=1)').raw_fn.tolist()

    n = len(fnames)

    for count,fname in enumerate(fnames):
        print "Normalizng " + fname + " image # %s of %s" % (count,n)
        # Load the image:
        image = imgutil.loadimg(fname,from_database=True)

        # Normalize up image:
        image = flatfield.ImgNormalize(image, Method="mean")

        print "Saving normalized image as " + str.replace(fname,'.dat','_norm.tif')
        # Save the image with _norm.tif appended
        imgutil.saveimg(image,os.environ.get('RawBaseLoc') + str.replace(fname,'.dat','_norm.tif'))

