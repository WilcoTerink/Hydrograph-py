# -*- coding: utf-8 -*-

#-Authorship information-########################################################################################################################
__author__ = 'Wilco Terink'
__copyright__ = 'Wilco Terink'
__version__ = '1.0.0'
__email__ = 'wilco.terink@ecan.govt.nz'
__date__ ='December 2019'
#################################################################################################################################################

import pandas as pd
import numpy as np
from scipy.stats import genextreme

#-some matplotlib libraries
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.ticker import FormatStrFormatter

rcParams.update({'font.size': 9})
colors = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
for i in range(len(colors)):
    r, g, b = colors[i]
    colors[i] = (r / 255., g / 255., b / 255.)

pd.options.display.max_columns = 100



def exceed(x):
    '''
    Calculates exceedance probability and return period for data in Pandas series x.
    '''
    x = np.sort(x)
    ind = np.arange(1,len(x)+1)
    nonexc = ind / (len(ind)+1)
    exc = 1 - nonexc
    T = 1/exc
    return exc, T

def plotPDF(x, gevfit, bins, xLabel, Title, fname=None):
    '''
    Plot the PDF of data x.
    ----------------------------------------------------------
    Input:
        x:        Pandas series
        gevfit:   Tuple with the three fitted GEV parameters
        bins:     Integer indicating number of bins or a numpy array with the bin edges
        xLabel:   Str label to use for x-axis
        Title:    Str chart title
        fname:    (Optional) Full path to filename to save the figure in *.png format
    '''
    fig, ax = plt.subplots(1, 1)
    h = ax.hist(x, bins, density=True, color=[0, 1, 1], edgecolor='k', linewidth=.5, facecolor=colors[0])
    p = ax.plot(x,genextreme.pdf(x, gevfit[0], gevfit[1], gevfit[2]), color='k')
    plt.xlabel(xLabel)
    plt.ylabel('Probability density [-]')
    plt.title(Title)
    if fname:
        plt.savefig(fname, dpi=600.)
    else:
        plt.show()

def plotCDF(x, gevfit, e, xLabel, Title, EventFlow=None, EventT=None, EventLabel=None, fname=None):
    '''
    Plots CDF of data in Pandas Series x.
    -------------------------------------------------------------------------------------------
    Input:
        x:            Pandas series
        gevfit:       Tuple with the three fitted GEV parameters
        e:            Numpy array with exceedance probabilities
        xLabel:       Str label to use for x-axis
        Title:        Str chart title
        EventFlow:    (Optional) Flow of event that needs to be highlighted as a separate marker
        EventT:       (Optional) Return period of flow of event that needs to be highlighted as a separate marker
        EventLabel:   (Optional) Legend label of flow of event that needs to be highlighted as a separate marker
        fname:        (Optional) Full path to filename to save the figure in *.png format
    '''
    
    fig, ax = plt.subplots(1, 1)
    mx = max(x)
    plt.hlines(1, 0, mx+250, colors='k', linestyles='--')
    q = genextreme.cdf(x, gevfit[0], gevfit[1], gevfit[2])
    ax.plot(x,q, color='k', label='Fit')
    ax.scatter(x, 1-e, color=colors[0], label='Recorded data', s=15)
    if EventFlow and EventT and EventLabel:
        ax.scatter(EventFlow, 1-(1/EventT), c='g', s=100, label=EventLabel)
    ax.yaxis.grid()
    plt.xlabel(xLabel)
    plt.ylabel('CDF [-]')
    plt.xlim(0,mx+100)
    plt.ylim(0,1)
    plt.title(Title)
    plt.grid(True, which='both')
    ax.legend(loc='lower right')
    if fname:
        plt.savefig(fname, dpi=600.)
    else:
        plt.show()
        
def plotGEV(x, t, gevinv, Tmax, yLabel, Title, EventFlow=None, EventT=None, EventLabel=None, fname=None):
    '''
    Plots GEV of data x.
    -------------------------------------------------------------------------------------------
    Input:
        x:            Pandas series of maxima
        t:            Exceedance return periods associated with data in x
        gevinv:       Inverse CDF for values associated with return periods up to Tmax
        Tmax:         Maximum return period to consider to fit GEV distribution for
        yLabel:       Str label to use for y-axis
        Title:        Str chart title
        EventFlow:    (Optional) Flow of event that needs to be highlighted as a separate marker
        EventT:       (Optional) Return period of flow of event that needs to be highlighted as a separate marker
        EventLabel:   (Optional) Legend label of flow of event that needs to be highlighted as a separate marker
        fname:        (Optional) Full path to filename to save the figure in *.png format
    '''
    
    T = np.linspace(1, Tmax, 100000)
    
    #-The data and fit 
    fig, ax = plt.subplots(1, 1) #, figsize=(12, 10)
    d = ax.scatter(t, x.values,c='r', label='Data')
    f = ax.plot(T, gevinv,'k-', label='Fit')
    if EventFlow and EventT and EventLabel:
        d1 = ax.scatter(EventT, EventFlow, c='g', s=100,label=EventLabel)
    ax.set_xscale('log')
    ax.grid(True, which='both')
    plt.xlim((min(T),max(T)))
    plt.ylim((0,max(gevinv)))
    plt.xlabel('Return period [year]')
    plt.ylabel(yLabel)
    plt.title(Title)
    ax.xaxis.set_major_formatter(FormatStrFormatter("%d"))
    ax.legend()
    if fname:
        plt.savefig(fname, dpi=600.)
    else:
        plt.show()        


def fitGEV(x, Tmax):
    '''
    Fit a GEV distribution to the data in x. Inverse function values are calculateded for returnperiods up to Tmax.
    ---------------------------------------------------------------------------------------------------------------
    Input:
        x:        Pandas series of maxima
        Tmax:     Maximum return period to consider to fit GEV distribution for
    ---------------------------------------------------------------------------------------------------------------
    Returns:
        gev_fit:    Tuple of GEV fit parameters
        gev_inv:    Inverse of CDF for each T
    '''
    T = np.linspace(1, Tmax, 100000)
    
    probs = 1/T
    #-initial guess of shape parameter
    c = 0
    #-fit GEV and calculate inverse
    gev_fit = genextreme.fit(x,c)
    gev_inv = genextreme.ppf(1-probs, gev_fit[0], gev_fit[1], gev_fit[2])
    return gev_fit, gev_inv
    
