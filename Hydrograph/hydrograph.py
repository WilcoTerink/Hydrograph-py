# -*- coding: utf-8 -*-

#-Authorship information-########################################################################################################################
__author__ = 'Wilco Terink'
__copyright__ = 'Wilco Terink'
__version__ = '1.0.1'
__email__ = 'wilco.terink@ecan.govt.nz'
__date__ ='December 2019'
#################################################################################################################################################

import pandas as pd
import numpy as np

def sepBaseflow(x, dt, A, k=0.000546, dt_max=None, tp_min=None):
    '''
    Separate a time-series into baseflow and peakflow. Fills missing flow records by interpolation.
    
    -----------------------------------------------------------------------------------------------
    Input:
        x:          Pandas dataframe with Index being a pandas datetime index and 'Date' label. Dataframe should.
                    contain one column for flow data, and should be labeled 'Total runoff [m^3 s^-1]'.
        dt:         Minimum time-step interval (in minutes) for analysing the data. Minute choices are 5, 15, or 60.
        k:          Slope of the dividing line; i.e. slope that defines when peakflow event starts and baseflow separation occurs.
                    Default is 0.000546  m^3 s^-1 km^-2 h^-1 (Hewlett and Hibbert 1967).
        A:          Catchment area in km^2 upstream of point of interest.
        dt_max:     Only interpolate over maximum number of consecutive NaN defined over time period dt_max in hours.
        tp_min:     Minimum duration of runoff peak in hours to be selected as being a peak.
    -----------------------------------------------------------------------------------------------
    Returns:
        df_final:    Pandas dataframe with datetime index and the following columns:
                        dt [hour]:                       Time difference in hours between two records.
                        Total runoff [m^3 s^-1]:         Recorded flow in cumecs for that timestamp.
                        Total runoff interp. [m^3 s^-1]: Interpolated recorded flow in cumecs.
                        Baseflow [m^3 s^-1]:             Calculated baseflow in cumecs for that timestamp.
                        Peakflow [m^3 s^-1]:             Calculated peakflow in cumecs for that timestamp.
                        Peak nr.:                        Peak number in sequence. Each peakflow event (i.e. flow above baseflow curve) is given a unique number
                                                         if it classifies as being a peak after filtering.
                        Peakflow starts:                 Timestamp when peakflow starts (moment when runoff peak exceeds baseflow curve).
                        Peakflow ends:                   Timestamp when peakflow ends (moment when runoff peak itersects again with baseflow curve).
                        Flow volume [m^3]:               Volume of the flow between two time-steps (total volume; i.e. baseflow + peakflow).
                        Max flow [m^3 s^-1]:             Maximum flow of peak flow event.
                        Date max. flow:                  Timestamp of maximum flow of peak flow event.
                        Tp [hour]:                       Time to peak.
    '''

    minDate = x.index.min()
    maxDate = x.index.max()
    #-date range for full period (set it depending on the defined time interval)
    if dt == 5:
        print('Processing using a 5-minute interval...')
        dr = pd.date_range(minDate, maxDate, freq='5T')   #-5-minute interval
    elif dt == 15:
        print('Processing using a 15-minute interval...')
        dr = pd.date_range(minDate, maxDate, freq='15T')  #-15-minute interval
    else:
        print('Processing using a 60-minute interval...')
        dr = pd.date_range(minDate, maxDate, freq='60T')  #-60-minute interval
        
    df_final = pd.DataFrame(dr, columns=['Date']); dr = None
    df_final['Time_diff'] = df_final['Date'].diff()
    df_final['dt [hour]'] = df_final['Time_diff'].dt.seconds / 3600.0
    df_final['dt [hour]'] = df_final['dt [hour]'].fillna(0)
    df_final.drop('Time_diff', axis=1, inplace=True)
    df_final.set_index('Date', inplace=True)
    
    df_final['Total runoff [m^3 s^-1]'] = x; x = None;
    #-only interpolate maximum number of consecutive NaNs. dt_max is in hours, so to calculate nr of timesteps depending on the set time-interval
    if dt_max:
        if dt == 5:
            df_final['Total runoff interp. [m^3 s^-1]'] = df_final['Total runoff [m^3 s^-1]'].interpolate(method='time', limit=dt_max*12)
        elif dt == 15:
            df_final['Total runoff interp. [m^3 s^-1]'] = df_final['Total runoff [m^3 s^-1]'].interpolate(method='time', limit=dt_max*4)
        else:
            df_final['Total runoff interp. [m^3 s^-1]'] = df_final['Total runoff [m^3 s^-1]'].interpolate(method='time', limit=dt_max)
    else:
        df_final['Total runoff interp. [m^3 s^-1]'] = df_final['Total runoff [m^3 s^-1]'].interpolate(method='time')
    df_final['Baseflow [m^3 s^-1]'] = np.nan
    df_final['Peakflow [m^3 s^-1]'] = np.nan
     
    cnt=0
    flag = True   #-flag to define new baseflow threshold
    t=0
    Qthresh = False
    for i in df_final.iterrows():
        dindex = i[0]
        print(dindex)
        Qtot = i[1]['Total runoff interp. [m^3 s^-1]']
        QBase = Qtot
         
        #-For first record, baseflow equals total runoff
        if cnt==0:
            df_final.loc[df_final.index==dindex, 'Baseflow [m^3 s^-1]'] = Qtot
        else:
            #-Total runoff of t-1
            QtotOld = df_final.iloc[cnt-1,2]
            dt = df_final.iloc[cnt,0]

            #-Check whether increase in streamflow between two time-steps is larger than k * dt * A, and thus indicates the start of the rising limb
            if (Qtot > (QtotOld + (k * dt * A))) and flag:
                Qthresh = QtotOld
                flag = False
                t = 0
            #-Linearly calculate baseflow using time difference and threshold
            if Qthresh:
                t+=dt
                QBase = Qthresh + (k * t * A)
            #-Check if recession limb is below the baseflow curve 
            if QBase>Qtot:
                Qthresh = False
                flag = True
            #-Make sure baseflow does not exceed total runoff at any point in time
            QBase = min(QBase, Qtot)
                 
            #-Fill in the final dataframe
            df_final.loc[df_final.index==dindex, 'Baseflow [m^3 s^-1]'] = QBase
         
        cnt+=1
   
    df_final['Baseflow [m^3 s^-1]'] = df_final[['Baseflow [m^3 s^-1]', 'Total runoff [m^3 s^-1]']].min(axis=1)
    #df_final = df_final.astype(np.float)
      
    df_final['Peakflow [m^3 s^-1]'] = df_final['Total runoff interp. [m^3 s^-1]'] - df_final['Baseflow [m^3 s^-1]']

    #-Now filter the peaks and assign peak numbers
    df_final = filterpeaks(df_final, tp_min)

    print('Calculating event values...')
    df_final.reset_index(inplace=True)
    #-Start of peakflow event
    df = df_final[['Date', 'Peak nr.']].groupby('Peak nr.').min()
    df.rename(columns={'Date': 'Peakflow starts'}, inplace=True)
    df.reset_index(inplace=True)
    df_final = pd.merge(df_final, df, how='left', on='Peak nr.')
    #-End of peakflow event
    df = df_final[['Date', 'Peak nr.']].groupby('Peak nr.').max()
    df.rename(columns={'Date': 'Peakflow ends'}, inplace=True)
    df.reset_index(inplace=True)
    df_final = pd.merge(df_final, df, how='left', on='Peak nr.')
    #-Flow volume
    df_final['Flow volume [m^3]'] = df_final['Total runoff interp. [m^3 s^-1]'] * 3600 * df_final['dt [hour]']
    df_final.loc[pd.isna(df_final['Peak nr.']), 'Flow volume [m^3]'] = np.nan
    #-Max flow and time of max flow
    df_final['Max. flow [m^3 s^-1]'] = np.nan
    df_final['Date max. flow'] = np.nan
    df_final['Tp [hour]'] = np.nan
    for i in pd.unique(df_final['Peak nr.']):
        df_short = df_final.loc[df_final['Peak nr.'] ==i, ['Date', 'Total runoff interp. [m^3 s^-1]']]#,'Max. flow [m^3 s^-1]']]
        mflow = df_short['Total runoff interp. [m^3 s^-1]'].max()
        df_short = df_short.loc[df_short['Total runoff interp. [m^3 s^-1]'] == mflow]
        mdate = df_short['Date'].min()
        df_final.loc[df_final['Peak nr.'] ==i, 'Max. flow [m^3 s^-1]'] = mflow
        df_final.loc[df_final['Peak nr.'] ==i, 'Date max. flow'] = mdate
    df_final['Date max. flow'] = pd.to_datetime(df_final['Date max. flow'])
    df_final['Tp [hour]'] = (df_final['Date max. flow'] - df_final['Peakflow starts']).dt.seconds / 3600
    df_final.set_index('Date', inplace=True)

    print('Processing completed successfully.')
     
    return df_final
    

