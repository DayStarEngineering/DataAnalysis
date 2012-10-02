#
# Script name: example_script.py
# Author: Kevin Dinkel
# Created: 10/2/2012
# Description: This script tells you it is an example script.
#

###################################################################################
# Must import this for every script in this directory in order to use our modules!!
###################################################################################
import script_setup

###################################################################################
# Import modules from analysis (the correct way to do it):
###################################################################################
from analysis import chzphot as chzphot

###################################################################################
# Functions:
###################################################################################
def foo():
    ''' This function prints something to the screen! 
    Run: "help(foo)" in interactive mode to see this help statement print out.
    '''
    print "This is an example script!"

###################################################################################
# Main
###################################################################################
foo()

# Run a function from chzphot:
array = [1,2,3,4,5,6,7,8,9]
m,s = chzphot.MAD(array)
print
print 'Lets use some chzphot!'
print 'array: ' + str(array)
print 'median: ' + str(m) 
print 'median absolute deviation: ' + str(s)
