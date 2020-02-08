from geopy.geocoders import Nominatim
import time
import pickle
import pandas as pd
from webscraper import fetch_high_risk_address


def pop_address(address):
    address_lst = address.split(',')
    return ','.join(address_lst[1:])
    
def get_coordinates(address):
    print(f'Getting the coordinates for new address: {address}.')
    address = address + ', Hong Kong'
    trial0 = 0
    trial1 = 0
    trial2 = 0
    location = None
    geolocator = Nominatim(user_agent='hk_explorer')
    while location is None and trial0 < 5:
        trial0 += 1
        try:
            location = geolocator.geocode(address)
        except:
            pass
        time.sleep(1)
    if location is None:
        simplified_address1 = pop_address(address)
        while location is None and trial1 < 5:
            trial1 += 1
            try:
                location = geolocator.geocode(simplified_address1)
            except:
                pass
            time.sleep(1)
    if location is None:
        simplified_address2 = pop_address(simplified_address1)
        while location is None and trial2 < 5:
            trial2 += 1
            try:
                location = geolocator.geocode(simplified_address2)
            except:
                pass
            time.sleep(1)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None, None

def update_address(address_df, high_risk_df):
    unseen_df = high_risk_df[
        ~high_risk_df['id'].isin(address_df['id'])
    ][
        ['id', 'sub_district_zh', 'sub_district_en', 'location_en', 'location_zh']
    ].copy()

    for idx, row in unseen_df.iterrows():
        address_name = row['location_en'] + ', ' + row['sub_district_en']
        if 'high speed rail' in address_name.lower():
            latitude = 22.304080
            longitude = 114.166501
        elif '航空' in row['location_zh']:
            latitude = 22.308007
            longitude = 113.918803
        else:
            latitude, longitude = get_coordinates(address_name)

        address_df = address_df.append(
            pd.Series({
                'id': row['id'],
                'sub_district_zh': row['sub_district_zh'],
                'sub_district_en': row['sub_district_en'],
                'location_en': row['location_en'],
                'location_zh': row['location_zh'],
                'latitude': latitude,
                'longitude': longitude,
            }),
            ignore_index=True
        )
    return address_df

