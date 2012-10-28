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
import time

# Globals



# -----------------
# --- FUNCTIONS ---
# -----------------

def newton(Vi, Vb):
    
    return 0    
    
# -------------------------------------------------------------------------------
def qmethod(Vi, Vb, W=None):
    '''
    This method analytically solves for the least-squares fit quaternion
    relating the set of inertial and body vectors Vi and Vb. W is a vector
    of weights, and by default is all ones. 
    
    The body vectors Vi and Vb must be of size Nx3, where N is the number of
    vectors. 2D cases should set the third column to zero. 
    '''

    Vi = array( Vi )
    Vb = array( Vb )
    
    # Calculate components of K    
    S, Z, tr = qmatrices(Vi, Vb, W)
    
    # K Matrix
    K = array( vstack([ hstack( [S - tr*eye(3), Z] ), append(Z.T, tr) ]) )
    
    # Eigenvalues and vectors
    w,v = linalg.eig(K)
    
    # Best fit quaternion
    Q = v[:,argmax(w)]
    
    return Q    
    
# -------------------------------------------------------------------------------
def quest(Vi, Vb, W=None):

    Vi = array( Vi )
    Vb = array( Vb )
    
    # Check weights
    if W is None: 
        W = ones( (Vi.shape[0], 1) )
    elif W.shape != (Vi.shape[0], 1):
        raise RuntimeError('Weight vector must have same length as row in Vb, Vi')
    
    # Optimal eigenvalue
    opt = sum(W)
    
    # Calculate components of K    
    S, Z, tr = qmatrices(Vi, Vb, W)

    # Construct A matrix
    A = eye(3)*(opt + tr) - S
    
    # Solve for p
    p = linalg.solve(A, Z)
    
    # Convert to quaternion
    q = 1/sqrt(1 + sum(p*p)) * append(p, 1)

    return q
    
# -------------------------------------------------------------------------------
def qmatrices(Vi, Vb, W=None):
    '''
    This function takes inertial and body vectors and calculates three parameters
    that are common to the q-method and QUEST method (these are the 3x3 S array, 
    the 3x1 Z vector, and the trace of B, "tr").
    '''

    # Check vector sizes
    if Vi.shape != Vb.shape:
        raise RuntimeError('Must have same number of body and inertial vectors')
    
    row, col = Vi.shape;
    
    # Check weights
    if W is None: 
        W = ones( (row, 1) )
    elif W.shape != (row, 1):
        raise RuntimeError('Weight vector must have same length as row in Vb, Vi')
        
    # Construct B matrix
    B = dot(Vb.T, Vi*tile(W, (1,col)) )
    
    # Components of K matrix
    tr = trace(B)
    S = B + B.T;
    Z = array( [[B[1,2] - B[2,1]], [B[2,0] - B[0,2]], [B[0,1] - B[1,0]]] )

    return S, Z, tr

# -------------------------------------------------------------------------------
def quat2rot(q):
    '''
    Converts a quaternion to a rotation matrix
    '''
    
    # Components of q
    x = q[0];
    y = q[1];
    z = q[2];
    w = q[3];
    
    # Calculate
    r = array( [ [-y**2 - z**2, x*y + w*z   , x*z - w*y   ],
                 [x*y - w*z   , -x**2 - z**2, y*z + w*x   ], 
                 [x*z + w*y   , y*z - w*x   , -x**2 - y**2] ] )
    
    R = eye(3) + 2*r
       
    return R

# ------------
# --- MAIN ---
# ------------

def main():

    # This is the example given in Statistical Attitude Determination
    # http://www.dept.aoe.vt.edu/~cdhall/courses/aoe4140/attde.pdf
    
    # Inertial vectors
    vi1 = array( [ 0.2673, 0.5345, 0.8018] )
    vi2 = array( [-0.3124, 0.9370, 0.1562] )
    
    # Body vectors (measured)
    vb1 = array( [0.7814, 0.3751,  0.4987] )
    vb2 = array( [0.6163, 0.7075, -0.3459] )
    
    # Combined into arrays
    vi = array( vstack( [vi1, vi2] ) )
    vb = array( vstack( [vb1, vb2] ) )
    
    # Quaternion
    q_actual = array( [0.2643, -0.0051, 0.4706, 0.8418] )
    
    t1 = time.time()
    q_calc = qmethod(vi, vb)
    t2 = time.time()
    q_quest = quest(vi, vb)
    t3 = time.time()
    
    R_calc = quat2rot(q_calc)
    R_quest = quat2rot(q_quest)
    
    # Print results
    print q_actual
    print q_calc
    print q_quest
    print ''
    print R_calc
    print ''
    print R_quest
    print ''
    print 'Q Method takes: ' + str( (t2 - t1)*1000)
    print 'QUEST takes: ' + str( (t3 - t2)*1000)
    
    return 0
    
    
# -------------------
# --- Run as Main --- 
# -------------------
if __name__ == "__main__":
	sys.exit(main())
