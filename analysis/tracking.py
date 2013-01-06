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
from scipy import signal,polyfit,polyval
from scipy.signal import filter_design as fd
import matplotlib
import pylab as pylab
import math
import sys
import time

def FindVariance(quaternions,delta_t=0.1,motion_frequency=3,plot=False,filt_type='ellip',method='kevin',attitude='azelbore'):
    """
        Purpose: Find the variance of a set of quaternions. Low Frequency components are assumed to be invalid
                 and will be discarded. Intended for analyzing high-frequency variations in a set of rotation
                 quaternions, specifically for the DayStar platform.
        Inputs: quaternions - List of quaternion arrays, formatted 'SXYZ' I think.
                delta_t - (optional) Time between quaternion observations [s]. Assumed (and must be) uniform for all frames
                motion_frequency - (optional) The Frequency we want to filter below
                plot - (optional) Set to generate plots of the fourrier filterig as we do it, to see how the signal
                       changes
                variable -(optional), the name of the signal being filtered. Used for plot labeling.
                {filt_type}  -(optional) Specify filter type. Either:
                    * 'ellip' - try a scipy elliptical filter
                    * 'brick' - try a simple brick wall filter
        Outputs: var - The computed variance of all observations. Meant to be some indication of DayStar performance

        **NOTE**
            MOTION_FREQUENCY KEYWORD MUST BE GREATER THAN 1 FOR ELLIPTICAL FILTER. It is an inverse ratio of the full spectrum
            that we wish to cut off. So a '4' will cutoff (1/4) of the frequency spectrum.
    """
    # Hey, do this later smarter
    quats=[]
    qtmp=quaternions[0]
    for q in quaternions:
        # Get rotation from epoch
        qtmp=transform.quaternion_multiply(qtmp,q)      # Multiply each quaternion by the sum of all previous quaternions
        if method=='kevin':
            quats.append(np.array(np.hstack([qtmp[3],qtmp[0:3]])))
        else:
            quats.append(np.array(np.hstack([qtmp[0:3],qtmp[3]])))

    if attitude == 'azelbore':
        AZ = []
        EL = []
        PHI = []
        x = np.array([1, 0, 0])
        y = np.array([0, 1, 0])
        for q in quats:
            # Find rotation matrix from quaternion:
            M = quat2dcm(q)
            
            # Rotate the x axis
            xhat = np.dot(M,x)
            
            # Rotate the y axis
            yhat = np.dot(M,y)
            
            # Find azimuth and elevation:
            az = np.arctan2(xhat[1],xhat[0])
            el = np.arcsin(xhat[2])
            
            # Find unrotate boresite y-axis:
            yhatp = np.array([-np.sin(az),np.cos(az),0])
            
            # Find the boresight rotation:
            phi = np.arccos(np.dot(yhat,yhatp))
            
            # Store data
            AZ.append(az)
            EL.append(el)
            PHI.append(phi)
            
        y_filt = high_pass(AZ,cutoff=motion_frequency,delta=delta_t,plot=plot,variable='Azimuth',filt_type=filt_type,color='blue')     #radians
        p_filt = high_pass(EL,cutoff=motion_frequency,delta=delta_t,plot=plot,variable='Elevation',filt_type=filt_type,color='purple')     #radians
        r_filt = high_pass(PHI,cutoff=motion_frequency,delta=delta_t,plot=plot,variable='Boresight Rotation',filt_type=filt_type,color='green')     #radians
            
    else:
        [y,p,r]=quat2ypr(quats,method=method)
    
        y_filt = high_pass(y,cutoff=motion_frequency,delta=delta_t,plot=plot,variable='yaw',filt_type=filt_type,color='blue')     #radians
        p_filt = high_pass(p,cutoff=motion_frequency,delta=delta_t,plot=plot,variable='pitch',filt_type=filt_type,color='purple')     #radians
        r_filt = high_pass(r,cutoff=motion_frequency,delta=delta_t,plot=plot,variable='roll',filt_type=filt_type,color='green')     #radians

#    obs_std = np.sqrt(np.std(r_filt)**2 + np.std(p_filt)**2 + np.std(y_filt)**2)    #Standard deviation
    y_std = 3600*(np.std(y_filt)*180/math.pi)
    p_std = 3600*(np.std(p_filt)*180/math.pi)
    r_std = 3600*(np.std(r_filt)*180/math.pi)
    
    y_var = y_std**2
    p_var = p_std**2
    r_var = r_std**2
