__author__ = 'zachdischner'


import numpy as np
import transformations as transform
import scipy as sp
from scipy import signal
import matplotlib
#from pylab import plot, show, title, xlabel, ylabel, subplot,figure
import pylab as pylab
import sys

# Simple routine to test the effectiveness of the highpass filter
def test_highpass():
    signal=noisy_sin()
    signal2=high_pass(signal,plot=1)
    pylab.title('Brick Wall Filtering')
    nil=high_pass(signal,plot=1,lfilt=1)
    pylab.title('SciPy "lfilt" filtering. Just guesswork')
    return signal, signal2

# Return list of arrays of quaternions. Taken from spring semester processing attempts
def sample_quats():
    tmp=np.loadtxt(open("./analysis/quats.csv","rb"),delimiter=",",skiprows=0)
    quats=[]
    for ii in range(tmp.size/4-1):
        quats.append([tmp[0][ii],tmp[1][ii],tmp[2][ii],tmp[3][ii]])
    return quats

def noisy_sin():
    xs=np.arange(1,100,.05)     #generate Xs (0.00,0.01,0.02,0.03,...,100.0)
    signal=np.sin(xs)
    signal2=np.sin(xs*.2)
    noise= (np.random.random_sample((len(xs))))

    return signal + signal2 + noise




# Convert a list of arrays of quaternions to arrays of corresponding roll, pitch, and yaw values.
def quat_to_roll_pitch_yaw(quaternions):
    roll=[]
    pitch=[]
    yaw=[]
    for q in quaternions:
        RPY=transform.euler_from_quaternion(q, axes='sxyz')   # They expect the 'sxyz'
        roll.append(RPY[0])
        pitch.append(RPY[1])
        yaw.append(RPY[2])
    return roll,pitch,yaw




# Get rid of low frequency occurances in 'rotations'. Single array of rotations.
# For now, just get rid anything below 10 Hz

# Returns inverse raw series with the low frequencies filtered out
# lfilt - experimenting with scipy.signal.lfilt method
def high_pass(series,cutoff=100,sampling_frequency=1,plot=None,lfilt=None):
    # Filter the Power?
    power = power_spectrum(series,sampling_frequency=sampling_frequency)
    power_filt = power.copy()

    if lfilt is None:
        for ii in range(0, len(power)):
            if ii <cutoff:
                power_filt[ii] = 0.0
                power_filt[len(power) - ii -1] = 0.0
    else:  # Doesn't really work
        power_filt=signal.lfilter([0,0,0,.5,1,1,1,1,1,1,1,1,1,1,.5,0,0,0],[1],power)

    # Inverse fourrier. Get new filtered signal back
    new_series = np.fft.irfft(power_filt)

    if plot is not None:
        pylab.figure(num=None, figsize=(13, 7), dpi=80, facecolor='w', edgecolor='k')
        # Signal
        pylab.subplot(2,2,1)
        pylab.plot(series)
        pylab.xlabel('Time')
        pylab.ylabel('Signal')

        pylab.subplot(2,2,3)
        pylab.plot(new_series)
        pylab.xlabel('Time')
        pylab.ylabel('Filtered Signal')

        #fourrier signal
        pylab.subplot(2,2,2)
        pylab.plot(power)
        pylab.xlabel('Freq (Hz)')
        pylab.ylabel('Original Power')

        pylab.subplot(2,2,4)
        pylab.plot(power_filt)
        pylab.xlabel('Freq (Hz)')
        pylab.ylabel('Filtered Power')


    return np.fft.ifft(power)






# Compute power spectrum of a series.
def power_spectrum(series,sampling_frequency=1):
    # Get sampling frequency
    Fs = 1/sampling_frequency

    freq=np.fft.rfft(series)
    power=freq*np.conj(freq)
#    power=power[range(len(power)/2)]
    return power



#Plot a series' power spectrum. Do something like:
#In [95]: tracking.plot_power(sin(th))
#
#In [96]: tracking.plot_power(sin(10*th))
#
#In [97]: tracking.plot_power(sin(50*th))
# where 'th' is an array
def plot_power(series,sampling_frequency=1):
    t=sp.arange(0,len(series))/(1.0*sampling_frequency)
    pylab.subplot(2,1,1)
    pylab.plot(t,series)
    pylab.xlabel('Time')
    pylab.ylabel('Amplitude')
    pylab.subplot(2,1,2)

    power=power_spectrum(series)
    pylab.plot(power)
    pylab.xlabel('Freq (Hz)')
    pylab.ylabel('Power')



# I think LESS USEFUL than the above, "plot_power"
def plot_freq(series,sampling_frequency=1):
    t=sp.arange(0,len(series))/(1.0*sampling_frequency)
    pylab.subplot(2,1,1)
    pylab.plot(t,series)
    pylab.xlabel('Time')
    pylab.ylabel('Amplitude')
    pylab.subplot(2,1,2)

    n = len(series)             # length of the signal
    k = sp.arange(n)
    T = n/sampling_frequency
    frq = k/T                   # two sides frequency range
    frq = frq[range(n/2)]       # one side frequency range

    Y = np.fft.fft(series)/n    # fft computing and normalization
    Y = Y[range(n/2)]

    pylab.plot(frq,abs(Y),'r') # plotting the spectrum
    pylab.xlabel('Freq (Hz)')
    pylab.ylabel('|Y(freq)|')
    pylab.show()







