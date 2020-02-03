# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 12:50:18 2020

@author: awong3
"""

from lxml import html
import requests

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
    Returns a list of dictionary that contains the confirmed cases information.
    
    """
    page = requests.get('https://wars.vote4.hk/en/cases')
    tree = html.fromstring(page.content)
    
    boxes = tree.xpath('//*[@id="gatsby-focus-wrapper"]/div/main/div[2]/div[contains(@class, "CaseCard__WarsCaseContainer-zltyy4-0")]')
    
    res = []
    
    for box in boxes:
        s = box.xpath('./div[1]/div/text()')
        casenum = s[0]
        status = s[1]
        age = box.xpath('./div[2]/div[1]/text()')[0]
        date = box.xpath('./div[3]/div[1]/div[1]/text()')[0]
        residence = box.xpath('./div[3]/div[1]/div[2]/text()')[0]
        hospital = box.xpath('./div[3]/div[1]/div[3]/text()')[0]
        desc = box.xpath('./div[4]/p/text()')[0]
        
        res.append({
                'casenum': str(casenum),
                'status': str(status),
                'age': str(age),
                'date': str(date),
                'residence': str(residence),
                'hospital': str(hospital),
                'desc': str(desc)
                })
    
    return res

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
    
    return res

def fetch_stat():
    """
    Return a list of 4 numbers that represent death, confirmed, investigating and reported numbers respectively.
    
    """
    page = requests.get('https://wars.vote4.hk/en/')
    tree = html.fromstring(page.content)
    
    boxes = tree.xpath('//div[contains(@class, "pages__DailyStatsContainer-sc-6kvjaa-1")]/div')
    res = [int(box.xpath('./p[1]/text()')[0]) for box in boxes]
    
    return res