#    var = 3600*(obs_std*180/math.pi)**2         # arcseconds

    return y_var,p_var,r_var,y_filt,p_filt,r_filt


def high_pass(series,cutoff=100,delta=1,plot=False,filt_type='ellip',variable='signal',color='blue'):
    """
        Purpose: High-pass filter a single array series using fourrier transforms.

        Inputs: {series} -an array of observations to filter (i.e) lots of angle measurements
                {cutoff} -(optional)
                    *if 'brick' Specify cutoff frequency [HZ]
                    *if 'ellip' Specify fraction of frequency spectrum to lose. (cutoff > 1.1)
                {delta}  -(optional) time between observations [s]
                {plot}   -(optional) Plot the results of this op in an awesome way
                {filt_type}  -(optional) Specify filter type. Either:
                        * 'ellip' - try a scipy elliptical filter
                        * 'brick' - try a simple brick wall filter

        Outputs:{new_series} -the new series, with low frequency changes filtered out

        **NOTE**
            "CUTOFF" KEYWORD MUST BE GREATER THAN 1 FOR ELLIPTICAL FILTER. It is an inverse ratio of the full spectrum
            that we wish to cut off. So a '4' will cutoff (1/4) of the frequency spectrum.
    """
    #    power = power_spectrum(series,sampling_frequency=sampling_frequency)

    ## Convert to Frequency Domain
    #---------------------------------------------------------
    series  = np.array(series)          # Convert to Array
    ns      =len(series)                # number of samples
    cutoff_freq=cutoff*(ns*delta)       # Index of cutoff frequency in this new awesome frequency domain
    #---------------------------------------------------------

    ## Construct Frequency Filter
    #---------------------------------------------------------
    Nyquist_freq  = 1/delta/2   # Nyquist frequency. Highest freq we can detect
    Wp = cutoff/Nyquist_freq   # Proportion of Full spectrum to filter
    if Wp > 1:
        print "Hey douche, your cutoff frequency is higher than your Nyquist frequency."
        print "You can't filter this way"
#    Wp = cutoff_freq/(ns/math.pi) #(ns*delta)/cutoff_freq     # Cutoff frequency, normalized to 1
    Ws = Wp-0.1*Wp                  # Stop frequency
    Rp = 0.01                       # passband maximum loss (gpass)
    As = 90                         # stoppand min attenuation (gstop)

    if filt_type.lower() == 'ellip':
        try:
            # Must 'try' this because wrong cutoff can spawn an error really easily
            b,a = fd.iirdesign(Wp, Ws, Rp, As, ftype='ellip')
            new_series = signal.lfilter(b,a,series)
        except:
            print "Something went wrong with the Fourier Filter, possibly the cutoff frequency wrong"
            print "Cutoff freq is : %s" % cutoff_freq
            print "Just doing a dumb brick wall filter"
#            cutoff_freq=(ns/cutoff*delta)
            fft_series = np.fft.rfft(series)
            fft_filt   = np.array(fft_series.copy())
            for ii in range(0, len(fft_filt)):
                if ii == cutoff_freq:
                    fft_filt[ii] = 0.5
                if ii <cutoff_freq:
                    fft_filt[ii] = 0.0
            # Inverse fourrier. Get new filtered signal back
            new_series = np.array(np.fft.irfft(fft_filt))   #                fft_filt[len(fft_filt) - ii -1] = 0.0
    elif filt_type.lower() == 'brick':
        fft_series = np.fft.rfft(series)
        fft_filt   = np.array(fft_series.copy())
        for ii in range(0, len(fft_filt)):
            if ii == cutoff_freq:
                fft_filt[ii] = 0.5
            if ii <cutoff_freq:
                fft_filt[ii] = 0.0
            # Inverse fourrier. Get new filtered signal back
        new_series = np.array(np.fft.irfft(fft_filt))
    else:
        fft_series = np.fft.rfft(series)
        fft_filt   = np.array(fft_series.copy())
        for ii in range(0, len(fft_filt)):
            if ii == cutoff_freq:
                fft_filt[ii] = 0.5
            if ii <cutoff_freq:
                fft_filt[ii] = 0.0
            # Inverse fourrier. Get new filtered signal back
        new_series = np.array(np.fft.irfft(fft_filt))

    # Try a linear regression. See which is better
    (ar,br)=polyfit(np.arange(0,len(series)),series,1)
    lin_series=polyval([ar,br],np.arange(0,len(series))) - series
    res_filt = np.std(new_series)
    res_lin = np.std(lin_series)

    if res_filt > res_lin:
        if variable != 'signal':
            print variable
        print "Frequency filter is way worse than a simple linear one"
        print "Freq filter gives resulting std of : %s " % res_filt
        print "Linear regression gives resulting std of : %s " % res_lin
        new_series = lin_series



    if plot:
        pylab.figure(num=None, figsize=(13, 7), dpi=80, facecolor='w', edgecolor='k')
        # Signal
        pylab.subplot(2,2,1)
        pylab.plot(np.arange(0,len(series)*delta,delta)[0:len(series)],series*180/math.pi*3600,color=color)
