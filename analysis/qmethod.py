#
# Script name: qmethod.py
# Author: Nick Truesdale
# Created: 10/21/2012
#
# Description: This file contains three methods for statistically 
# solving for attitude using intertial and body vectors. 
#

# -------------------------
# --- IMPORT AND GLOBAL ---
# -------------------------

# Import
import os
import sys
sys.path.append('../')

from numpy import *

# Globals



# -----------------
# --- FUNCTIONS ---
# -----------------

def newton(Vi, Vb):
        
    
    
    
    


def qmethod(Vi, Vb, W=None):
    '''
    This method analytically solves for the least-squares fit quaternion
    relating the set of inertial and body vectors Vi and Vb. W is a vector
    of weights, and by default is all ones.  
    '''
    
    # Check vector sizes
    if Vi.shape != Vb.shape:
        raise RuntimeError('Must have same number of body and inertial vectors')
    
    if W is None: 
        W = ones( (Vb.shape[0], 1) )
        
    
    # Construct K matrix
    B = W*dot(Vb, Vi.T)
    
    
    return Q    
    


def quest():

# ------------
# --- MAIN ---
# ------------

def main():

        
    
    return 0
    
    
# -------------------
# --- Run as Main --- 
# -------------------
if __name__ == "__main__":
	sys.exit(main())
