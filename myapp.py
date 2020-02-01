import os

import dash
import dash_core_components as dcc
import dash_html_components as html

import pickle
import plotly.express as px
import pandas as pd
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
import numpy as np
import time

#########################
## Set up Dash
#########################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server


#########################
## Get Data
#########################

url = r'https://wars.vote4.hk/en/high-risk'
hk_latitude, hk_longitude = 22.2793278, 114.1628131
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

html_addresses = soup.find_all(
    'span', 
    class_=r'MuiTypography-root MuiTypography-h6 MuiTypography-colorTextPrimary'
)

high_risk_addresses = [job_elem.text + ', Hong Kong' for job_elem in html_addresses]

with open(r'assets/coordinates_df.pkl', 'rb') as f:
    coordinates_df = pickle.load(f)

def pop_address(address):
    address_lst = address.split(',')
    return ','.join(address_lst[1:])
    
def get_coordinates(address):
    trial0 = 0
    trial1 = 0
    trial2 = 0
    location = None
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

for address in high_risk_addresses:
    if address in coordinates_df['address'].values:
        pass
    else:
        latitude, longitude = get_coordinates(address)
        coordinates_df = coordinates_df.append(
            pd.Series({
                'loc_id': coordinates_df['loc_id'].max() + 1,
                'address': address,
                'latitude': latitude,
                'longitude': longitude
            }),
            ignore_index=True
        )

with open(r'assets/coordinates_df.pkl', 'wb') as f:
    pickle.dump(coordinates_df,f)

#########################
## Plot Map
#########################

with open(r'assets/.mapbox_token', 'rb') as f:
    token = pickle.load(f)


px.set_mapbox_access_token(token)

fig = px.scatter_mapbox(
    coordinates_df, 
    lat="latitude", 
    lon="longitude",     
    hover_name = 'address',
    zoom=10,
    title=r'Coronovirus High Risk Areas',
    size=[1] * coordinates_df.shape[0],
    size_max=6,
    height=900
)

app.layout = html.Div([
    dcc.Graph(
        id='external-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)