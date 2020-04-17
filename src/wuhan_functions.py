import os
try:
    import pyodbc
except Exception as e:
    print(f'Unable to import pyodbc')
from geopy.geocoders import Nominatim
import time
import pickle
import pandas as pd
from webscraper import fetch_highrisk, fetch_cases, fetch_awaiting_time

dir_path = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(dir_path, '..', 'data') 

def calculate_stats(cases_df):
    """Calcualte the basic statistics based on the information from cases_df

    """

    death = (cases_df['status_en'] == 'Deceased').sum()
    confirmed = cases_df.shape[0]
    discharged = (cases_df['status_en'] == 'Discharged').sum()
    hospitalised = (cases_df['status_en'] == 'Hospitalised').sum()

    df = pd.DataFrame(
        data={
            'death': death,
            'confirmed': confirmed,
            'discharged': discharged,
            'hospitalised': hospitalised
        },
        index=[0]
    )
    return df

def load_address_csv(path=os.path.join(data_dir, 'ADDRESS.tsv')):
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
        },
        sep='\t'
    )
    return address_df

def load_awaiting_csv(path=os.path.join(data_dir, 'AWAITING.tsv')):
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
        },
        sep='\t'
    )
    return awaiting_df

def load_cases_csv(path=os.path.join(data_dir, 'CASES.tsv')):
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
        },
        sep='\t'
    )

    return cases_df

def load_high_risk_csv(path=os.path.join(data_dir, 'HIGH_RISK.tsv')):
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
        },
        sep='\t'
    )

    high_risk_df['end_date'] = pd.to_datetime(high_risk_df['end_date'], format='%Y-%m-%d')
    high_risk_df['start_date'] = pd.to_datetime(high_risk_df['start_date'], format='%Y-%m-%d')

    return high_risk_df

def load_hospitals_csv(path=os.path.join(data_dir, 'HOSPITALS.tsv')):
    hospital_df = pd.read_csv(
        path,
        dtype={
            'address': str,
            'category': str,
            'id': int,
            'latitude': float,
            'longitude': float,
        },
        sep='\t'
    )
    
    return hospital_df

def load_hospital_awaiting_csv(
        hospital_path=os.path.join(data_dir, 'HOSPITALS.tsv'),
        awaiting_path=os.path.join(data_dir, 'AWAITING.tsv')
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
    hospital_awaiting_df = load_hospital_awaiting_csv()
    stats_df = calculate_stats(cases_df)
    return cases_df, high_risk_df, stats_df, hospital_awaiting_df

def convert_csv_to_pickle():
    cases_df = load_cases_csv()
    high_risk_df = load_high_risk_csv()
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



def load_data_pkl():
    with open(os.path.join(data_dir, 'AWAITING.pkl'), 'rb') as f:
        awaiting_df = pickle.load(f)
    with open(os.path.join(data_dir, 'CASES.pkl'), 'rb') as f:
        cases_df = pickle.load(f)
    with open(os.path.join(data_dir, 'HIGH_RISK.pkl'), 'rb') as f:
        high_risk_df = pickle.load(f)
    with open(os.path.join(data_dir, 'HOSPITALS.pkl'), 'rb') as f:
        hospital_df = pickle.load(f)

    stats_df = calculate_stats(cases_df)

    hospital_awaiting_df = pd.merge(
        hospital_df[['address', 'latitude', 'longitude']],
        awaiting_df[['name_en', 'topWait', 'topWait_value']],
        how='left',
        left_on='address',
        right_on='name_en'
    )

    return cases_df, high_risk_df, stats_df, hospital_awaiting_df

def load_data_sql():
    server = 'datavisualizationfti.database.windows.net'
    database = 'myVisualizationData'
    username = 'azureuser'
    password = 'Pass7890'
    driver = 'SQL Server'   
    
    cnxn = pyodbc.connect('DRIVER={' + driver + '};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    
    cases_df = pd.read_sql('SELECT * FROM CASES', cnxn)
    high_risk_df = pd.read_sql('SELECT * FROM HIGH_RISK', cnxn)
    hospital_df = pd.read_sql('SELECT * FROM HOSPITALS', cnxn)
    awaiting_df = pd.read_sql('SELECT * FROM AWAITING', cnxn)
    
    cnxn.close()
    
    cases_df = cases_df.astype(
        {
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
    
    high_risk_df['lat'] = pd.to_numeric(high_risk_df['lat'])
    high_risk_df['lng'] = pd.to_numeric(high_risk_df['lng'])
    high_risk_df['start_date'] = pd.to_datetime(high_risk_df['start_date'].replace('Invalid date', None), format='%Y-%m-%d')
    high_risk_df['end_date'] = pd.to_datetime(high_risk_df['end_date'].replace('Invalid date', None), format='%Y-%m-%d')
    
    hospital_df = hospital_df.astype(
        {
            'address': str,
            'category': str,
            'id': int,
            'latitude': float,
            'longitude': float,
        }
    )
    
    awaiting_df = awaiting_df.astype(
        {
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
    
    hospital_awaiting_df = pd.merge(
        hospital_df[['address', 'latitude', 'longitude']],
        awaiting_df[['name_en', 'topWait', 'topWait_value']],
        how='left',
        left_on='address',
        right_on='name_en'
    )
    
    stats_df = calculate_stats(cases_df)
    
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
    stats_df = calculate_stats(cases_df)

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
        print('Trying to load data from SQL database.')
        return load_data_sql()
    except Exception as e:
        print(f'Loading SQL database failed, trying to load data from pkl file.')
            
    try:
        print('Trying to load data from pickle file.')
        return load_data_pkl()
    except Exception as e:
        print(f'Loading pickle file failed, trying to read from csv.')
        # convert_csv_to_pickle()

    print('Trying to load data from csv.')
    return load_data_csv()

