import sys
import operator
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

datadir = 'data'

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

# Add new column with day of week
df_raw['dayofweek'] = df_raw.cal_dt.astype('datetime64[D]').apply(lambda x: x.isoweekday())

# Some basic plots
fig, axs = plt.subplots(1,2, figsize=(15, 10))
df_raw['language'].value_counts().plot.bar(subplots=True, ax=axs[0])
df_raw['source'].value_counts().plot.bar(subplots=True, ax=axs[1])

fig, axs = plt.subplots(1,1)
axs.pie(df_raw.language.value_counts(normalize=True), labels=df_raw.language.unique(), autopct='%1.1f%%')
axs.axis('equal')
fig.suptitle('Language Distribution')
fig.savefig('language_pie.png')

fig, axs = plt.subplots(1,1)
axs.pie(df_raw.source.value_counts(normalize=True), labels=df_raw.source.unique(), autopct='%1.1f%%')
axs.axis('equal')
fig.suptitle('Source Distribution')
fig.savefig('source_pie.png')
fig.savefig('lang_source_bars.png')
plt.close()

# Create coarser source categories
source_dict = {j: 'job_alert' for j in df_raw.source.unique() if 'alert' in j}
source_dict.update({j: 'vacancy' for j in df_raw.source.unique() if 'vacancy' in j})
source_dict.update({j: j for j in df_raw.source.unique() if 'vacancy' not in j and 'alert' not in j})
df_raw['source_coarse'] = df_raw.source.map(source_dict)
fig, axs = plt.subplots(1,1)
axs.pie(df_raw.source_coarse.value_counts(normalize=True), labels=np.unique(list(source_dict.values())), autopct='%.2f')
axs.axis('equal')
fig.savefig('source_coarse_pie.png')

# Do users stick to the same source category?
df_raw.groupby('user_id')['source_coarse'].value_counts(normalize=True).unstack().plot.box()

# Do users stick to the same language?
df_raw.groupby('user_id')['source_coarse'].value_counts(normalize=True).unstack().plot.box()

dates = sorted(df_raw.cal_dt_int32.unique())
#df_raw.groupby(['cal_dt'])['user_id'].value_counts().unstack().mean(1).plot(ax=axs)
clicks_de = df_raw.loc[df_raw.language=='de'].groupby(['cal_dt', 'dayofweek'])['user_id'].value_counts().unstack()
clicks_de.lang = 'DE'
clicks_fr = df_raw.loc[df_raw.language=='fr'].groupby(['cal_dt', 'dayofweek'])['user_id'].value_counts().unstack()
clicks_fr.lang = 'FR'
clicks_en = df_raw.loc[df_raw.language=='en'].groupby(['cal_dt', 'dayofweek'])['user_id'].value_counts().unstack()
clicks_en.lang = 'EN'

fig, axs = plt.subplots(1,3, figsize=(15,10))
for idx, clicks in enumerate([clicks_de, clicks_en, clicks_fr]):
    axs[idx].hist(clicks.mean(1), density=True, label=clicks.lang)
    axs[idx].text(2, 5.4, 'mean {0:.3f}'.format(clicks.mean(1).mean()))
    axs[idx].text(2, 5.32, 'std {0:.3f}'.format(clicks.mean(1).std()))
    axs[idx].text(2, 5.24, 'max {0:.3f} @ {1}'.format(clicks.mean(1).max(), clicks.mean(1).idxmax()))
    axs[idx].legend()
fig.suptitle("Avg. no. of clicks per user per day")
fig.tight_layout(rect=[0, 0.03, 1, 0.95])
fig.savefig('hist_avgclicks.png')

