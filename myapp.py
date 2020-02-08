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
import plotly.graph_objects as go
import pandas as pd

import numpy as np
import datetime
import pytz
tz = pytz.timezone('Asia/Hong_Kong')

from wuhan_functions import pop_address, get_coordinates, update_address
from webscraper import fetch_stat, fetch_cases, fetch_awaiting_time, fetch_highrisk

#########################
## Update data with the data source?
#########################
update = True

if update:
	print('Pulling data online.')
else:
	print('Using old data from local')

#########################
## Get mapbox token (needed for some map designs)
#########################
with open(r'data/.mapbox_token', 'rb') as f:
    token = pickle.load(f)

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

with open(r'data/HIGH_RISK.pkl', 'rb') as f:
	high_risk_df = pickle.load(f)


if update:
	# update the high risk location data
	try:
		high_risk_df = fetch_highrisk()
		with open(r'data/HIGH_RISK.pkl', 'wb') as f:
			pickle.dump(high_risk_df, f)
	except Exception as e:
		print(e)
		print('Get new high risk location failed.')
	# update the new address with coordinates
	try:
		address_df = update_address(address_df, high_risk_df)
		with open(r'data/ADDRESS.pkl', 'wb') as f:
			pickle.dump(address_df, f)
	except Exception as e:
		print(e)
		print('Update address coordinates failed.')

high_risk_with_coordinates_df = pd.merge(
	high_risk_df,
	address_df[['id', 'latitude', 'longitude']],
	how='left',
	left_on='id',
	right_on='id'
).dropna()

# 3. Cases

with open(r'data/CASES.pkl', 'rb') as f:
	cases_df = pickle.load(f)

if update:
	try:
		cases_df = fetch_cases()
		with open(r'data/CASES.pkl', 'wb') as f:
			pickle.dump(cases_df, f)
	except Exception as e:
		print(e)
		print(f'Get cases data failed')

# 4. Hospital Awaiting time

with open(r'data/HOSPITALS.pkl', 'rb') as f:
	hospital_df = pickle.load(f)

with open(r'data/AWAITING.pkl', 'rb') as f:
	awaiting_df = pickle.load(f)

if update:
	try:
		awaiting_df = fetch_awaiting_time()
		with open(r'data/AWAITING.pkl', 'wb') as f:
			pickle.dump(awaiting_df, f)
	except Exception as e:
		print(e)
		print(f'Get awaiting time data failed')
	
hospital_awaiting_df = pd.merge(
	hospital_df[['address', 'latitude', 'longitude']],
	awaiting_df[['name_en', 'topWait', 'topWait_value']],
	how='left',
	left_on='address',
	right_on='name_en'
)

#########################
## Website Layout
#########################

# plot figure (move out of the function to allow faster figure refresh)

fig = go.Figure()

fig.update_layout(
	autosize=True,
	hovermode='closest',
	showlegend=True,
	mapbox=go.layout.Mapbox(
		accesstoken=token,
		bearing=0,
		center=go.layout.mapbox.Center(
			lat=22.302711,
			lon=114.177216
		),
		pitch=0,
		zoom=10,
		style='light',
	),
	height=740,
	margin={'l': 0, 'r': 0, 'b': 0, 't': 0},
	legend_orientation="h",
	legend_title='',
	legend=dict(x=.02, y=0.98)
)


# website layout

