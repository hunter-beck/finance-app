import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import State, Input, Output
from dash.exceptions import PreventUpdate
from dash import callback_context
import yaml
from finance.client import Client  
from finance.client.data_classes.accounts import Account
from finance.client.data_classes.records import Record
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

### ACCOUNT SELECTION ###
account_dropdown = dcc.Dropdown(
    options=account_options, 
    multi=True, 
    className='mb-2',
    placeholder='Account'
)       

country_code_dropdown = dcc.Dropdown(
    options=country_code_options, 
    multi=True, 
    className='mb-2',
    placeholder='Country'
)
    
label_dropdown = dcc.Dropdown(
    options=labels_options, 
    multi=True, 
    className='mb-2',
    placeholder='Type')

date_range = dcc.DatePickerRange(id='date-picker-range', className='mb-2')

label_filter_form = dbc.Form()

### SIDEBAR ###
side_bar = html.Div(
    [
        account_dropdown,
        country_code_dropdown,
        label_dropdown,
        date_range
    ],
    style={'height':'100vh'}
)

### BODY ###
body = html.Div(
    dbc.Row(
        [
            dbc.Col(
                side_bar, 
                className='m-2',
                width=3),
            dbc.Col(
                html.H1('BODY'), 
                className='mr-4'
            )
        ]
    )
)

### LAYOUT ###
layout = html.Div([body])