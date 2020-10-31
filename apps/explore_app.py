import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import State, Input, Output
from dash import callback_context
import yaml
from finance.client import Client  

from app import app

with open('config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

client = Client(db_path=config['database']['file_path']) 

### DATA TYPE SELECTOR ###
data_type_buttons = dbc.ButtonGroup(
    [
        dbc.Button('Accounts', id='accounts-button'),
        dbc.Button('Records', id='records-button'),
        dbc.Button('Labels', id='labels-button')
    ],
    className='mb-3'
)

### ACCOUNT SELECTION ###
accounts = client.accounts.list()
account_options = [{'label':account.name, 'value':account.id} for account in accounts]
account_dropdown = dcc.Dropdown(
    options=account_options, 
    multi=True, 
    className='mb-2',
    placeholder='Account'
)       

country_codes = [account.country_code for account in accounts]
country_codes = list(set(country_codes))
country_code_options = [{'label':code, 'value': code} for code in country_codes]
country_code_dropdown = dcc.Dropdown(
    options=country_code_options, 
    multi=True, 
    className='mb-2',
    placeholder='Country'
)
    
labels = client.labels.list()
labels_options = [{'label':label.name, 'value':label.id} for label in labels]
label_dropdown = dcc.Dropdown(
    options=labels_options, 
    multi=True, 
    className='mb-2',
    placeholder='Type')

date_range = dcc.DatePickerRange(id='date-picker-range', className='mb-2')

account_filter_form = dbc.Form(
    [
        account_dropdown,
        label_dropdown, 
        country_code_dropdown,
    ]
)

record_filter_form = dbc.Form(
    [
        account_dropdown,
        date_range,
        label_dropdown, 
    ]
)

label_filter_form = dbc.Form()

### SIDEBAR ###
side_bar = dbc.Card(
    [
        dbc.CardBody(
            [
                data_type_buttons,
                html.Div(id='sidebar-content')
            ]
        ),
    ],
    style={'height':'100vh'}
)

### TABLE ###
records_df = client.records.list().to_pandas()

table_placeholder = html.Div(id='table-content', className='mt-3')

TABLE_STYLE = {
    'style_as_list_view':True,
    'style_header':{'backgroundColor': 'rgb(30, 30, 30)'},
    'style_cell':{
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white'
    },
    'page_size':20
}

accounts_df = client.accounts.list().to_pandas()
accounts_table = dash_table.DataTable(
    data=accounts_df.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in accounts_df.columns],
    **TABLE_STYLE,
)

records_df = client.records.list().to_pandas()
records_table = dash_table.DataTable(
    data=records_df.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in records_df.columns],
    **TABLE_STYLE,
)

labels_df = client.labels.list().to_pandas()
labels_table = dash_table.DataTable(
    data=labels_df.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in labels_df.columns],
    **TABLE_STYLE,
)

### BODY ###
body = html.Div(
    dbc.Row(
        [
            dbc.Col(side_bar, width=3),
            dbc.Col(table_placeholder, className='mr-4')
        ]
    )
)

### LAYOUT ###
explore_app_layout = html.Div([body])

### CALLBACKS ###
@app.callback(
    [Output('table-content', 'children'),
     Output('sidebar-content', 'children')],
    [Input('accounts-button', 'n_clicks'),
     Input('records-button', 'n_clicks'),
     Input('labels-button', 'n_clicks')]
)
def accounts_selection(account_n, record_n, label_n):
    ctx = callback_context
    trigger_button = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_button == 'accounts-button':
        return accounts_table, account_filter_form
    elif trigger_button == 'records-button':
        return records_table, record_filter_form
    elif trigger_button == 'labels-button':
        return labels_table, label_filter_form

