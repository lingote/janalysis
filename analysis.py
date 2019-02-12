import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import urllib
import json
from html.parser import HTMLParser

datadir = '/home/ignacio/myprojects/jcloud/'

df_raw = pd.read_csv(f'{datadir}/jobcloud_interview_challenge.csv')

# Get some basic data information
print('dataframe size {}'.format(df_raw.shape))
print('dataframe columns {}'.format(df_raw.columns))
print('dataframe dtypes {}'.format(df_raw.dtypes))
print('dataframe size {0:.3f}MB'.format(sys.getsizeof(df_raw)/1024/1024))
print('dataframe memory usage (Bytes) per column:')
print(df_raw.memory_usage())

# Are there any NAN values?
print('Any nan values?')
print(df_raw.isnull().sum())

# Transform 'cal_dt' to np.int32. Not really an issue here since data small enough to keep in memory
df_raw['cal_dt_int32'] = df_raw['cal_dt'].apply(lambda x: x.replace('-','')).astype(np.int32)

# Check memory usage
print('Updated memory usage:')
print(df_raw.memory_usage())

# Some basic plots
fig, axs = plt.subplots(1,2)
df_raw['language'].value_counts().plot.bar(subplots=True, ax=axs[0])
df_raw['source'].value_counts().plot.bar(subplots=True, ax=axs[1])
#for ticks in axs[1].get_xticklabels():
#    ticks.set_rotation(45)
#plt.show()

