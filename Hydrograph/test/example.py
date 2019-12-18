# -*- coding: utf-8 -*-

#-Authorship information-########################################################################################################################
__author__ = 'Wilco Terink'
__copyright__ = 'Wilco Terink'
__version__ = '1.0'
__email__ = 'wilco.terink@ecan.govt.nz'
__date__ ='December 2019'
#################################################################################################################################################

import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'font.size': 10})
colors = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
for i in range(len(colors)):
    r, g, b = colors[i]
    colors[i] = (r / 255., g / 255., b / 255.)

from Hydrograph.hydrograph import sepBaseflow, maxFlowVolStats
from Hydrograph.extreme_analysis import *
import pandas as pd
import numpy as np

pd.options.display.max_columns = 100

###############-PART TO SEPARATE PEAKS FROM BASEFLOW-##########################################################################################

#-Period selection
fm_date = '1-1-1980 00:00:00'
to_date = '13-12-1980 23:15:00'

#-Catchment properties
Area = 1461   #-km2
k = 0.000546  #-m^3 s^-1 km^-2 h^-1

# #-Read the first csv file
# ts_df = pd.read_csv(r'C:\Active\Projects\Rangitata_flood\data\ts_part1_hydrstra.csv', parse_dates=[0], dayfirst=True, skiprows=2)
# ts_df.rename(columns={ts_df.columns[0]: 'Date', ts_df.columns[1]: 'Total runoff [m^3 s^-1]'}, inplace=True)
# ts_df = ts_df.loc[(ts_df.Date>=pd.Timestamp(fm_date)) & (ts_df.Date<=pd.Timestamp(to_date))]
# #-Read the second csv file
# ts_df1 = pd.read_csv(r'C:\Active\Projects\Rangitata_flood\data\ts_part2_hydrotel.csv', parse_dates=[[1,2]], dayfirst=True)
# ts_df1.drop(['Ident', 'Quality'], axis=1, inplace=True)
# ts_df1.rename(columns={ts_df1.columns[0]: 'Date', ts_df1.columns[1]: 'Total runoff [m^3 s^-1]'}, inplace=True)
# ts_df1 = ts_df1.loc[(ts_df1.Date>=pd.Timestamp(fm_date)) & (ts_df1.Date<=pd.Timestamp(to_date))]
#   
# #-combine to dateframes into 1
# df = pd.concat([ts_df, ts_df1], axis=0); ts_df = None; ts_df1 = None;
# df.drop_duplicates(subset='Date', inplace=True)
# df.set_index('Date', inplace=True)
#  
#  
# #-Separate baseflow and peakflow and assign peak numbers 
# df = sepBaseflow(df, 15, Area, k, dt_max=12, tp_min=6)
# df.to_csv(r'C:\Active\Projects\Rangitata_flood\data\test.csv')
df = pd.read_csv(r'C:\Active\Projects\Rangitata_flood\data\Rangitata_Klondyke_Peaks.csv',parse_dates=[0], index_col=0, dayfirst=True)

# #-Plot recorded flow and interpolated recorded flow  
# fig, ax = plt.subplots()
# lines = plt.plot(df.index, df['Total runoff [m^3 s^-1]'], df.index, df['Total runoff interp. [m^3 s^-1]'])
# plt.xlabel('Date')
# plt.ylabel('Streamflow [m$^3$ s$^{-1}$]')
# plt.grid(True)
# plt.title('Rangitata at Klondyke') 
# plt.legend(['Runoff', 'Runoff interpolated'])
# fig.autofmt_xdate()
# plt.show()
# 
# #-Plot the baseflow and peakflow as stacked
# df1 = df.loc[(df.index>=pd.Timestamp('2019-11-01'))&(df.index<=pd.Timestamp('2019-12-31'))]
# fig, ax = plt.subplots()
# lines = plt.plot(df1.index, df1['Baseflow [m^3 s^-1]'], df1.index, df1['Peakflow [m^3 s^-1]'] +  df1['Baseflow [m^3 s^-1]'])
# plt.xlabel('Date')
# plt.ylabel('Streamflow [m$^3$ s$^{-1}$]')
# plt.grid(True)
# plt.title('Rangitata at Klondyke') 
# plt.legend(['Baseflow', 'Peakflow'])
# fig.autofmt_xdate()
# plt.show()

 
###############-PART TO SEPARATE PEAKS FROM BASEFLOW-##########################################################################################

#-Calculate the annual maxima for peak and volume
df = maxFlowVolStats(df)
df.to_csv(r'C:\Active\Projects\Rangitata_flood\data\flow_stats_final.csv', index=False)

graph_title = 'Rangitata at Klondyke'

