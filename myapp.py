import sys
sys.path.insert(1, 'assets/src')
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import pickle
import plotly.express as px
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import datetime

from wuhan_functions import pop_address, get_coordinates, get_infection_stats

#########################
## Set up Dash
#########################

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server


#########################
## Get Data
#########################

death, confirmed, investigating, reported = get_infection_stats(r'assets/data/infection_stats.pkl')

url = r'https://wars.vote4.hk/en/high-risk'
hk_latitude, hk_longitude = 22.2793278, 114.1628131
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

html_addresses = soup.find_all(
    'span', 
    class_=r'MuiTypography-root MuiTypography-h6 MuiTypography-colorTextPrimary'
)

high_risk_addresses = [job_elem.text + ', Hong Kong' for job_elem in html_addresses]

with open(r'assets/data/coordinates_df.pkl', 'rb') as f:
    coordinates_df = pickle.load(f)


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

with open(r'assets/data/coordinates_df.pkl', 'wb') as f:
    pickle.dump(coordinates_df,f)

#########################
## Plot Map
#########################

with open(r'assets/data/.mapbox_token', 'rb') as f:
    token = pickle.load(f)


px.set_mapbox_access_token(token)

fig = px.scatter_mapbox(
    coordinates_df.dropna(), 
    lat="latitude", 
    lon="longitude",     
    hover_name = 'address',
    zoom=10,
    title=r'High Risk Areas',
    size=[1] * coordinates_df.shape[0],
    size_max=15,
    height=600
)

app.layout = html.Div([
	dbc.Row([
		dbc.Col([
			html.H1(r'Wuhan Coronavirus Dashboard', style={'text-align': 'center'})
		])
	]),
	dbc.Row([
		dbc.Col([
			html.P(f'Last update: {datetime.datetime.now().strftime("%H:%M:%S")}', style={'text-align': 'right'})
		])
	]),
	dbc.Row([
		dbc.Col(
			[
				html.Div(
					[html.H3(death), html.P('Death')],
					className='mini_container'
				)
			]
		),
		dbc.Col(
			[
				html.Div(
					[html.H3(confirmed), html.P('Confirmed')],
					className='mini_container'
				)
			]
		),
		dbc.Col(
			[
				html.Div(
					[html.H3(investigating), html.P('Investigating')],
					className='mini_container'
				)
			]
		),
		dbc.Col(
			[
				html.Div(
					[html.H3(reported), html.P('Reported')],
					className='mini_container'
				)
			]
		),
	]),
	dbc.Row([
		dbc.Col([], width=4),
		dbc.Col(
			[
				dcc.Graph(
			        id='external-graph',
			        figure=fig
			    )
			], 
			width=8
		)
	])
])

if __name__ == '__main__':
    app.run_server(debug=True)