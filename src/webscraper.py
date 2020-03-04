# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 12:50:18 2020

@author: awong3
"""

from lxml import html
import requests
import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup
import json

hk_latitude, hk_longitude = 22.2793278, 114.1628131

def fetch_highrisk():
    """
    Returns a DataFrame that contains the high risk area information.
    
    """
    page = requests.get('https://wars.vote4.hk/page-data/en/high-risk/page-data.json')
    data = json.loads(page.content)
    cases = data['result']['data']['allWarsCaseLocation']['edges']
    
    res = []
    
    for case in cases:
        res.append(case['node'])

    ## Change the 'case' column to one that uses string instead of dictionary
    high_risk_df = pd.DataFrame(res)
    high_risk_df['case'] = high_risk_df['case'].apply(lambda d: d['case_no'] if type(d) == dict else '')
    high_risk_df['start_date'] = pd.to_datetime(high_risk_df['start_date'].replace('Invalid date', None), format='%Y-%m-%d')
    high_risk_df['end_date'] = pd.to_datetime(high_risk_df['end_date'].replace('Invalid date', None), format='%Y-%m-%d')

    return high_risk_df

def fetch_cases():
    """
    Returns a DataFrame that contains the confirmed cases information.

    """
   
    page = requests.get('https://wars.vote4.hk/page-data/en/cases/page-data.json')
    data = json.loads(page.content)
    cases = data['result']['data']['allWarsCase']['edges']
    
    res = []
    
    for case in cases:
        res.append(case['node'])
    
    cases_df = pd.DataFrame(res)
    cases_df['case_no'] = cases_df['case_no'].astype(int)
    cases_df = cases_df.sort_values(by='case_no', ascending=False)

    return cases_df
    
def fetch_awaiting_time():
    """ 
    Return a list of dictionary that contains the hospital awaiting time.
    
    """
    page = requests.get('https://wars.vote4.hk/page-data/en/ae-waiting-time/page-data.json')
    data = json.loads(page.content)
    cases = data['result']['data']['allAeWaitingTime']['edges']
    
    res = []
    
    for case in cases:
        res.append(case['node'])
    
    awaiting_df = pd.DataFrame(res)

    # Add column 'topWait_value' that will be used in hte slide bar to display hospitals of a particular waiting time group
    replace_dict = {f'> {i}': i for i in np.arange(1, 24)}
    replace_dict['< 1'] = 0
    awaiting_df['topWait_value'] = awaiting_df['topWait'].replace(replace_dict)
    return awaiting_df

def fetch_stat():
    """
    Return a DataFrame that represent death, confirmed, investigating and reported numbers respectively.
    
    There are two elements in the json that contain the required value: 
    "allBotWarsLatestFigures" and "allWarsLatestFiguresOverride".
    
    The values in allBotWarsLatestFigures are the record in history for every day.
    The values in allWarsLatestFiguresOverride are the live values.
    Whenenver an attribute in allWarsLatestFiguresOverride is not an empty string,
    it overrides the values in allBotWarsLatestFigures.
    
    """
    statnames = ['Death', 'Confirmed', 'Investigating', 'Reported']
    
    page = requests.get('https://wars.vote4.hk/page-data/en/page-data.json')
    data = json.loads(page.content)
#     print(json.dumps(data['result']['data'], indent=4, sort_keys=True))
    stats_yesterday = data['result']['data']['allBotWarsLatestFigures']['edges'][0]
    stats_live = data['result']['data']['allWarsLatestFiguresOverride']['edges'][0]
    
    res = {}
    
    for attr in ['death', 'confirmed', 'investigating', 'reported', 'discharged', 'ruled_out']:
        if stats_live['node'][attr] != "":
            res[attr] = stats_live['node'][attr]
        else:
            res[attr] = stats_yesterday['node'][attr]
    
    df = pd.DataFrame(data=res, index=[0])
    
    return df