# #-Scatter plot of annual maximum peak flow volume vs annual maximum peak flow
# fig = plt.figure(figsize=(14, 12), dpi=80, facecolor='w')
# plt.scatter(df['Flow volume [MCM]'], df['Total runoff interp. [m^3 s^-1]'],c='b', label='Data')
# for i in df.iterrows():
#     if i[1]['Max. flow [m^3 s^-1]'] != i[1]['Total runoff interp. [m^3 s^-1]']:
#         plt.text(i[1]['Flow volume [MCM]'], i[1]['Total runoff interp. [m^3 s^-1]'], int(i[1]['Year max flow']), color='red')
#         plt.scatter(i[1]['Flow volume [MCM]'], i[1]['Total runoff interp. [m^3 s^-1]'],c='r')
#     else:
#         plt.text(i[1]['Flow volume [MCM]'], i[1]['Total runoff interp. [m^3 s^-1]'], int(i[1]['Year max flow']), color='k')
#     if i[1]['Year max flow']==2019:
#         if i[1]['Max. flow [m^3 s^-1]'] != i[1]['Total runoff interp. [m^3 s^-1]']:
#             plt.scatter(i[1]['Flow volume [MCM]'], i[1]['Total runoff interp. [m^3 s^-1]'],c='r', s=150)
#         else:
#             plt.scatter(i[1]['Flow volume [MCM]'], i[1]['Total runoff interp. [m^3 s^-1]'],c='b', s=150)
# plt.xlabel('Peak flow volume [MCM]'); plt.ylabel('Peak flow [m$^3$ s$^{-1}$]')
# plt.xticks(np.arange(50, 600, step=50))
# plt.yticks(np.arange(250, 3250, step=250))
# plt.grid(True)
# plt.title('Maximum annual flow volume vs. maximum annual peakflow for %s' %graph_title)
# plt.show()
# #plt.savefig(r'C:\Active\Projects\Rangitata_flood\data\Klondyke_max_vol_vs_max_peak.png', dpi=600)
# 
# df_temp = df.copy()
# df_temp = df_temp.loc[df_temp['Max. flow [m^3 s^-1]']==df_temp['Total runoff interp. [m^3 s^-1]']]
# fig = plt.figure(figsize=(14, 12), dpi=80, facecolor='w')
# df_temp['ratio'] = df_temp['Avg. volume rate [m^3 s^-1]'] / df_temp['Total runoff interp. [m^3 s^-1]']
# df_temp.sort_values(by='Year max flow', inplace=True)
# plt.bar(df_temp['Year max flow'],df_temp['ratio'])
# plt.grid(True)
# plt.xlabel('Year'); plt.ylabel('Avg. volume rate / Peak flow rate [-]')
# plt.title('Ratio between average rate of peak flow volume and peak flow rate')
# #plt.savefig(r'C:\Active\Projects\Rangitata_flood\data\Klondyke_volume_to_peak_rate.png', dpi=600.)
# plt.show()
# df_temp = None

#-Maximum return period to plot (in years)
Tmax = 100

#####################-Peak flow volume analysis-#########################
df_sorted = df.sort_values(by=['Flow volume [MCM]'])

#-fit GEV and calculate inverse
gev_fit, gev_inv = fitGEV(df_sorted['Flow volume [MCM]'], Tmax)

#-get exceedances e and returnperiods t associated with the data
e,t = exceed(df_sorted['Flow volume [MCM]'].to_numpy())
#-Add column with return periods
df_sorted['T [year]'] = t
 
#-Plotting stuff
x = df_sorted['Flow volume [MCM]']
flow_2019 = df_sorted.loc[df_sorted['Year max flow']==2019,'Flow volume [MCM]'].values[0]
T_2019 = df_sorted.loc[df_sorted['Year max flow']==2019,'T [year]'].values[0]
 
#-Plot the PDF of the flow volume  
fn = r'C:\Active\Projects\Rangitata_flood\data\PDF_Rangitata_max_volume.png'    
plotPDF(x, gev_fit, np.arange(0, 1000, 50), 'Peak flow volume [MCM]', graph_title, fn)   
 
#-Plot the CDF of the flow volume    
fn = r'C:\Active\Projects\Rangitata_flood\data\CDF_Rangitata_max_volume.png'
plotCDF(x, gev_fit, e, 'Peak flow volume [MCM]', graph_title, flow_2019, T_2019, '2019 event', fn)
 
#-Plot the GEV fit and the data for the flow volume
fn = r'C:\Active\Projects\Rangitata_flood\data\GEV_Rangitata_max_volume.png'
plotGEV(x, t, gev_inv, Tmax, 'Peak flow volume [MCM]', graph_title, flow_2019, T_2019, '2019 event', fn)
 
 
#####################-Peak flow max analysis-#########################
df_sorted = df.sort_values(by=['Total runoff interp. [m^3 s^-1]'])
 
#-fit GEV and calculate inverse
gev_fit, gev_inv = fitGEV(df_sorted['Total runoff interp. [m^3 s^-1]'], Tmax)
 
#-get exceedances e and returnperiods t associated with the data
e,t = exceed(df_sorted['Total runoff interp. [m^3 s^-1]'].to_numpy())
#-Add column with return periods
df_sorted['T [year]'] = t
 
#-Plotting stuff
x = df_sorted['Total runoff interp. [m^3 s^-1]']
flow_2019 = df_sorted.loc[df_sorted['Year max flow']==2019,'Total runoff interp. [m^3 s^-1]'].values[0]
T_2019 = df_sorted.loc[df_sorted['Year max flow']==2019,'T [year]'].values[0]
 
#-Plot the PDF of the flow volume  
fn = r'C:\Active\Projects\Rangitata_flood\data\PDF_Rangitata_max_peak.png'    
plotPDF(x, gev_fit, 5, 'Peak flow [m$^3$ s$^{-1}$]', graph_title, fn)   
  
#-Plot the CDF of the flow volume    
fn = r'C:\Active\Projects\Rangitata_flood\data\CDF_Rangitata_max_peak.png'
plotCDF(x, gev_fit, e, 'Peak flow [m$^3$ s$^{-1}$]', graph_title, flow_2019, T_2019, '2019 event', fn)
 
#-Plot the GEV fit and the data for the flow volume
fn = r'C:\Active\Projects\Rangitata_flood\data\GEV_Rangitata_max_peak.png'
plotGEV(x, t, gev_inv, Tmax, 'Peak flow [m$^3$ s$^{-1}$]', graph_title, flow_2019, T_2019, '2019 event', fn)