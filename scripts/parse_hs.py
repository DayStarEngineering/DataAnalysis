#
# Script name: parse_hs.py
# Author: Kevin Dinkel
# Created: 10/9/2012
# Description: This script parses a h&s file
#

###################################################################################
# Must import this for every script in this directory in order to use our modules!!
###################################################################################
import script_setup

###################################################################################
# Import modules from analysis (the correct way to do it):
###################################################################################
from util import hsutil as hs
from pylab import *

###################################################################################
# Main
###################################################################################
HS = hs.load('/home/kevin/Desktop/health/')

# Plot some useful things:
hs.plotme(HS,30)
