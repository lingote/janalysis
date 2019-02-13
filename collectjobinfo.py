import time
import multiprocessing
import pandas as pd
import numpy as np
import urllib
import json
from html.parser import HTMLParser

datadir = '/home/ignacio/myprojects/jcloud/'

# Collect additional data for jobId from url

class JobInfoHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.head = False
        self.script = False
        self._jobdata = {}

    @property
    def jobdata(self):
        return self._jobdata

    def handle_starttag(self, tag, attrs):
        if tag!='head' and tag!='script':
            return
        if tag=='head':
            self.head = True
        if tag=='script':
            for attr in attrs:
                if attr == ('id','linkeddata'):
                    self.script = True

    def handle_endtag(self, tag):
        if tag=='head':
            self.head = False
        if tag=='script':
            self.script = False

    def handle_data(self, data):
        if self.head and self.script:
            self._jobdata = {'title' : np.nan, 'company' : np.nan,
                             'joblocation' : np.nan, 'industry' : np.nan,
                             'employmentType' : np.nan, 'category' : np.nan}
            d = json.loads(data)
            if 'title' in d:
                self.jobdata['title'] = d['title'].replace('\n', ' ')
            # Some records have no company name
            if 'hiringOrganization' in d:
                if not isinstance(d['hiringOrganization'], str):
                    self.jobdata['company'] = d['hiringOrganization']['name'].replace('\n', ' ')
            if 'joblocation' in d:
                try:
                    self.jobdata['joblocation'] = d['jobLocation']['address']['addressLocality'].replace('\n', ' ')
                except KeyError as e:
                    pass
            if 'industry' in d:
                self.jobdata['industry'] = d['industry'].replace('\n', ' ')
            if 'employmentType' in d:
                self.jobdata['employmentType'] = [emp.replace('\n', ' ') for emp in  d['employmentType']]
            if 'occupationalCategory' in d:
                self.jobdata['category'] = d['occupationalCategory'].replace('\n', ' ')

    def reset(self):
        HTMLParser.reset(self)
        self.head = False
        self.script = False
        self._jobdata = {}


def collectjobinfo(jobid, parser):
    """
    Collect job info for given job id

    Args:
        jobid (str): job identifier

    Returns:
        utf-8 output of url request
    """
    assert isinstance(parser, JobInfoHTMLParser), 'wrong parser object type {}'.format(type(parser))
    try:
        resp = urllib.request.urlopen('https://www.jobs.ch/de/stellenangebote/detail/{}/'.format(str(jobid)))
        res = resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        #print(f'got error {e.code} for job id {jobid}')
        res = e.read().decode('utf-8')
    parser.feed(res)
    jobdata = parser.jobdata
    jobdata['jobid'] = jobid
    return jobdata


if __name__ == '__main__':
    # Create a new dataframe with job infos
    parser = JobInfoHTMLParser()
    df_raw = pd.read_csv(f'{datadir}/jobcloud_interview_challenge.csv')
    njobs = df_raw.job_id.unique().shape[0]
    jobinfo_dict = {col: np.ndarray((njobs,), dtype='O') for col in ['jobid', 'title', 'company', 'joblocation', 'industry', 'employmentType', 'category']}
    jobids = sorted(df_raw.job_id.unique())
    pool = multiprocessing.Pool(processes=16)
    starttime = time.time()
    results = [pool.apply_async(collectjobinfo, (x, parser)) for x in jobids]
    idx = 0
    for result in results:
        jobinfo = result.get()
        for key in jobinfo.keys():
            jobinfo_dict[key][idx] = jobinfo[key]
        idx += 1

    print('took {}'.format(time.time() - starttime))
    pd.DataFrame.from_dict(jobinfo_dict).to_csv('jobinfo3.csv', encoding='utf-8')
