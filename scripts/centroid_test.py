#
# Script name: centroid_test.py
# Author: Kevin Dinkel
# Created: 10/2/2012
# Description: This script centroids some stars.
#

###################################################################################
# Must import this for every script in this directory in order to use our modules!!
###################################################################################
import script_setup

###################################################################################
# Import modules from analysis (the correct way to do it):
###################################################################################
from analysis import centroid as centroid
from util import imgutil as imgutil
import matplotlib.pyplot as plt

###################################################################################
# Main
###################################################################################
image = imgutil.loadimg('/home/kevin/Desktop/img_1348368011_459492_00146_00000_1.dat')
