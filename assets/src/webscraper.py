# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 12:50:18 2020

@author: awong3
"""

from lxml import html
import requests
import pandas as pd

def fetch_highrisk():
    """
    Returns a list of dictionary that contains the high risk area information.
    
    """
    page = requests.get('https://wars.vote4.hk/en/high-risk')
    tree = html.fromstring(page.content)
    
    boxes = tree.xpath('//*[@id="gatsby-focus-wrapper"]/div/main/div[2]/div[contains(@class, "Card__StyledBox-sc-6m23vi-0 cNwpZn")]')
    
    res = []
    
    for box in boxes:
        district = box.xpath('./div[1]/div[1]/div[1]/div/span[contains(@class, "MuiTypography-body2")]/text()')
        address = box.xpath('./div[1]/div[1]/div[1]/div/span[contains(@class, "MuiTypography-h6")]/text()')
        msg = box.xpath('./div[1]/span/text()')
        
        res.append({'district': str(district[0]), 'address': str(address[0]), 'msg': str(msg[0])})

    return res

def fetch_cases():
    """
    Returns a DataFrame that contains the confirmed cases information.

    """
    page = requests.get('https://wars.vote4.hk/en/cases')
    tree = html.fromstring(page.content)

    boxes = tree.xpath('//*[@id="gatsby-focus-wrapper"]/div/main/div[2]/div[contains(@class, "CaseCard__WarsCaseContainer-zltyy4-0")]')

    res = []

    for box in boxes:
        s = box.xpath('./div[1]/div/text()')
        casenum = s[0]
        status = s[1]
        age_and_gender = box.xpath('./div[2]/div[1]/text()')[0]
        date = box.xpath('./div[3]/div[1]/div[1]/text()')[0]
        residence = box.xpath('./div[3]/div[1]/div[2]/text()')[0]
        hospital = box.xpath('./div[3]/div[1]/div[3]/text()')[0]
        desc = box.xpath('./div[4]/p/text()')[0]
        
        # clean up casenum
        casenum = casenum.replace('#', '').replace('(Confirmed)', '').strip()
        #get age from age_and_gender
        age = age_and_gender.replace('Age', '').replace('Male', '').replace('Female', '').strip()
        
        #get gender from age_and_gender
        gender = None
        if 'female' in age_and_gender.lower():
            gender = 'Female'
        elif 'male' in age_and_gender.lower():
            gender = 'Male'

        res.append({
            'casenum': str(casenum),
            'status': str(status),
            'age': int(age),
            'gender': str(gender),
            'date': str(date),
            'residence': str(residence),
            'hospital': str(hospital),
            'desc': str(desc)
        })

    return pd.DataFrame(res)

def fetch_awaiting_time():
    """
    Return a list of dictionary that contains the hospital awaiting time.
    
    """
    page = requests.get('https://wars.vote4.hk/en/ae-waiting-time')
    tree = html.fromstring(page.content)
    
    boxes = tree.xpath('//*[@id="gatsby-focus-wrapper"]/div/main/div[2]/div[contains(@class, "Card__StyledBox-sc-6m23vi-0 cNwpZn")]')

    res = []
    
    for box in boxes:
        district = box.xpath('./div[1]/div[1]/p[1]/text()')[0]
        hospital = box.xpath('./div[1]/div[1]/p[2]/text()')[0]
        time = box.xpath('./div[1]/h6/text()')[0]
        
        res.append({
                'district': str(district),
                'hospital': str(hospital),
                'time': str(time)
                })
    
    return pd.DataFrame(res)

def fetch_stat():
    """
    Return a DataFrame that represent death, confirmed, investigating and reported numbers respectively.

    """
    statnames = ['Death', 'Confirmed', 'Investigating', 'Reported']
    
    page = requests.get('https://wars.vote4.hk/en/')
    tree = html.fromstring(page.content)

    boxes = tree.xpath('//div[contains(@class, "pages__DailyStatsContainer-sc-6kvjaa-1")]/div')
    res = [int(box.xpath('./p[1]/text()')[0]) for box in boxes]
    
    df = pd.DataFrame(data=[res], columns=statnames)

    return df