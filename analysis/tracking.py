__author__ = 'zachdischner'
"""
    Purpose: This file includes methods for analyzing sequences of star rotations. Includes utils for
             *  Frequency transformation
             *  Rotation sequence transformation
             *  High pass frequency filtering
             *  Time and frequency based plotting
             *  Variance calculations from rotation sets
"""




import numpy as np
import transformations as transform
import scipy as sp
from scipy import signal
import matplotlib
import pylab as pylab
import math
import sys



def FindVariance(quaternions,delta_t=0.1,motion_frequency=2,plot=None,order="xyzs"):
    """
        Purpose: Find the variance of a set of quaternions. Low Frequency components are assumed to be invalid
                 and will be discarded. Intended for analyzing high-frequency variations in a set of rotation
                 quaternions, specifically for the DayStar platform.
        Inputs: quaternions - List of quaternion arrays, formatted 'SXYZ' I think.
                delta_t - (optional) Time between quaternion observations [s]. Assumed (and must be) uniform for all frames
                motion_frequency - (optional) The frequency of motion that we wish to filter out.
                plot - (optional) Set to generate plots of the fourrier filterig as we do it, to see how the signal
                       changes
                variable -(optional), the name of the signal being filtered. Used for plot labeling.
        Outputs: var - The computed variance of all observations. Meant to be some indication of DayStar performance
    """
    # Hey, do this later smarter
    if order == "xyzs":
        quats=[]
        for ii in range(quaternions.size/4-1):
            quats.append([quaternions[3][ii],quaternions[1][ii],quaternions[2][ii],quaternions[0][ii]])
        quaternions=quats

    [r,p,y]=quat2rpy(quaternions)
    r_filt = high_pass(r,cutoff=motion_frequency,delta=delta_t,plot=plot,variable='roll')     #radians
    p_filt = high_pass(p,cutoff=motion_frequency,delta=delta_t,plot=plot,variable='pitch')     #radians
    y_filt = high_pass(y,cutoff=motion_frequency,delta=delta_t,plot=plot,variable='yaw')     #radians

    obs_std = np.sqrt(np.std(r_filt)**2 + np.std(p_filt)**2 + np.std(y_filt)**2)    #Standard deviation

    var = 3600*(obs_std*180/math.pi)**2         # arcseconds

    return var


def high_pass(series,cutoff=100,delta=1,plot=None,lfilt=None,variable='signal'):
    """
        Purpose: High-pass filter a single array series using fourrier transforms.

        Inputs: {series} -an array of observations to filter (i.e) lots of angle measurements
                {cutoff} -(optional) Specify cutoff frequency [HZ]
                {delta}  -(optional) time between observations [s]
                {plot}   -(optional) Plot the results of this op in an awesome way
                {lfilt}  -(optional) Try a Scipy.signal.lfilt filter. Just experimental for now

        Outputs:{new_series} -the new series, with low frequency changes filtered out
    """
    #    power = power_spectrum(series,sampling_frequency=sampling_frequency)
    ns =len(series)     # number of samples

    cutoff_freq=cutoff*(ns*delta)   # Index of cutoff frequency in this new awesome frequency domain
    #    cutoff_freq=100

    fft_series = np.fft.rfft(series)
    fft_filt = fft_series.copy()


    if lfilt is None:

        for ii in range(0, len(fft_filt)):
            if ii <cutoff_freq:
                fft_filt[ii] = 0.0
            #                fft_filt[len(fft_filt) - ii -1] = 0.0
    else:  # Doesn't really work
        fft_filt=signal.lfilter([0,0,0,.5,1,1,1,1,1,1,1,1,1,],[1],fft_series)

    # Inverse fourrier. Get new filtered signal back
    new_series = np.fft.irfft(fft_filt)

    if plot is not None:
        pylab.figure(num=None, figsize=(13, 7), dpi=80, facecolor='w', edgecolor='k')
        # Signal
        pylab.subplot(2,2,1)
        pylab.plot(np.arange(0,ns*delta,delta),series)
#        pylab.plot(series)
        pylab.xlabel('Time')
        pylab.ylabel(variable)

        pylab.subplot(2,2,3)
#        pylab.plot(new_series)
        pylab.plot(np.arange(0,ns*delta,delta),new_series)
        pylab.xlabel('Time')
        pylab.ylabel('Filtered ' + variable)

        #fourrier signal
        pylab.subplot(2,2,2)
        pylab.plot(fft_series)
        pylab.xlabel('Freq (Hz)')
        pylab.ylabel('Original Power')

        pylab.subplot(2,2,4)
        pylab.plot(fft_filt)
        pylab.xlabel('Freq (Hz)')
        pylab.ylabel('Filtered Power')

    return new_series






