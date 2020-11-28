import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import State, Input, Output
from dash.exceptions import PreventUpdate
from dash import callback_context
import plotly.express as px
import pandas as pd
import yaml
from finance.client import Client  
from finance.client.data_classes.accounts import Account
from finance.client.data_classes.records import Record, RecordList
from finance.client.data_classes.labels import Label

from app import app

with open('config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

client = Client(db_path=config['database']['file_path']) 

accounts = client.accounts.list()
account_options = [{'label':account.name, 'value':account.id} for account in accounts]

country_codes = client._country_codes
country_code_options = [{'label':code, 'value': code} for code in country_codes]

labels = client.labels.list()
labels_options = [{'label':label.name, 'value':label.id} for label in labels]

currency_codes = client._currency_codes
currency_options = [{'label': code, 'value':code} for code in currency_codes]


### DATA STORE ###
records = client.records.list().to_pandas(currency=config['app']['default_currency'])

compiled_df = records.merge(
    accounts.to_pandas(), 
    how='left', 
    left_on='account_id', 
    right_on='id', 
    suffixes=('_record', '_account')
)

compiled_df = compiled_df.merge(
    labels.to_pandas(), 
    how='left', 
    left_on='label_id', 
    right_on='id', 
    suffixes=('_account', '_label')
)

initial_data_store = compiled_df.to_json()

data_store = dcc.Store(id='data-store', data=initial_data_store)

### ACCOUNT SELECTION ###
account_dropdown = dcc.Dropdown(
    id='account-dropdown',
    options=account_options, 
    multi=True, 
    className='mb-2',
    placeholder='Account'
)       

currency_dropdown = dcc.Dropdown(
    id='currency-dropdown',
    placeholder='Currency',
    className='mb-2',
    options=currency_options,
    value=config['app']['default_currency'],
    disabled=True
)

country_code_dropdown = dcc.Dropdown(
    id='country-code-dropdown',
    options=country_code_options, 
    multi=True, 
    className='mb-2',
    placeholder='Country'
)
    
label_dropdown = dcc.Dropdown(
    id='label-dropdown',
    options=labels_options, 
    multi=True, 
    className='mb-2',
    placeholder='Type')

date_range = dcc.DatePickerRange(
    id='date-picker-range', 
    className='mb-2'
)

filter_button = dbc.Button(
    'Show',
    id='filter-button',
    color='primary'
)

### SIDEBAR ###
side_bar = html.Div(
    [
        account_dropdown,
        currency_dropdown,
        country_code_dropdown,
        label_dropdown,
        date_range,
        filter_button
    ],
    style={'height':'100vh'}
)

### GRAPH ###
graph_type_selection = dbc.ButtonGroup(
    [
        dbc.Button("Plot", id='plot-graph-button', color='info'), 
        dbc.Button("Tree", id='tree-graph-button', color='info')
    ]
)

graph = dbc.Card(dcc.Loading(dcc.Graph(id='graph')))

### BODY ###
body = html.Div(
    dbc.Row(
        [
            dbc.Col(
                side_bar, 
                className='m-2',
                width=3),
            dbc.Col(
                [
                    dbc.Row(graph_type_selection, justify='end', className='mt-2'),
                    dbc.Row(dbc.Col(graph), className='mt-2')
                ], 
                className='mr-4'
            )
        ]
    )
)

### LAYOUT ###
layout = html.Div([body, data_store])

@app.callback(
    Output('graph', 'figure'),
    [Input('filter-button', 'n_clicks'),
     Input('plot-graph-button', 'n_clicks'),
     Input('tree-graph-button', 'n_clicks')],
    [State('data-store','data'),
     State('account-dropdown', 'value'),
     State('country-code-dropdown', 'value'),
     State('label-dropdown', 'value'),
     State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date')]
)
def update_graph(filter_click, plot_click, tree_click, 
                 data_store, account_ids, country_codes, label_ids, date_start, date_end):
    
    ctx = callback_context
    trigger_button = ctx.triggered[0]['prop_id'].split('.')[0]

    compiled_df = pd.read_json(data_store)

    graph_labels={
        'balance_USD':'Balance (USD)', 
        'name_account':'Account',
        'date':'Date'
    }

    if trigger_button == 'tree-graph-button':
        
        most_recent_records = compiled_df[['name_account', 'date']].groupby(['name_account'], as_index=False).max()
        current_balances = most_recent_records.merge(compiled_df, on=['name_account','date'], how='left')
        
        fig = px.treemap(
            current_balances,
            names='name_account',
            values='balance_USD',
            path=['name_label','name_account'],
            labels=graph_labels
        )

    else:
    
        fig = px.line(
            compiled_df,
            x='date',
            y='balance_USD',
            color='name_account',
            labels=graph_labels
        )
    
        fig.update_traces(mode='markers+lines')
        

    return fig

