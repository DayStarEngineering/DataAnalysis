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

ROOT = '/media/'
HD = 'daystar/'
IMGPATH = ['data/img', 'data1/img', 'data2/img']

'''
ROOT = '/home/sticky/Daystar/dev/'
HD = 'harddrive/'
IMGPATH = ['data/img', 'data2/img']
'''

DEST = '../db' + '/img_db.csv'

HEADERS = ['Zeros', 'Root', 'Filename', 'Time (s)', 'Time (us)', 'Hour',
           'Time of Day', 'Burst Number', 'Image Number', 'Gain','Exposure (ms)'] 

# -----------------
# --- FUNCTIONS ---
# -----------------

def unix2hour(unixTime):
    ''' Converts a unix timestamp to fractional hour of the day '''
    
    time = datetime.fromtimestamp(unixTime)
    hour = float(time.hour) + float(time.minute)/60 + float(time.second)/3600 + \
           float(time.microsecond)/3600000000
    
    timeofday = str(time.hour) + ':' + str(time.minute) + ':' + str(time.second)
       
    return str(hour), timeofday
 
 
def batch2exptime(batch):
    '''Returns the exposure time (ms) of an image as an int based on its batch number.'''

    # Daytime, batches 0-59, 20,30,40,50 ms exposures
    if batch in range(0, 60): # 0-59
        index = 0
        for i in range(0, 6): # 5 daytime bursts
            if batch in range(0+index,3+index):    # 0-2
                exptime = 20
                return exptime
            elif batch in range(3+index,6+index):  # 3-5
                exptime = 30
                return exptime
            elif batch in range(6+index,9+index):  # 6-8
                exptime = 40
                return exptime
            elif batch in range(9+index,12+index): # 9-11
                exptime = 50
                return exptime
            index = index + 12
                    
    # Twilight, batches 60-143, 20,30,40,50 ms exposures
    elif batch in range(60, 144): #60-143
        index = 60
        for i in range(0,7*3): # 7 daytime bursts x 3 gain settings
            if batch == index + 0:   # 0
                exptime = 20
                return exptime
            elif batch == index + 1: # 1
                exptime = 30
                return exptime
            elif batch == index + 2: # 2
                exptime = 40
                return exptime
            elif batch == index + 3: # 3
                exptime = 50
                return exptime
            index = index + 4

    # Nightime, batches 144-197, 30,50,70ms exposures
    elif batch in range(144, 198): # 144-197
        index = 144
        for i in range(0, 7): # 6 nighttime bursts
            if batch in range(0+index,3+index):    # 0-2
                exptime = 30
                return exptime
            elif batch in range(3+index,6+index):  # 3-5
                exptime = 50
                return exptime
            elif batch in range(6+index,9+index):  # 6-8
                exptime = 70
                return exptime
            index = index + 9
    
    # Not a valid batch number
    else:
        raise RuntimeError('Batch number is out of bounds: 0-197.')
 
 
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
        batch = int(fields[3])
        fields[3] = str(int(fields[3]))
        fields[4] = str(int(fields[4]))
        
        # Calculate time in hours
        unixTime = float(fields[1]) + float(fields[2])/1000000       
        hour, time = unix2hour( unixTime )
        
        # Add filename and time in hours to list
        fields.insert(3, time)
        fields.insert(3, hour) # pushes batch, img number to fields[5], fields[6] 
        
        # Add in exposure time based on batch number
        fields.append(str(batch2exptime(batch))) # gain = fields [7], exptime = fields[8]
        
        # Insert the root directory and column of zeros
        fields.insert(0, imgpath.replace('/img',''))
        fields.insert(0, '0')
        
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
