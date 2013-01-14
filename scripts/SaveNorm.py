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
    data = db.select("select id,raw_fn from rawdata where(norm_fn='0' AND burst_num=172)")
    fnames=data.raw_fn.tolist()
    ids=data.id.tolist()

    n = len(fnames)

    for count,fname in enumerate(fnames):
        path=os.environ.get('RawBaseLoc') + '/norm/'
        norm_fn= str.replace(fname,'.dat','_norm.tif')

        if not os.path.isfile(path+norm_fn):


            print "Normalizng " + fname + " image # %s of %s" % (count,n)
            # Load the image:
            image = imgutil.loadimg(fname,from_database=True,load_full=True)

            # Normalize up image:
            image = flatfield.ImgNormalize(image, Method="mean")

            print "Saving normalized image as " + norm_fn
            # Save the image with _norm.tif appended
            imgutil.saveimg(image,path+norm_fn)

            del image # Remove from memory to make go faster?

        print "Adding normalized image to database in 'norm_fn': " + norm_fn
        query="UPDATE rawdata SET norm_fn='"+ norm_fn + "' WHERE(id="+str(ids[count])+")"
        db.execute_statement(query)