app.layout = html.Div([
	dbc.Row([
		dbc.Col(
			[
				html.Img(src=app.get_asset_url(r'fti_logo.png'), id='fti_logo', style={"height": '60px'})
			],
			width=3
		),
		dbc.Col(
			[
				html.H1('Wuhan Coronavirus Dashboard', style={'text-align': 'center'}),
				html.P('created for demonstration purpose only', style={'text-align': 'center'})
			],
			width=6
		),
		dbc.Col(
			[
				html.P(f'Last update: {datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z%z")}', style={'text-align': 'right'})
			],
			width=3
		)
	]),
	dbc.Row(id='live-update-stats'),
	dbc.Row([
		dbc.Col(
			[
				dcc.Graph(
			        id='interactive-map'
			    ),
			    html.Div(
			    	[
			    		html.H4('New Cases'),
			    		dcc.Dropdown(
			    			id='case-drop-down',
							options=[
								{
									'label': f'#{row.case_no}: Age {row.age} {row.gender}, {row.type_en} {row.status}', 
									'value': row.case_no
								} for idx, row in cases_df.sort_values(by='case_no', ascending=False).iterrows()
							],
							value=cases_df['case_no'].max()
						),
						html.Div(id='case-description')
			    	], 
			    	className='mini_container'
			    ),
			], 
			width=8
		),
		dbc.Col(
			[
				html.Div(
					[
						dcc.Checklist(
							id='high-risk-hospitals',
						    options=[
						        {'label': 'High Risk Area   ', 'value': 'show-high-risk'},
						        {'label': 'Hospitals   ', 'value': 'show-hospitals'}
						    ],
						    value=['show-high-risk', 'show-hospitals'],
						    labelStyle={'display': 'inline-block'}
						),
						html.P('Filter hospitals by A&E waiting time: '),
						dcc.RangeSlider(
							id='waiting-time-slider',
							marks={i: f'> {i} hr' for i in range(0, awaiting_df['topWait_value'].max() + 1)},
							min=0,
							max=awaiting_df['topWait_value'].max(),
							value=[0, 0]
						),
						html.P('Filter high risk areas by dates: '),
						dcc.DatePickerRange(
							id='date-filter',
							start_date=datetime.datetime(2020, 1, 10),
							end_date=datetime.datetime.today()
						),
						html.P('Filter by districts: '),
						dcc.Dropdown(
							id='district-filter',
							options=[
								{'label': district, 'value': district} for district in sorted(high_risk_df['sub_district_en'].unique())
							],
							multi=True,
							value=sorted(high_risk_df['sub_district_en'].unique())
						)
					],
					className="pretty_container four columns"
				)
			], 
			width=4
		),
	]),
	html.Footer('This website and its contents herein, including all data, mapping, and analysis (“Website”), is provided for educational purpose internally within FTI Consulting, Inc. (FTI).  The Website relies upon publicly available data from multiple sources, that do not always agree. FTI hereby disclaims any and all representations and warranties with respect to the Website, including accuracy, fitness for use, and merchantability.  Reliance on the Website for medical guidance or use of the Website in commerce is strictly prohibited.'),
	dcc.Interval(
        id='interval-component',
        interval=60*1000, # in milliseconds
        n_intervals=0
    )
])

#########################
## Live Components
#########################

