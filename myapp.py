import sys
sys.path.insert(1, 'src')
import os

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import pickle
import plotly.express as px
import pandas as pd

import numpy as np
import datetime
import pytz
tz = pytz.timezone('Asia/Hong_Kong')

from wuhan_functions import pop_address, get_coordinates, get_infection_stats, update_address
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

# 2. Addresses
with open(r'data/ADDRESS.pkl', 'rb') as f:
    address_df = pickle.load(f)

address_df = update_address(address_df)

with open(r'data/ADDRESS.pkl', 'wb') as f:
    pickle.dump(address_df,f)


# 3. Cases
try:
	cases_df = fetch_cases()
	with open(r'data/CASES.pkl', 'wb') as f:
		pickle.dump(cases_df, f)
except Exception as e:
	print(e)
	print(f'Get cases data failed')
	with open(r'data/CASES.pkl', 'rb') as f:
		cases_df = pickle.load(f)

# 4. Awaiting time
try:
	awaiting_df = fetch_awaiting_time()
	with open(r'data/AWAITING.pkl', 'wb') as f:
		pickle.dump(awaiting_df, f)
except Exception as e:
	print(e)
	print(f'Get awaiting time data failed')
	with open(r'data/AWAITING.pkl', 'rb') as f:
		awaiting_df = pickle.load(f)


#########################
## Plot Map
#########################


def plot_map(address_df):
	'''
	Plot the map with labels showing the hospitals and high risk areas

	'''

	with open(r'data/.mapbox_token', 'rb') as f:
	    token = pickle.load(f)

	px.set_mapbox_access_token(token)

	map_df = address_df.copy()


	fig = px.scatter_mapbox(
	    map_df.dropna(),
	    mapbox_style='light',
	    lat="latitude", 
	    lon="longitude",     
	    hover_name = 'address',
	    zoom=10,
	    # title=r'High Risk Areas',
	    size=[1] * map_df.dropna().shape[0],
	    size_max=9,
	    opacity=0.9,
	    color='category',
	    color_discrete_sequence=px.colors.sequential.Bluered[::-1],
	    height=540
	)
	fig.update_layout(margin={'l': 0, 'r': 0, 'b': 0, 't': 0})

	return fig


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
			html.P(f'Last update: {datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z%z")}', style={'text-align': 'right'})
		])
	]),
	dbc.Row(id='live-update-stats'),
	dbc.Row([
		dbc.Col(
			[
				html.H4(['Confirmed Cases']),
			],
			width=4
		),
		dbc.Col(
			[
				html.H4(['High Risk Areas']),
			],
			width=8
		)
	]),
	dbc.Row([
		dbc.Col(
			[
				dash_table.DataTable(
					data=cases_df[['casenum', 'gender', 'age', 'hospital', 'date']].to_dict('records'),
					columns=[{'id': c, 'name': c} for c in cases_df[['casenum', 'gender', 'age', 'hospital', 'date']].columns],
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
			        figure=plot_map(address_df)
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
	]),
	dcc.Interval(
        id='interval-component',
        interval=60*1000, # in milliseconds
        n_intervals=0
    )
])

#########################
## Live Components
#########################

@app.callback(
	Output('live-update-stats', 'children'),
	[Input('interval-component', 'n_intervals')]
)
def update_stats_cards(n):
	'''
	Return a list of four dbc.Col() objects. Corresponding to the number of Deaths, Confirmed, Investigating and Reported
	'''
	# Get stats data

	# 1. Stats
	try:
		stats_df = fetch_stat()
		with open(r'data/STATS.pkl', 'wb') as f:
			pickle.dump(stats_df, f)
	except Exception as e:
		print(e)
		print(f'Get stat data failed')
		with open(r'data/STATS.pkl', 'rb') as f:
			stats_df = pickle.load(f)


	death = stats_df.loc[0, 'Death']
	confirmed = stats_df.loc[0, 'Confirmed']
	investigating = stats_df.loc[0, 'Investigating']
	reported = stats_df.loc[0, 'Reported']

	return [
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
	]

if __name__ == '__main__':
    app.run_server(
    	debug=True,
    	dev_tools_hot_reload_watch_interval=3
    )