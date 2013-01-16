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
    data = db.select("select id,raw_fn from rawdata where(norm_fn='0') limit 5000")
    fnames=data.raw_fn.tolist()
    ids=data.id.tolist()

    n = len(fnames)



    for count,fname in enumerate(fnames):
        path=os.environ.get('RawBaseLoc')
        dir_path="/".join((path + fname).split("/")[:-1])+"/norm/"

        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

#        norm_fn= str.replace(fname,'.dat','_norm.tif')
        full_path=(path+fname).split('/')
        full_path[-1]=str.replace("norm/"+full_path[-1],'.dat','_norm.tif')
        norm_fn='/'.join(full_path[-3:])
        full_path='/'.join(full_path)
        if not os.path.isfile(full_path):


            print "Normalizng " + fname + " image # %s of %s" % (count,n)
            # Load the image:
            image = imgutil.loadimg(fname,from_database=True,load_full=True)

            # Normalize up image:
            image = flatfield.ImgNormalize(image, Method="mean")

            print "Saving normalized image as " + norm_fn
            # Save the image with _norm.tif appended
            imgutil.saveimg(image,full_path)

            del image # Remove from memory to make go faster?

        print "Adding normalized image to database in 'norm_fn': " + full_path
        query="UPDATE rawdata SET norm_fn='"+ norm_fn + "' WHERE(id="+str(ids[count])+")"
        db.execute_statement(query)