#        pylab.plot(series*180/math.pi*3600)
        pylab.xlabel('Time')
        pylab.ylabel(variable + " [arcseconds]")

        pylab.subplot(2,2,3)
#        pylab.plot(new_series*180/math.pi*3600)
        pylab.plot(np.arange(0,len(new_series)*delta,delta)[0:len(new_series)],new_series*180/math.pi*3600,color=color)
        pylab.xlabel('Time')
        pylab.ylabel('Filtered ' + variable + " [arcseconds]")

        #fourrier signal
        pylab.subplot(2,2,2)
#        pylab.plot(np.fft.rfft(series))
        power_axis = np.fft.fftfreq(len(series),0.1)
        power_axis=power_axis[power_axis>0]
        power_axis=np.append(power_axis,1/delta/2)

#        power_axis=sp.fftpack.rfftfreq(len(series),0.1)


        pylab.plot(power_axis, power_spectrum(series,sampling_frequency=1/delta),color=color)
        pylab.xlabel('Freq (Hz)')
        pylab.ylabel('Original Power (log10 Scale)')

        pylab.subplot(2,2,4)
#        pylab.plot(power_axis,np.fft.rfft(new_series))
#        pylab.plot(np.fft.rfft(new_series))
        pylab.plot(power_axis,power_spectrum(new_series,sampling_frequency=1/delta),color=color)
        pylab.xlabel('Freq (Hz)')
        pylab.ylabel('Filtered Power (log10 Scale)')


        # Motion and Correlated Standard Deviation
        moving_width = 16   # Do even numbers
        stdseries=np.zeros(len(series))
        for ii in np.arange(moving_width/2,len(series)-moving_width/2):
            stdseries[ii]=np.std(new_series[ii-moving_width/2:ii+moving_width/2])

        pylab.figure(num=None, figsize=(13, 7), dpi=80, facecolor='w', edgecolor='k')
        pylab.title('Gondola Motion and Corresponding Signal Standard Deviation')
        pylab.subplot(2,1,1)
        pylab.grid()
        pylab.plot(np.arange(0,len(series)*delta,delta)[0:len(series)],series*180/math.pi*3600,color=color)
#        pylab.plot(np.arange(0,len(stdseries)*delta,delta)[0:len(stdseries)],series*180/math.pi*3600 + 10*stdseries*180/math.pi*3600,color='red')
#        pylab.plot(np.arange(0,len(stdseries)*delta,delta)[0:len(stdseries)],series*180/math.pi*3600-10*stdseries*180/math.pi*3600,color='red')
        pylab.xlabel('Time')
        pylab.ylabel(variable + " [arcseconds]")

        pylab.subplot(2,1,2)
        pylab.grid()
        pylab.plot(np.arange(0,len(new_series)*delta,delta)[0:len(new_series)],new_series*180/math.pi*3600,color=color)

        #3 Standard Deviation Envelope
        pylab.plot(np.arange(0,len(stdseries)*delta,delta)[0:len(stdseries)],3*stdseries*180/math.pi*3600,color='red',linewidth=2)
        pylab.plot(np.arange(0,len(stdseries)*delta,delta)[0:len(stdseries)],-3*stdseries*180/math.pi*3600,color='red',linewidth=2)
        pylab.xlabel('Time')
        pylab.ylabel(variable + " Moving STD [arcseconds]")
        pylab.legend(['High Frequency Motion','+3 Sigma','-3 Sigma'])



    return new_series