def do_ts_plots(inputdata, mode='notna().sum()', ylabel='No. active users', pngfile=None):
    fig, axs = plt.subplots(1,3, figsize=(15,10))
    for idx, clicks in enumerate(inputdata):
        lang = clicks.lang
        for m in mode.split('.'):
            print(clicks.shape)
            farg = m[m.find('(')+1:m.find(')')]
            if len(farg) == 0:
                clicks = getattr(clicks, m[:m.find('(')])()
            else:
                clicks = getattr(clicks, m[:m.find('(')])(int(farg))
        axs[idx].plot(clicks, label=lang)
        axs[idx].text(2, 5.4, 'mean {0:.3f}'.format(clicks.mean()))
        axs[idx].text(2, 5.32, 'std {0:.3f}'.format(clicks.std()))
        if 'mean' in mode:
            axs[idx].text(2, 5.24, 'max {0:.3f} @ {1}'.format(clicks.max(), clicks.idxmax()))
        #axs[idx].set_ylim(1.6, 5.5)
        axs[idx].set_ylabel(ylabel)
        axs[idx].set_xticks(range(5,90,10))
        axs[idx].set_xticklabels(operator.itemgetter(*range(5,90,10))(dates))
        axs[idx].legend()
        for ticks in axs[idx].get_xticklabels():
            ticks.set_rotation(90)
    if pngfile is not None:
        fig.savefig(pngfile)
    return fig, axs


fig1, axs1 = do_ts_plots([clicks_de, clicks_fr, clicks_en], 'notna().sum(1)', ylabel='No. active users')
fig1.suptitle("Active users per day")
fig1.tight_layout(rect=[0, 0.03, 1, 0.95])
fig1.savefig('ts_activeusers.png')

fig1, axs1 = do_ts_plots([clicks_de, clicks_fr, clicks_en], 'sum(1)', ylabel='Total no. clicks')
fig1.suptitle("Total number of clicks per day")
fig1.tight_layout(rect=[0, 0.03, 1, 0.95])
fig1.savefig('ts_sumclicks.png')

fig1, axs1 = do_ts_plots([clicks_de, clicks_fr, clicks_en], 'mean(1)', ylabel='<clicks> per user')
fig1.suptitle("Daily average no. clicks per user")
fig1.tight_layout(rect=[0, 0.03, 1, 0.95])
fig1.savefig('ts_avgclicks.png')

# Boxplot of clicks per day of week
clicks_de.sum(1).unstack().plot.box()
clicks_fr.sum(1).unstack().plot.box()
clicks_en.sum(1).unstack().plot.box()

# Relative change
rel_de = (clicks_de.sum(1).diff(1)/clicks_de.sum(1).shift(1))
rel_fr = (clicks_fr.sum(1).diff(1)/clicks_fr.sum(1).shift(1))
rel_en = (clicks_en.sum(1).diff(1)/clicks_en.sum(1).shift(1))

fig, axs = plt.subplots(1,3, figsize=(15,10))
for idx, reldata in enumerate([rel_de, rel_en, rel_fr]):
    axs[idx].plot(reldata)
    axs[idx].set_xticks(range(5,90,10))
    axs[idx].set_xticklabels(operator.itemgetter(*range(5,90,10))(dates))
    axs[idx].set_ylabel('daily %change tot. clicks')
    for ticks in axs[idx].get_xticklabels():
        ticks.set_rotation(90)
fig.tight_layout(rect=[0, 0.03, 1, 0.95])
fig.suptitle('Daily pct. change clicks')

fig.savefig('rel_totalclicks.png')

# Add info from scraped data
jobinfo = pd.read_csv('jobinfo2.csv', encoding='utf-8', lineterminator='\n')
# Transform employment type, keep only first entry for simplicity
jobinfo['employmentType'] = jobinfo.employmentType.fillna('NA').apply(lambda x: x[1:-1].split(',')[0])
df_merged = df_raw.merge(jobinfo[['job_id', 'industry', 'employmentType']], left_on='job_id', right_on='jobid')

# Job type pie chart
fig, axs = plt.subplots(1,1)
axs.pie(df_merged.employmentType.value_counts(normalize=True), labels=df_merged.employmentType.unique(), autopct='%1.1f%%')
axs.axis('equal')
fig.suptitle('Employment type distribution')
fig.savefig('employment_type.png')

fig, axs = plt.subplots(1,1)
axs.bar(df_merged.industry)
