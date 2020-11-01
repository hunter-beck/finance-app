import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import State, Input, Output
from dash.exceptions import PreventUpdate
from dash import callback_context
import yaml
from finance.client import Client  

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

### CREATE POPUP ###
create_button = dbc.Button("Create", id='create-button', color='info')

create_name_input = dbc.FormGroup(
    [
        dbc.Label("Name"),
        dbc.Input(id='create-name-input', placeholder='Name')
    ],
)

create_description_input = dbc.FormGroup(
    [
        dbc.Label("Description"),
        dbc.Input(id='create-description-input', placeholder='Description')
    ]
)

create_balance_input = dbc.FormGroup(
    [
        dbc.Label("Balance"),
        dbc.Input(id='create-balance-input', placeholder='Balance')
    ]
)

create_account_dropdown = dbc.FormGroup(
    [
        dbc.Label("Account"),
        dcc.Dropdown(
            id='create-account-dropdown',
            placeholder='Account',
            options=account_options
        )
    ]
)

create_label_dropdown = dbc.FormGroup(
    [
        dbc.Label("Label"),
        dcc.Dropdown(
            id='create-label-dropdown',
            placeholder='Label',
            options=labels_options
        )
    ]
)

create_currency_dropdown = dbc.FormGroup(
    [
        dbc.Label("Currency"),
        dcc.Dropdown(
            id='create-currency-dropdown',
            placeholder='Currency',
            options=currency_options
        )
    ]
)

create_country_dropdown = dbc.FormGroup(
    [
        dbc.Label("Country"),
        dcc.Dropdown(
            id='create-country-dropdown',
            placeholder='Country',
            options=country_code_options
        )
    ]
)

account_create_form = dbc.Form([
    create_name_input,
    create_description_input,
    create_label_dropdown,
    create_country_dropdown
])

label_create_form = dbc.Form([
    create_name_input,
    create_description_input
])

record_create_form = dbc.Form([
    create_account_dropdown,
    create_balance_input,
    create_currency_dropdown
])

create_modal = dbc.Modal(
    [
        dbc.ModalBody(html.Div(id='create-modal-content')),
        dbc.ModalFooter(
            dbc.Button(
                "Close", id="close-create-modal", className="ml-auto"
            )
        ),
    ],
    id="create-modal",
    centered=True,
)


### BODY ###
body = html.Div(
    dbc.Row(
        [
            dbc.Col(side_bar, width=3),
            dbc.Col(
                [
                    dbc.Row(
                        create_button,
                        justify='end',
                        className='mt-2'
                    ),
                    dbc.Row(
                        dbc.Col(table_placeholder),
                        className='mt-2')
                ], 
                className='mr-4'
            )
        ]
    )
)

### DATA TYPE STORE ###
data_type_store = dcc.Store(id='data-type-store')

### LAYOUT ###
explore_app_layout = html.Div([data_type_store, create_modal, body])

### CALLBACKS ###
@app.callback(
    [Output('table-content', 'children'),
     Output('sidebar-content', 'children'),
     Output('data-type-store', 'data')],
    [Input('accounts-button', 'n_clicks'),
     Input('records-button', 'n_clicks'),
     Input('labels-button', 'n_clicks')]
)
def accounts_selection(account_n, record_n, label_n):
    ctx = callback_context
    trigger_button = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_button == 'accounts-button':
        return accounts_table, account_filter_form, 'accounts'
    elif trigger_button == 'records-button':
        return records_table, record_filter_form, 'records'
    elif trigger_button == 'labels-button':
        return labels_table, label_filter_form, 'labels'
    else:
        raise PreventUpdate

@app.callback(
    [Output("create-modal", "is_open"),
     Output('create-modal-content', 'children')],
    [Input('create-button', 'n_clicks'),
     Input("close-create-modal", "n_clicks")],
    [State("create-modal", "is_open"),
     State('data-type-store', 'data')],
)
def close_modal(create_n, close_n, is_open, data_type_store):
    
    if data_type_store == 'accounts':
        return not is_open, account_create_form
    elif data_type_store == 'labels':
        return not is_open, label_create_form
    elif data_type_store == 'records':
        return not is_open, record_create_form
    else:
        raise PreventUpdate