# Plot Map
@app.callback(
	Output('interactive-map', 'figure'),
	[
		Input('high-risk-hospitals', 'value'),
		Input('waiting-time-slider', 'value'),
		Input('district-filter', 'value'),
		Input('date-filter', 'start_date'),
		Input('date-filter', 'end_date')
	]
)
def plot_map(high_risk_hospitals, waiting_time_slider, district_filter, start_date, end_date):
	'''
	Plot the map with labels showing the hospitals and high risk areas

	'''


	# slider component to show relevant hospitals
	waiting_time_min = waiting_time_slider[0]
	waiting_time_max = waiting_time_slider[1]

	is_within_waiting_time = (
		(hospital_awaiting_df['topWait_value'] >= waiting_time_min) &
		(hospital_awaiting_df['topWait_value'] <= waiting_time_max)
	)

	# date filter components
	# the record is considered not within date range if:
	# 1. the start date is later than the specified end_date, or
	# 2. the end date is earlier than the specified start_date.
	is_within_date = ~(
		(high_risk_with_coordinates_df['start_date'] > end_date) |
		(high_risk_with_coordinates_df['end_date'] < start_date)
	)

	# district filter components
	is_within_district = high_risk_with_coordinates_df['sub_district_en'].isin(district_filter)

	
	# Establich masks to mask irrelevant dots
	# records to show are labeled with 1, records not to show are marked with 0
	hospital_awaiting_masks = (
		is_within_waiting_time
	)

	# records to show are labeled with 1, records not to show are marked with 0
	high_risk_with_coordinates_masks = (
		is_within_district &
		is_within_date
	)

	# Apply masks to highlight points
	hospital_awaiting_sharp_df = hospital_awaiting_df[hospital_awaiting_masks]
	hospital_awaiting_fade_df = hospital_awaiting_df[~hospital_awaiting_masks]

	high_risk_with_coordinates_sharp_df = high_risk_with_coordinates_df[high_risk_with_coordinates_masks]
	high_risk_with_coordinates_fade_df = high_risk_with_coordinates_df[~high_risk_with_coordinates_masks]



	# Plot the map


	fig.data = []  # clear all scatter dots before refreshing
	

	if 'show-high-risk' in high_risk_hospitals:
		fig.add_trace(go.Scattermapbox(
			lat=high_risk_with_coordinates_sharp_df['latitude'],
			lon=high_risk_with_coordinates_sharp_df['longitude'],
			mode='markers',
			marker=go.scattermapbox.Marker(
				size=10,
				color='rgb(255, 0, 0)',
				opacity=0.9,
				symbol='circle'
			),
			text=(
				high_risk_with_coordinates_sharp_df['location_en'] + '<br>' + 
				high_risk_with_coordinates_sharp_df['sub_district_en'] + '<br>' + 
				high_risk_with_coordinates_sharp_df['start_date'].dt.strftime("%Y-%m-%d") + ' - ' + high_risk_with_coordinates_sharp_df['end_date'].dt.strftime("%Y-%m-%d")
			),
			hoverinfo='text',
			name='High Risk Area (selected)'
		))

		fig.add_trace(go.Scattermapbox(
			lat=high_risk_with_coordinates_fade_df['latitude'],
			lon=high_risk_with_coordinates_fade_df['longitude'],
			mode='markers',
			marker=go.scattermapbox.Marker(
				size=7,
				color='rgb(255, 0, 0)',
				opacity=0.2,
				symbol='circle'
			),
			text=(
				high_risk_with_coordinates_fade_df['location_en'] + '<br>' + 
				high_risk_with_coordinates_fade_df['sub_district_en'] + '<br>' + 
				high_risk_with_coordinates_fade_df['start_date'].dt.strftime("%Y-%m-%d") + ' - ' + high_risk_with_coordinates_fade_df['end_date'].dt.strftime("%Y-%m-%d")
			),
			hoverinfo='text',
			name='High Risk Area (not selected)'
		))

	if 'show-hospitals' in high_risk_hospitals:
		fig.add_trace(go.Scattermapbox(
			lat=hospital_awaiting_sharp_df['latitude'],
			lon=hospital_awaiting_sharp_df['longitude'],
			mode='markers',
			marker=go.scattermapbox.Marker(
				size=10,
				color='rgb(0, 0, 255)',
				opacity=0.9,
				symbol='circle'
			),
			text='<b>' + hospital_awaiting_sharp_df['address'] + '</b><br>Waiting time: ' + hospital_awaiting_sharp_df['topWait'] + ' hours',
			hoverinfo='text',
			name='Hospitals (selected)'
		))
		fig.add_trace(go.Scattermapbox(
			lat=hospital_awaiting_fade_df['latitude'],
			lon=hospital_awaiting_fade_df['longitude'],
			mode='markers',
			marker=go.scattermapbox.Marker(
				size=7,
				color='rgb(0, 0, 255)',
				opacity=0.2,
				symbol='circle'
			),
			text=hospital_awaiting_fade_df['address'] + ':\n Waiting time: ' + hospital_awaiting_fade_df['topWait'] + ' hours',
			hoverinfo='text',
			name='Hospitals (not selected)'
		))
	
	

	return fig

# print the case description

@app.callback(
    Output(component_id='case-description', component_property='children'),
    [Input(component_id='case-drop-down', component_property='value')]
)
def update_case_description(case_no):
	selected_case = cases_df[cases_df['case_no'] == case_no].iloc[0].to_dict()
	output = [
		html.Hr(),
		html.P(f'#{selected_case["case_no"]} ({selected_case["status"]})'),
		html.H5(f'Age {selected_case["age"]} {selected_case["gender"]}'),
		html.P([
			html.Span('Confirmed date: '), 
			html.Strong(selected_case["confirmation_date"])
		]),
		html.P([
			html.Span('Place of residence: '), 
			html.Strong(selected_case["citizenship_en"])
		]),
		html.P([
			html.Span('Hospital admitted: '), 
			html.Strong(selected_case["hospital_en"])
		]),
		html.Hr(),
		html.P(selected_case["detail_en"])
	]
	return output


# top stats bar (live update every minute)
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
	with open(r'data/STATS.pkl', 'rb') as f:
		stats_df = pickle.load(f)

	if update:
		try:
			stats_df = fetch_stat()
			with open(r'data/STATS.pkl', 'wb') as f:
				pickle.dump(stats_df, f)
		except Exception as e:
			print(e)
			print(f'Get stat data failed')
		


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