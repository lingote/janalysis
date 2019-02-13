import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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
fig, axs = plt.subplots(1,2, figsize=(15, 10))
df_raw['language'].value_counts().plot.bar(subplots=True, ax=axs[0])
df_raw['source'].value_counts().plot.bar(subplots=True, ax=axs[1])
#for ticks in axs[1].get_xticklabels():
#    ticks.set_rotation(45)
fig.savefig('lang_source_bars.png')
plt.close()

fig, axs = plt.subplots(1,3, figsize=(20,10))
dates = sorted(df_raw.cal_dt_int32.unique())
#df_raw.groupby(['cal_dt'])['user_id'].value_counts().unstack().mean(1).plot(ax=axs)
df_raw.loc[df_raw.language=='de'].groupby(['cal_dt'])['user_id'].value_counts().unstack().mean(1).plot(ax=axs[0], label='DE')
df_raw.loc[df_raw.language=='fr'].groupby(['cal_dt'])['user_id'].value_counts().unstack().mean(1).plot(ax=axs[1], label='FR', x_compat=True)
df_raw.loc[df_raw.language=='en'].groupby(['cal_dt'])['user_id'].value_counts().unstack().mean(1).plot(ax=axs[2], label='EN')
axs[0].legend()
axs[1].set_xticks(range(len(dates)))
axs[1].set_xticklabels(dates[::19])
axs[1].xaxis.set_major_locator(ticker.MultipleLocator(20))
axs[1].xaxis.set_minor_locator(ticker.MultipleLocator(1))
axs[1].legend()
axs[2].legend()
axs[0].set
plt.show()