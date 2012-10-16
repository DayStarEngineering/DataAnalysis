# Jed Diller
# gray conversion
# 10/15/12

import numpy as np

# ------Gray Conversion------
def gentable(g2btable):
    for i in g2btable:
        g2btable[i] = gray2binary(g2btable[i])
    return g2btable


def gray2binary(num):
    
    def int2bin(n):
	    'From positive integer to list of binary bits, msb at index 0'
	    if n:
		    bits = []
		    while n:
			    n,remainder = divmod(n, 2)
			    bits.insert(0, remainder)
		    return bits
	    else: return [0]
     
    def bin2int(bits):
        'From binary bits, msb at index 0 to integer'
        i = 0
        for bit in bits:
	        i = i * 2 + bit
        return i	

    def bin2gray(bits):
	    return bits[:1] + [i ^ ishift for i, ishift in zip(bits[:-1], bits[1:])]
     
    def gray2bin(bits):
	    b = [bits[0]]
	    for nextb in bits[1:]: b.append(b[-1] ^ nextb)
	    return b
    
    return bin2int(gray2bin((int2bin(num))))

# ------ Execute ------
g2btable = np.uint16(np.arange(0,65536))  # ints in 2^16 range = 0,65536
g2btable = gentable(g2btable)

