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
from lib import create_total_col, compile_records

from app import app

with open('config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

client = Client(**config['database']) 

records = client.records.list()

accounts = client.accounts.list()
account_options = [{'label':account.name, 'value':account.id} for account in accounts]

country_codes = list(set([account.country_code for account in accounts]))
country_code_options = [{'label':code, 'value': code} for code in country_codes]

labels = client.labels.list()
labels_options = [{'label':label.name, 'value':label.id} for label in labels]

currency_codes = client._currency_codes
currency_options = [{'label': code, 'value':code} for code in currency_codes]

### RECORDS DATA STORE ###
compiled_records_df = compile_records(
    client=client,
    records=records.convert_currency(currency=config['app']['default_currency']).to_pandas(),
    accounts=accounts,
    labels=labels
)

initial_data_store = compiled_records_df.to_json()

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
    value=config['app']['default_currency']
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

clear_filter_button = dbc.Button(
    'Clear',
    id='clear-filter-button',
    color='light',
    className='ml-2'
)

### SIDEBAR ###
side_bar = html.Div(
    [
        account_dropdown,
        currency_dropdown,
        country_code_dropdown,
        label_dropdown,
        date_range,
        filter_button, 
        clear_filter_button
    ],
    style={'height':'100vh'}
)

### GRAPH ###
graph_type_selection = dbc.ButtonGroup(
    [
        dbc.Button("Plot", id='plot-graph-button', color='info'), 
        dbc.Button("Tree", id='tree-graph-button', color='info'),
        dbc.Button("Map", id='map-graph-button', color='info')
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
    [Output('account-dropdown', 'value'),
     Output('country-code-dropdown', 'value'),
     Output('label-dropdown', 'value'),
     Output('date-picker-range', 'start_date'),
     Output('date-picker-range', 'end_date'),
     Output('currency-dropdown', 'value')],
    [Input('clear-filter-button', 'n_clicks')],
)
def clear_filters(click):
    
    return None, None, None, None, None, config['app']['default_currency']

@app.callback(
    Output('graph', 'figure'),
    [Input('filter-button', 'n_clicks'),
     Input('plot-graph-button', 'n_clicks'),
     Input('plot-graph-button', 'n_clicks_timestamp'),
     Input('tree-graph-button', 'n_clicks'),
     Input('tree-graph-button', 'n_clicks_timestamp'),
     Input('map-graph-button', 'n_clicks'),
     Input('map-graph-button', 'n_clicks_timestamp')],
    [State('data-store','data'),
     State('account-dropdown', 'value'),
     State('country-code-dropdown', 'value'),
     State('label-dropdown', 'value'),
     State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('currency-dropdown', 'value')]
)
def update_graph(filter_click, plot_click, plot_timestamp, tree_click, tree_timestamp,
                 map_click, map_timestamp, data_store, account_ids, country_codes, 
                 label_ids, date_start, date_end, currency_code):
    
    ctx = callback_context
    trigger_button = ctx.triggered[0]['prop_id'].split('.')[0]

    compiled_df = pd.read_json(data_store)
    
    if account_ids:
        account_filter = compiled_df['account_id'].isin(account_ids)
    else:
        account_filter = pd.Series([True]*len(compiled_df))
        
    if country_codes:
        country_filter = compiled_df['country_code'].isin(country_codes)
    else:
        country_filter = pd.Series([True]*len(compiled_df))
        
    if label_ids:
        label_filter = compiled_df['label_id'].isin(label_ids)
    else:
        label_filter = pd.Series([True]*len(compiled_df))
        
    if date_start:
        start_filter = compiled_df['date'] > date_start
    else:
        start_filter = pd.Series([True]*len(compiled_df))
        
    if date_end:
        end_filter = compiled_df['date'] < date_end
    else:
        end_filter = pd.Series([True]*len(compiled_df))
        
    compiled_df = compiled_df[account_filter & country_filter & label_filter & start_filter & end_filter]        

    graph_labels={
        f'balance':f'Balance ({currency_code})', 
        'name_account':'Account',
        'date':'Date'
    }

    def create_treemap(compiled_df):
        
        most_recent_records = compiled_df[['name_account', 'date']].groupby(['name_account'], as_index=False).max()
        current_balances = most_recent_records.merge(compiled_df, on=['name_account','date'], how='left')
        
        fig = px.treemap(
            current_balances,
            names='name_account',
            values=f'balance',
            path=['name_label','name_account'],
            labels=graph_labels
        )
        
        return fig
    
    def create_plot(compiled_df):
        
        compiled_df = create_total_col(compiled_df, 'balance')
    
        fig = px.line(
            compiled_df.sort_values('date'),
            x='date',
            y=f'balance',
            color='name_account',
            labels=graph_labels,
        )
        
        fig.update_traces(mode='markers+lines')
        
        return fig    
    
    def create_map(compiled_df):
        
        comp
    
    if trigger_button == 'tree-graph-button':
        return create_treemap(compiled_df)
    
    elif trigger_button == 'filter-button':
        
        if tree_timestamp == None and plot_timestamp == None:
            return create_plot(compiled_df)
        
        elif tree_timestamp == None or plot_timestamp == None:
            if tree_timestamp:
                return create_treemap(compiled_df)
            else:
                return create_plot(compiled_df)
        
        elif tree_timestamp > plot_timestamp:
            return create_treemap(compiled_df)
        
        else:
            return create_plot(compiled_df)
        
    else:
        return create_plot(compiled_df)
    

@app.callback(
    Output('data-store','data'),
    [Input('currency-dropdown', 'value')],
)
def update_data_store_currency(currency):
    
    compiled_records_df = compile_records(
        client=client, 
        records=records.convert_currency(currency=currency).to_pandas(),
        accounts=accounts,
        labels=labels,
    )
    
    return compiled_records_df.to_json()
