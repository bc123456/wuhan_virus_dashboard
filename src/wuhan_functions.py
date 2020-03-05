import os

from geopy.geocoders import Nominatim
import time
import pickle
import pandas as pd
from webscraper import fetch_highrisk, fetch_cases, fetch_awaiting_time, fetch_stat

dir_path = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(dir_path, '..', 'data') 


def load_address_csv(path=os.path.join(data_dir, 'ADDRESS.csv')):
    address_df = pd.read_csv(
        path, 
        dtype={
            'id': str,
            'sub_district_zh': str,
            'sub_district_en': str,
            'location_en': str,
            'location_zh': str,
            'longitude': float,
            'latitude': float
        }
    )
    return address_df

def load_awaiting_csv(path=os.path.join(data_dir, 'AWAITING.csv')):
    awaiting_df = pd.read_csv(
        path,
        dtype={
            'district_en': str,
            'district_zh': str,
            'hospCode': str,
            'hospTimeEn': str,
            'name_en': str,
            'name_zh': str,
            'sub_district_en': str,
            'sub_district_zh': str,
            'topWait': str,
            'topWait_value': int
        }
    )
    return awaiting_df

def load_cases_csv(path=os.path.join(data_dir, 'CASES.csv')):
    cases_df = pd.read_csv(
        path,
        dtype={
            'case_no': int,
            'onset_date': str,
            'confirmation_date': str,
            'gender': str,
            'age': int,
            'hospital_zh': str,
            'hospital_en': str,
            'status': str,
            'status_zh': str,
            'status_en': str,
            'type_zh': str,
            'type_en': str,
            'citizenship_zh': str,
            'citizenship_en': str,
            'detail_zh': str,
            'detail_en': str,
            'classification': str,
            'classification_zh': str,
            'classification_en': str,
            'source_url': str,
        }
    )

    return cases_df

def load_high_risk_csv(path=os.path.join(data_dir, 'HIGH_RISK.csv')):
    high_risk_df = pd.read_csv(
        path,
        dtype={
            'action_en': str,
            'action_zh': str,
            'case': str,
            'case_no': str,
            'end_date': str,
            'id': str,
            'lat': float,
            'lng': float,
            'location_en': str,
            'location_zh': str,
            'remarks_en': str,
            'remarks_zh': str,
            'source_url_1': str,
            'source_url_2': str,
            'start_date': str,
            'sub_district_en': str,
            'sub_district_zh': str,
            'type': str,
        }
    )

    high_risk_df['end_date'] = pd.to_datetime(high_risk_df['end_date'], format='%Y-%m-%d')
    high_risk_df['start_date'] = pd.to_datetime(high_risk_df['start_date'], format='%Y-%m-%d')

    return high_risk_df

def load_hospitals_csv(path=os.path.join(data_dir, 'HOSPITALS.csv')):
    hospital_df = pd.read_csv(
        path,
        dtype={
            'address': str,
            'category': str,
            'id': int,
            'latitude': float,
            'longitude': float,
        }
    )
    return hospital_df

def load_stats_csv(path=os.path.join(data_dir, 'STATS.csv')):
    stats_df = pd.read_csv(
        path,
        dtype={
            'confirmed': int,
            'death': int,
            'discharged': int,
            'investigating': int,
            'reported': int,
            'ruled_out': int,
        }
    )
    return stats_df

def load_hospital_awaiting_csv(
        hospital_path=os.path.join(data_dir, 'HOSPITALS.csv'),
        awaiting_path=os.path.join(data_dir, 'AWAITING.csv')
    ):
    hospital_df = load_hospitals_csv(hospital_path)
    awaiting_df = load_awaiting_csv(awaiting_path)

    hospital_awaiting_df = pd.merge(
        hospital_df[['address', 'latitude', 'longitude']],
        awaiting_df[['name_en', 'topWait', 'topWait_value']],
        how='left',
        left_on='address',
        right_on='name_en'
    )

    return hospital_awaiting_df
    

def load_data_csv():
    cases_df = load_cases_csv()
    high_risk_df = load_high_risk_csv()
    stats_df = load_stats_csv()
    hospital_awaiting_df = load_hospital_awaiting_csv()

    return cases_df, high_risk_df, stats_df, hospital_awaiting_df

def convert_csv_to_pickle():
    cases_df = load_cases_csv()
    high_risk_df = load_high_risk_csv()
    stats_df = load_stats_csv()
    hospital_df = load_hospitals_csv()
    awaiting_df = load_awaiting_csv()

    with open(os.path.join(data_dir, 'AWAITING.pkl'), 'wb') as f:
         pickle.dump(awaiting_df, f)
    with open(os.path.join(data_dir, 'CASES.pkl'), 'wb') as f:
         pickle.dump(cases_df, f)
    with open(os.path.join(data_dir, 'HIGH_RISK.pkl'), 'wb') as f:
         pickle.dump(high_risk_df, f)
    with open(os.path.join(data_dir, 'HOSPITALS.pkl'), 'wb') as f:
         pickle.dump(hospital_df, f)
    with open(os.path.join(data_dir, 'STATS.pkl'), 'wb') as f:
         pickle.dump(stats_df, f)



def load_data_pkl():
    with open(os.path.join(data_dir, 'AWAITING.pkl'), 'rb') as f:
        awaiting_df = pickle.load(f)
    with open(os.path.join(data_dir, 'CASES.pkl'), 'rb') as f:
        cases_df = pickle.load(f)
    with open(os.path.join(data_dir, 'HIGH_RISK.pkl'), 'rb') as f:
        high_risk_df = pickle.load(f)
    with open(os.path.join(data_dir, 'HOSPITALS.pkl'), 'rb') as f:
        hospital_df = pickle.load(f)
    with open(os.path.join(data_dir, 'STATS.pkl'), 'rb') as f:
        stats_df = pickle.load(f)

    hospital_awaiting_df = pd.merge(
        hospital_df[['address', 'latitude', 'longitude']],
        awaiting_df[['name_en', 'topWait', 'topWait_value']],
        how='left',
        left_on='address',
        right_on='name_en'
    )

    return cases_df, high_risk_df, stats_df, hospital_awaiting_df

def load_data_live():
    awaiting_df = fetch_awaiting_time()
    cases_df = fetch_cases()
    high_risk_df = fetch_highrisk()
    try:
        with open(os.path.join(data_dir, 'HOSPITALS.pkl'), 'rb') as f:
            hospital_df = pickle.load(f)
    except Exception as e:
        hospital_df = load_hospitals_csv()
    stats_df = fetch_stat()

    hospital_awaiting_df = pd.merge(
        hospital_df[['address', 'latitude', 'longitude']],
        awaiting_df[['name_en', 'topWait', 'topWait_value']],
        how='left',
        left_on='address',
        right_on='name_en'
    )

    return cases_df, high_risk_df, stats_df, hospital_awaiting_df

def load_data(live=False):

    if live:
        try:
            print('Loading live data')
            return load_data_live()
        except Exception as e:
            print(e)
            print(f'Load live data failed, switching to loading saved data')
            
    try:
        print('Trying to load data from pickle file.')
        return load_data_pkl()
    except Exception as e:
        print(f'Loading pickle file failed, trying to read from csv.')
        # convert_csv_to_pickle()

    print('Trying to load data from csv.')
    return load_data_csv()


