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

with open(r'assets/coordinates_df.pkl', 'rb') as f:
    coordinates_df = pickle.load(f)


with open(r'assets/.mapbox_token', 'rb') as f:
    token = pickle.load(f)


px.set_mapbox_access_token(token)

fig = px.scatter_mapbox(
    coordinates_df, 
    lat="latitude", 
    lon="longitude",     
    hover_name = 'address',
    zoom=9,
    title=r'Coronovirus High Risk Areas')

app.layout = html.Div([
    dcc.Graph(
        id='external-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)