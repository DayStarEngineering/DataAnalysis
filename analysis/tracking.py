__author__ = 'zachdischner'


import numpy as np
import transformations as transform
import scipy as sp
import matplotlib
from pylab import plot, show, title, xlabel, ylabel, subplot
import sys

# Return list of arrays of quaternions. Taken from spring semester processing attempts
def test():
    tmp=np.loadtxt(open("./analysis/quats.csv","rb"),delimiter=",",skiprows=0)
    quats=[]
    for ii in range(tmp.size/4-1):
        quats.append([tmp[0][ii],tmp[1][ii],tmp[2][ii],tmp[3][ii]])
    return quats

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
def high_pass(series,sampling_frequency=1):
    series*3




# Compute power spectrum of a series. Only HALF of the spectrum. No doubles.
def power_spectrum(series,sampling_frequency=1):
    # Get sampling frequency
    Fs = 1/sampling_frequency

    freq=np.fft.fft(series)
    power=freq*np.conj(freq)
    power=power[range(len(power)/2)]
    return power


#Plot a series' power spectrum. Do something like:
#In [95]: tracking.plot_power(sin(th))
#
#In [96]: tracking.plot_power(sin(10*th))
#
#In [97]: tracking.plot_power(sin(50*th))
def plot_power(series,sampling_frequency=1):
    t=sp.arange(0,len(series))/(1.0*sampling_frequency)
    subplot(2,1,1)
    plot(t,series)
    xlabel('Time')
    ylabel('Amplitude')
    subplot(2,1,2)
    Power=power_spectrum(series)
    plot(Power)
    xlabel('Freq (Hz)')
    ylabel('Power')



# I think LESS USEFUL than the above, "plot_power"
def plot_freq(series,sampling_frequency=1):
    t=sp.arange(0,len(series))/(1.0*sampling_frequency)
    subplot(2,1,1)
    plot(t,series)
    xlabel('Time')
    ylabel('Amplitude')
    subplot(2,1,2)

    n = len(series)             # length of the signal
    k = sp.arange(n)
    T = n/sampling_frequency
    frq = k/T                   # two sides frequency range
    frq = frq[range(n/2)]       # one side frequency range

    Y = np.fft.fft(series)/n    # fft computing and normalization
    Y = Y[range(n/2)]

    plot(frq,abs(Y),'r') # plotting the spectrum
    xlabel('Freq (Hz)')
    ylabel('|Y(freq)|')
    show()







#from numpy import sin, linspace, pi
#from pylab import plot, show, title, xlabel, ylabel, subplot
#from scipy import fft, arange
#
#def plotSpectrum(y,Fs):
#    """
#    Plots a Single-Sided Amplitude Spectrum of y(t)
#    """
#    n = len(y) # length of the signal
#    k = arange(n)
#    T = n/Fs
#    frq = k/T # two sides frequency range
#    frq = frq[range(n/2)] # one side frequency range
#
#    Y = fft(y)/n # fft computing and normalization
#    Y = Y[range(n/2)]
#
#    plot(frq,abs(Y),'r') # plotting the spectrum
#    xlabel('Freq (Hz)')
#    ylabel('|Y(freq)|')
#
#Fs = 150.0;  # sampling rate
#Ts = 1.0/Fs; # sampling interval
#t = arange(0,1,Ts) # time vector
#
#ff = 5;   # frequency of the signal
#y = sin(2*pi*ff*t)
#
#
#
#subplot(2,1,1)
#plot(t,y)
#xlabel('Time')
#ylabel('Amplitude')
#subplot(2,1,2)
#plotSpectrum(y,Fs)
#show()