def optimize_variance(quats,delta_t=0.01):
    """
    Purpose: Very basic attempt to find best motion frequency to get the best variance for a single series observations
    """
    ns = len(quats)
    # Max cutoff leaves at least half of the spectrum
    cutoff_freq=ns/2
    cutoff2=cutoff_freq/(ns*delta_t)

    motion_freq=np.arange(0,cutoff2,1)
    var=[]
    for ii in np.arange(0,4,.1):
        var.append(FindVariance(quats,motion_frequency=ii,delta_t=0.01))

    pylab.figure()
    pylab.plot(var)
    return var


# Simple routine to test the effectiveness of the highpass filter
def test_highpass():
    """ Simple routine to test the highpass filtering scheme.
        Just call, and it will perform all testing.
    """
    signal=noisy_sin()
    signal2=high_pass(signal,cutoff=2,delta=.05,plot=1,variable='roll [rad]')
    pylab.title('Brick Wall Filtering')
    nil=high_pass(signal,delta=.05,plot=1,lfilt=1)
    pylab.title('SciPy "lfilt" filtering. Just guesswork')
    return signal, signal2


def sample_quats():
    """
        Purpose: Load a list of sample quaternions. Quaternions come from spring semester ground testing with
                 Andor camera.
        Inputs: None
        Outputs: quats-a list of quaternion arrays
    """
    tmp=np.loadtxt(open("./analysis/quats.csv","rb"),delimiter=",",skiprows=0)
    quats=[]
    for ii in range(tmp.size/4-1):
        quats.append([tmp[3][ii],tmp[1][ii],tmp[2][ii],tmp[0][ii]])
    return quats



def noisy_sin():
    """
        Purpose: Load a sample noisy sin data set
        Inputs: None
        Outputs: signal-a noisy, overlaid sin computation array
    """
    xs=np.arange(1,100,.05)     #generate Xs (0.00,0.01,0.02,0.03,...,100.0)
    signal=np.sin(xs)
    signal2=np.sin(xs*.2)
    noise= (np.random.random_sample((len(xs))))

    return (signal + signal2 + noise)



# Convert a list of arrays of quaternions to arrays of corresponding roll, pitch, and yaw values.
def quat2rpy(quaternions):
    """
        Purpose: Convert a list of arrays of quaternions to Euler angles (roll,pitch,yaw)
        Inputs: quaternions - list of quaternion arrays. In the form of 'SXYZ' I THINK?!?!?
        Outputs: r,p,y - separate roll, pitch, and yaw vectors
        Can test with:
            >>>quats=tfdat /= abs(fdat).max()racking.sample_quats()
            >>>[r,p,y]=tracking.quat2rpy(quats)
    """
    roll=[]
    pitch=[]
    yaw=[]
    for q in quaternions:
        RPY=transform.euler_from_quaternion(q, axes='sxyz')   # They expect the 'sxyz'
        roll.append(RPY[0])
        pitch.append(RPY[1])
        yaw.append(RPY[2])
    return roll,pitch,yaw





def power_spectrum(series,sampling_frequency=1):
    """
        Purpose: Compute power spectrum of a data series
        Inputs: series-An array of data to compute the power spectrum for
                sampling_frequency-(optional) IDK what for yet
        Outputs: power-the computed power spectrum
    """
    # Get sampling frequency
    Fs = 1/sampling_frequency

    freq=np.fft.rfft(series)
    power=freq*np.conj(freq)
    power=power[range(len(power)/2)]
    power /= abs(power).max()        #Normalize to 1
    return power



#Plot a series' power spectrum. Do something like:
#In [95]: tracking.plot_power(sin(th))
#
#In [96]: tracking.plot_power(sin(10*th))
#
#In [97]: tracking.plot_power(sin(50*th))
# where 'th' is an array
def plot_power(series,sampling_frequency=1):
    """
        Purpose: Illustrate the power spectrum calculation for a given data series
        Inputs: series-A data array to show the power spectrum for. Calls power_spectrum
                sampling_frequency-(optional) IDK what for yet
        Outputs: none
    """
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
    """
        Purpose: Illustrate the power spectrum calculation for a given data series
        Inputs: series-A data array to show the power spectrum for. Calls power_spectrum
                sampling_frequency-(optional) IDK what for yet
        Outputs: none
    """
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







