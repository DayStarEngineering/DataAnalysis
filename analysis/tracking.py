__author__ = 'zachdischner'


import numpy as np
import transformations as transform
import scipy as sp
import matplotlib as plot
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
def high_pass(rotations,time):
    freq=np.fft.fft(rotations)
    power=freq*np.conj(freq)






from numpy import sin, linspace, pi
from pylab import plot, show, title, xlabel, ylabel, subplot
from scipy import fft, arange

def plotSpectrum(y,Fs):
    """
    Plots a Single-Sided Amplitude Spectrum of y(t)
    """
    n = len(y) # length of the signal
    k = arange(n)
    T = n/Fs
    frq = k/T # two sides frequency range
    frq = frq[range(n/2)] # one side frequency range

    Y = fft(y)/n # fft computing and normalization
    Y = Y[range(n/2)]

    plot(frq,abs(Y),'r') # plotting the spectrum
    xlabel('Freq (Hz)')
    ylabel('|Y(freq)|')

Fs = 150.0;  # sampling rate
Ts = 1.0/Fs; # sampling interval
t = arange(0,1,Ts) # time vector

ff = 5;   # frequency of the signal
y = sin(2*pi*ff*t)



subplot(2,1,1)
plot(t,y)
xlabel('Time')
ylabel('Amplitude')
subplot(2,1,2)
plotSpectrum(y,Fs)
show()



