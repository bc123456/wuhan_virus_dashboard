import sys
sys.path.insert(1, 'assets/src')
import os

import dash
import dash_table
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
import pytz
tz = pytz.timezone('Asia/Hong_Kong')

from wuhan_functions import pop_address, get_coordinates, get_infection_stats
from webscraper import fetch_stat, fetch_cases, fetch_awaiting_time

#########################
## Set up Dash
#########################

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server


#########################
## Get Data
#########################

# 1. Stats
try:
	stats_df = fetch_stat()
	with open(r'assets/data/STATS.pkl', 'wb') as f:
		pickle.dump(stats_df, f)
except Exception as e:
	print(e)
	print(f'Get stat data failed')
	with open(r'assets/data/STATS.pkl', 'rb') as f:
		stats_df = pickle.load(f)


death = stats_df.loc[0, 'Death']
confirmed = stats_df.loc[0, 'Confirmed']
investigating = stats_df.loc[0, 'Investigating']
reported = stats_df.loc[0, 'Reported']

# 2. Addresses

url = r'https://wars.vote4.hk/en/high-risk'
hk_latitude, hk_longitude = 22.2793278, 114.1628131
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

html_addresses = soup.find_all(
    'span', 
    class_=r'MuiTypography-root MuiTypography-h6 MuiTypography-colorTextPrimary'
)

high_risk_addresses = [job_elem.text + ', Hong Kong' for job_elem in html_addresses]

with open(r'assets/data/ADDRESS.pkl', 'rb') as f:
    address_df = pickle.load(f)


for address in high_risk_addresses:
    if address in address_df['address'].values:
        pass
    else:
        latitude, longitude = get_coordinates(address)
        address_df = address_df.append(
            pd.Series({
                'loc_id': address_df['loc_id'].max() + 1,
                'address': address,
                'latitude': latitude,
                'longitude': longitude
            }),
            ignore_index=True
        )

with open(r'assets/data/ADDRESS.pkl', 'wb') as f:
    pickle.dump(address_df,f)


# 3. Cases
try:
	cases_df = fetch_cases()
	with open(r'assets/data/CASES.pkl', 'wb') as f:
		pickle.dump(cases_df, f)
except Exception as e:
	print(e)
	print(f'Get cases data failed')
	with open(r'assets/data/CASES.pkl', 'rb') as f:
		cases_df = pickle.load(f)

# 4. Awaiting time
try:
	awaiting_df = fetch_awaiting_time()
	with open(r'assets/data/AWAITING.pkl', 'wb') as f:
		pickle.dump(awaiting_df, f)
except Exception as e:
	print(e)
	print(f'Get awaiting time data failed')
	with open(r'assets/data/AWAITING.pkl', 'rb') as f:
		awaiting_df = pickle.load(f)


#########################
## Plot Map
#########################

with open(r'assets/data/.mapbox_token', 'rb') as f:
    token = pickle.load(f)

px.set_mapbox_access_token(token)

fig = px.scatter_mapbox(
    address_df.dropna(),
    mapbox_style='satellite-streets',
    lat="latitude", 
    lon="longitude",     
    hover_name = 'address',
    zoom=10,
    title=r'High Risk Areas',
    size=[1] * address_df.shape[0],
    size_max=10,
    opacity=1,
    color_discrete_sequence=px.colors.cyclical.HSV,
    height=None
)
fig.update_layout(margin={'l': 0, 'r': 0, 'b': 0, 't': 0})

#########################
## Website Layout
#########################

app.layout = html.Div([
	dbc.Row([
		dbc.Col([
			html.H1(r'Wuhan Coronavirus Dashboard', style={'text-align': 'center'})
		])
	]),
	dbc.Row([
		dbc.Col([
			html.P(f'Last update: {datetime.datetime.now().strftime("%H:%M:%S")} (HKT)', style={'text-align': 'right'})
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
		dbc.Col(
			[
				dash_table.DataTable(
					data=cases_df[['gender', 'age', 'hospital', 'date']].to_dict('records'),
					columns=[{'id': c, 'name': c} for c in cases_df[['gender', 'age', 'hospital', 'date']].columns],
					# style_table={'overflowX': 'scroll'},
					style_cell={
						'fontSize':14, 
						'font-family': 'sans-serif', 
						'textAlign': 'left',
						# 'height': 'auto',
						'minWidth': '0px', 'maxWidth': '80px',
						# 'whiteSpace': 'normal',
						'textOverflow': 'ellipsis',
						'overflow': 'hidden'
					},
					style_as_list_view=True
				)
			], 
			width=4
		),
		dbc.Col(
			[
				dcc.Graph(
			        id='external-graph',
			        figure=fig
			    )
			], 
			width=8
		)
	]),
	dbc.Row([
		dbc.Col([
			html.H4(['A&E Waiting Time'])
		])
	]),
	dbc.Row([
		dbc.Col([
			dash_table.DataTable(
				id='table',
				columns=[{"name": i, "id": i} for i in awaiting_df.columns],
				data=awaiting_df.to_dict("rows"),
				style_cell={
					'fontSize': 14,
					'font-family': 'sans-serif',
				},
				style_as_list_view=True
		    )
		])
	])
])

if __name__ == '__main__':
    app.run_server(debug=True)