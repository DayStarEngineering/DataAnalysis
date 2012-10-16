#
# Script name: imgparse.py
# Author: Nick Truesdale
# Created: 10/16/2012
# Description: This will load the image file names from an external harddrive 
# mounted in the /media directory. 
#

# -------------------------
# --- IMPORT AND GLOBAL ---
# -------------------------

# Import
import script_setup
import os
import sys
from datetime import datetime

# Globals
'''
ROOT = '/media/'
HD = 'daystar/'
IMGPATH = ['data/img', 'data1/img', 'data2/img']
'''

ROOT = '/home/sticky/Daystar/dev/'
HD = 'harddrive/'
IMGPATH = ['data/img', 'data2/img']


DEST = '../db' + '/img_db.csv'

HEADERS = ['Filename', 'Time (s)', 'Time (us)', 'Hour',
           'Burst Number', 'Image Number', 'Gain'] 

# -----------------
# --- FUNCTIONS ---
# -----------------

def unix2hour(unixTime):
    ''' Converts a unix timestamp to fractional hour of the day '''
    
    time = datetime.fromtimestamp(unixTime)
    hour = float(time.hour) + float(time.minute)/60 + float(time.second)/3600 + \
           float(time.microsecond)/3600000000
       
    return hour
 
 
def parseDir(root, imgpath):
    ''' Reads all of the file names in the directory and outputs a list of strings, each of
        which contains the values specified in HEADERS
    '''     
    
    # Combine path info
    path = root + imgpath
    
    # Get filenames
    filenames = os.listdir(path)
    
    # Initialize output list
    writeList = []
    
    for name in filenames:
        
        # Initialize file string
        fields = [imgpath + '/' + name]
        
        # Split into components
        name = name.replace('.dat', '')
        name = name.replace('img_', '')
        fields = fields + name.split('_')
        
        # Remove leading zeros from batch and img number
        fields[3] = str(int(fields[3]))
        fields[4] = str(int(fields[4]))
        
        # Calculate time in hours
        unixTime = float(fields[1]) + float(fields[2])/1000000       
        hour = str( unix2hour( unixTime ) )
        
        # Add filename and time in hours to list
        fields.insert(3, hour)
        
        # Convert to single CSV line
        writeList.append(','.join(fields))

    return writeList

# ------------
# --- MAIN ---
# ------------

def main():

    # Initialize write list
    writeList = [','.join(HEADERS)]
    
    for path in IMGPATH:
        writeList += parseDir(ROOT + HD, path)   
    
    # Write to a file
    writeFile = open(DEST, 'w')
    
    for line in writeList:
        writeFile.write(line + '\n')
        
    # Close write file
    writeFile.close()    
    
    
    return 0
    
    
# -------------------
# --- Run as Main --- 
# -------------------
if __name__ == "__main__":
	sys.exit(main())