def filterpeaks(x, tp_min):
    '''
    Filters the peaks from the baseflow and assigns a peak nr. to it. Peaks are only
    assigned if they last at least as long as the tp_min threshold.
    
    --------------------------------------------------------------------------------
    Input:
        x:        Pandas dataframe with datetime index with 'Date' label and columns:
                    Peakflow [m^3 s^-1]    Peakflow in cumecs for that timestamp (=Total flow - baseflow).
                    dt [hour]              Time difference in hours between two records.
        tp_min:   Minimum duration of runoff peak in hours to be selected as being a peak.
        
    ---------------------------------------------------------------------------------
    Returns:
        df_final:    Pandas dataframe with datetime index and 'Peak nr.' as added column. Records for which no
                     peakflow nr. has been assigned are set to NaN for the 'Peakflow [m^3 s^-1]' column.
    '''

    print('Filtering peaks...')
    df_final = x.copy(); x = None
    df_final['Peak nr.'] = np.nan
    
    #-counter for nr of records in peak
    pcnt = 0
    oldPeakflow = 0.

    for i in df_final.iterrows():
        print(i[0])
        peakflow = i[1]['Peakflow [m^3 s^-1]']
        if peakflow>0. and oldPeakflow == 0.:
            pcnt+=1
            oldPeakflow = peakflow
        if np.isnan(peakflow):
            df_final.loc[df_final.index==i[0], 'Peak nr.'] = pcnt
            df_final.loc[df_final.index==i[0], 'Peakflow [m^3 s^-1]'] = -99.9
            oldPeakflow = peakflow
        elif peakflow==0.: #-this indicates an old event has ended and then it is time to check for nans in the peakflow
            oldPeakflow = 0.
            j = df_final.loc[(df_final['Peakflow [m^3 s^-1]'] == -99.9) & (df_final['Peak nr.']==pcnt)]
            if len(j)>1:
                df_final.loc[df_final['Peak nr.']==pcnt, ['Peakflow [m^3 s^-1]', 'Peak nr.']] = np.nan
                pcnt = pcnt-1
        else:
            df_final.loc[df_final.index==i[0], 'Peak nr.'] = pcnt
    
    df_final.loc[df_final['Peakflow [m^3 s^-1]'] == -99.9, 'Peakflow [m^3 s^-1]'] = np.nan

    #-Select for minimum number of records to make it classify as a peak
    if tp_min:
        print('Selecting events >= %.2f hours' %tp_min)
        df = df_final[['Peak nr.','dt [hour]']].groupby('Peak nr.').sum()
        df.rename(columns={'dt [hour]': 'Peakflow duration [hour]'}, inplace=True)
        clearPeakIds = df.loc[df['Peakflow duration [hour]']<tp_min]
        clearPeakIds = clearPeakIds.index.tolist()
        df_final.loc[df_final['Peak nr.'].isin(clearPeakIds), 'Peak nr.'] = np.nan
        clearPeakIds = None
    print('Filtering peaks completed.')
    return df_final