def optimize_variance(quats,delta_t=0.1):
    """
    Purpose: Very basic attempt to find best motion frequency to get the best variance for a single series observations
    """
    ns = len(quats)
    # Max cutoff leaves at least half of the spectrum
    cutoff_freq=ns/2
    cutoff2=cutoff_freq/(ns*delta_t)

    motion_freq=np.arange(0,5,0.1)
    yv=np.zeros(len(motion_freq))
    pv=np.zeros(len(motion_freq))
    rv=np.zeros(len(motion_freq))
    for ii in np.arange(0,len(motion_freq),1):
        yv[ii],pv[ii],rv[ii],t,tt,ttt=FindVariance(quats,motion_frequency=motion_freq[ii],delta_t=0.1)

    pylab.figure()
    pylab.plot(motion_freq,yv)
    pylab.title('Yaw')
    pylab.ylabel('Yaw Variance')
    pylab.xlabel('Motion Frequency')

    pylab.figure()
    pylab.plot(motion_freq,pv)
    pylab.title('Pitch')
    pylab.ylabel('Pitch Variance')
    pylab.xlabel('Motion Frequency')

    pylab.figure()
    pylab.plot(motion_freq,rv)
    pylab.title('Roll')
    pylab.ylabel('Roll Variance')
    pylab.xlabel('Motion Frequency')
    return yv,pv,rv,motion_freq


# Simple routine to test the effectiveness of the highpass filter
def test_highpass(filt_type='ellip',method='kevin',motion_freq=2):
    """ Simple routine to test the highpass filtering scheme.
        Just call, and it will perform all testing.
    """
    tic = time.clock()
    signal=noisy_sin()
    signal2=high_pass(signal,cutoff=2,delta=.05,plot=1,filt_type=filt_type)
    pylab.title(filt_type + ' Filter Cutoff is 2/.05 Hz')
    nil=high_pass(signal,cutoff=0.1,delta=.05,plot=1,filt_type=filt_type)
    pylab.title(filt_type + ' Filter Cutoff is 0.7/.05 Hz')

    quats = sample_quats()
    y,p,r=FindVariance(quats,plot=True,filt_type=filt_type,method=method,motion_frequency=motion_freq)
    print "Yaw rms = %s " % y
    print "Pitch rms = %s " % p
    print "Roll rms = %s " % r

#    [r,p,y]=quat2rpy(quats)
#    r_filt = high_pass(r,cutoff=1,delta=0.1,plot=1,variable='roll')     #radians
#    p_filt = high_pass(p,cutoff=1,delta=0.1,plot=1,variable='pitch')     #radians
#    y_filt = high_pass(y,cutoff=1,delta=0.1,plot=1,variable='yaw')     #radians
    toc = time.clock()

    print "Filtering with " + filt_type + " filtering took %s seconds" % (toc-tic)
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
        quats.append([tmp[3][ii],tmp[2][ii],tmp[1][ii],tmp[0][ii]])
    return quats



def noisy_sin():
    """
        Purpose: Load a sample noisy sin data set
        Inputs: None
        Outputs: signal-a noisy, overlaid sin computation array
    """
    xs=np.arange(1,100,.05)     #generate Xs (0.00,0.01,0.02,0.03,...,100.0)
#    xs=np.ones(100)*10
    signal=np.sin(xs)
    signal2=np.sin(xs*.2)
    noise= (np.random.random_sample((len(xs))))

    return (signal + signal2 + noise)



# Convert a list of arrays of quaternions to arrays of corresponding roll, pitch, and yaw values.
def quat2ypr(quaternions,method='kevin'):
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
        if method is 'transform':
            YPR=transform.euler_from_quaternion(q, axes='rzyx')   # default is 'sxyz'
        else:
            YPR= quat2euler321(q)
        yaw.append(YPR[0])
        pitch.append(YPR[1])
        roll.append(YPR[2])
    return yaw,pitch,roll

def quat2euler321(q):
    dcm = quat2dcm(q)
    return np.array([math.atan2(dcm[0,1],dcm[0,0]), -math.asin(dcm[0,2]), math.atan2(dcm[1,2],dcm[2,2])])
    
def quat2dcm(q):
    return np.array([[q[0]**2+q[1]**2-q[2]**2-q[3]**2, 2*(q[1]*q[2]+q[0]*q[3]), 2*(q[1]*q[3]-q[0]*q[2])],
                    [2*(q[1]*q[2]-q[0]*q[3]), q[0]**2-q[1]**2+q[2]**2-q[3]**2, 2*(q[2]*q[3]+q[0]*q[1])],
                    [2*(q[1]*q[3]+q[0]*q[2]), 2*(q[2]*q[3]-q[0]*q[1]), q[0]**2-q[1]**2-q[2]**2+q[3]**2]]);

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
#    power=power[range(len(power)/2)]
#    power /= abs(power).max()        #Normalize to 1
    return np.log10(power)



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