def maxFlowVolStats(df):
    '''
    Calculates the annual maximum flow peak (crest) and maximum annual flow volume for each year. The flow volume is calculated for each
    peakflow event. These events can be determined using the 'sepBaseflow' function. The volume for each event is calculated as the area
    under the total flow curve from the start till the end of the event.
    
    ------------------------------------------------------------------------------------------------------------------------------------
    Input:
        df:    Pandas dataframe with datetime index with 'Date' label and columns:
                  Date max. flow:                     Timestamp of maximum flow of peak flow event.
                  Max. flow [m^3 s^-1]:               Maximum crest flow of each identified flow peak.
                  Total runoff interp. [m^3 s^-1]:    Recorded (interpolated) flow in cumecs.
                  dt [hour]:                          Time difference in hours between two records.
                  Flow volume [m^3]:                  Volume of the flow between two time-steps (total volume; i.e. baseflow + peakflow).
                  Peak nr.:                           Assigned peak number to each flow peak.
    ------------------------------------------------------------------------------------------------------------------------------------
    Returns:
        vol_peak_combined:     Pandas dataframe with the following columns:
            Year max flow:                    Year for which the maximum annual peak flow and maximum annual peak flow volume are calculated.
            dt [hour]:                        Duration of the maximum flow peak in hours.
            Max. flow [m^3 s^-1]              Maximum peak flow of the maximum annual peak flow volume event.
            Total runoff interp. [m^3 s^-1]   Maximum prak flow of the maximum annual peak flow event.
            Avg. volume rate [m^3 s^-1]       Average flow rate of the maximum annual peak flow volume event (volume/duration).
            Flow volume [MCM]                 Maximum annual peak flow volume in MCM.
    '''
    df_new = df.copy(); df = None
    
    df_new.reset_index(inplace=True)
    df_new['Year'] = df_new['Date'].dt.year
    df_new['Year max flow'] = pd.to_datetime(df_new['Date max. flow']).dt.year
    #-Maximum peak for each year
    y_max = df_new[['Year', 'Total runoff interp. [m^3 s^-1]']].groupby('Year').max()
    y_max.reset_index(inplace=True)
    
    
    #-Maximum volume of peak per year. Year is chosen to be the point when the crest is maximum
    y_peak_vol = df_new[['dt [hour]', 'Flow volume [m^3]','Peak nr.']].groupby('Peak nr.').sum()
    y_peak_vol.reset_index(inplace=True)
    y_peak_vol = pd.merge(y_peak_vol, df_new[['Peak nr.', 'Year max flow', 'Max. flow [m^3 s^-1]']], how='left', on='Peak nr.')
    y_peak_vol.drop_duplicates(inplace=True)
    y_peak_maxvol = y_peak_vol[['dt [hour]','Year max flow', 'Flow volume [m^3]', 'Max. flow [m^3 s^-1]']].groupby('Year max flow').max()
    y_peak_vol = None;
    y_peak_maxvol.reset_index(inplace=True)
    y_peak_maxvol['Year max flow'] = y_peak_maxvol['Year max flow'].astype(np.int)
    
    #-Merge the maximum annual peak flow (crest flow)
    vol_peak_combined = pd.merge(y_peak_maxvol, y_max, how='left', left_on='Year max flow', right_on='Year')
    vol_peak_combined.drop('Year', axis=1, inplace=True)
    #-Calculate the average flow rate of the volume; volume/(hours*3600)
    vol_peak_combined['Avg. volume rate [m^3 s^-1]'] = vol_peak_combined['Flow volume [m^3]'] / (vol_peak_combined['dt [hour]'] * 3600)
    vol_peak_combined['Flow volume [MCM]'] = vol_peak_combined['Flow volume [m^3]'] / 1000000
    vol_peak_combined.drop('Flow volume [m^3]', axis=1, inplace=True)
    y_peak_maxvol = None; y_max = None

    return vol_peak_combined
