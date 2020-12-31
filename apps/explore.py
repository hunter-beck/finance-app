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
import pandas as pd
from operator import itemgetter 
import json

from app import app

with open('config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

client = Client(**config['database']) 

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
side_bar = html.Div(
    [
        data_type_buttons,
        html.Div(id='sidebar-content')
    ],
    style={'height':'100vh'}
)

### TABLE ###
records_df = client.records.list().to_pandas()

table_placeholder = dash_table.DataTable(
    id='view-table',
    style_as_list_view=True,
    page_size=20,
    row_selectable='multi'
)

### MODAL STYLING ###
MODAL_CREATE_BUTTON_STYLE = {
    'className':"mr-2",
    'color':'primary'
}

MODAL_DELETE_BUTTON_STYLE = {
    'className':"mr-2",
    'color':'danger'
}

MODAL_CLOSE_BUTTON_STYLE = {
    'className':"mr-2",
    'color':'secondary'
}

### CREATE MODALS ###

create_button = dbc.Button("Create", id='create-button', color='info', className='mr-2')

create_account_name_input = dbc.FormGroup(
    [
        dbc.Label("Name"),
        dbc.Input(id='create-account-name-input', placeholder='Name', type='text', debounce=True)
    ],
)

create_account_description_input = dbc.FormGroup(
    [
        dbc.Label("Description"),
        dbc.Input(id='create-account-description-input', placeholder='Description')
    ]
)

create_account_label_dropdown = dbc.FormGroup(
    [
        dbc.Label("Label"),
        dcc.Dropdown(
            id='create-account-label-dropdown',
            placeholder='Label',
            options=labels_options
        )
    ]
)

create_account_country_dropdown = dbc.FormGroup(
    [
        dbc.Label("Country"),
        dcc.Dropdown(
            id='create-account-country-dropdown',
            placeholder='Country',
            options=country_code_options
        )
    ]
)

create_account_modal = dbc.Modal(
    [
        dbc.ModalBody(
            dbc.Form([
                create_account_name_input,
                create_account_description_input,
                create_account_label_dropdown,
                create_account_country_dropdown
            ])
        ),
        dbc.ModalFooter(
            [   
                dbc.Button(
                    "Create", id="create-accounts-button", **MODAL_CREATE_BUTTON_STYLE
                )
            ]
        ),
    ],
    id="create-account-modal",
    centered=True,
)

create_label_name_input = dbc.FormGroup(
    [
        dbc.Label("Name"),
        dbc.Input(id='create-label-name-input', placeholder='Name', type='text', debounce=True)
    ],
)

create_label_description_input = dbc.FormGroup(
    [
        dbc.Label("Description"),
        dbc.Input(id='create-label-description-input', placeholder='Description')
    ]
)

create_label_modal = dbc.Modal(
    [
        dbc.ModalBody(
            dbc.Form([
                create_label_name_input,
                create_label_description_input
            ])
        ),
        dbc.ModalFooter(
            [   
                dbc.Button(
                    "Create", id="create-labels-button", **MODAL_CREATE_BUTTON_STYLE
                )
            ]
        ),
    ],
    id="create-label-modal",
    centered=True,
)

create_record_account_dropdown = dbc.FormGroup(
    [
        dbc.Label("Account"),
        dcc.Dropdown(
            id='create-record-account-dropdown',
            placeholder='Account',
            options=account_options
        )
    ]
)

create_record_currency_dropdown = dbc.FormGroup(
    [
        dbc.Label("Currency"),
        dcc.Dropdown(
            id='create-record-currency-dropdown',
            placeholder='Currency',
            options=currency_options
        )
    ]
)

create_record_balance_input = dbc.FormGroup(
    [
        dbc.Label("Balance"),
        dbc.Input(id='create-record-balance-input', placeholder='Balance')
    ]
)

create_record_date_input = dbc.FormGroup(
    [
        dbc.Label("Date"),
        dcc.DatePickerSingle(id='create-record-date-input', placeholder='Date')
    ]
)

create_record_modal = dbc.Modal(
    [
        dbc.ModalBody(
            dbc.Form([
                create_record_account_dropdown,
                create_record_balance_input,
                create_record_currency_dropdown,
                create_record_date_input
            ])
        ),
        dbc.ModalFooter(
            [   
                dbc.Button(
                    "Create", id="create-records-button", **MODAL_CREATE_BUTTON_STYLE
                )
            ]
        ),
    ],
    id="create-record-modal",
    centered=True,
)

### DELETE MODALS

delete_button = dbc.Button("Delete", id='delete-button', color='danger')

delete_table = dash_table.DataTable(
    id='delete-table',
    style_as_list_view=True,
    page_size=5,
    row_selectable='multi'
)

delete_modal = dbc.Modal(
    [
        dbc.ModalBody(
            [
                html.Div('Confirm deletion of the following items:', className='mb-2'),
                delete_table
            ],
            className='m-2'
        ),
        dbc.ModalFooter(
            [   
                dbc.Button(
                    "Delete", id="confirm-delete-button", **MODAL_CREATE_BUTTON_STYLE
                )
            ]
        ),
    ],
    id="delete-modal",
    centered=True,
)

delete_not_selected_alert = dbc.Alert(
    "No items selected for deletion. Check boxes below.", 
    id='delete-alert', 
    color="warning",
    duration=10000,
    dismissable=True,
    className='m-2',
    is_open=False
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
                [
                    dbc.Row(
                        [create_button, delete_button],
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
temp_val_store = dcc.Store(id='temp-val-store')
data_type_store = dcc.Store(id='data-type-store')


### LAYOUT ###
layout = html.Div([
    data_type_store,
    create_account_modal, create_label_modal, create_record_modal, delete_modal,
    delete_not_selected_alert,
    body
])

### CALLBACKS ###
@app.callback(
    [Output("create-account-modal", "is_open"),
     Output("create-label-modal", "is_open"),
     Output("create-record-modal", "is_open"),
     Output("master-records-store","data"),
     Output("master-labels-store","data"),
     Output("master-accounts-store","data")],
    [Input('create-button', 'n_clicks'),
     Input("create-accounts-button", "n_clicks"),
     Input("create-labels-button", "n_clicks"),
     Input("create-records-button", "n_clicks")],
    [State('data-type-store', 'data'),
     State("create-account-modal", "is_open"),
     State("create-label-modal", "is_open"),
     State("create-record-modal", "is_open"),
     State('create-account-name-input', 'value'),
     State('create-account-description-input', 'value'),
     State('create-account-label-dropdown', 'value'),
     State('create-account-country-dropdown', 'value'),
     State('create-label-name-input', 'value'),
     State('create-label-description-input', 'value'),
     State('create-record-account-dropdown', 'value'),
     State('create-record-balance-input', 'value'),
     State('create-record-currency-dropdown', 'value'),
     State('create-record-date-input', 'date'),
     State("master-records-store","data"),
     State("master-labels-store","data"),
     State("master-accounts-store","data")]
)
def createModal(create_n, create_account_n, create_label_n, create_record_n,
                data_type_store, account_is_open, label_is_open, record_is_open,
                account_name, account_description, account_label, account_country, 
                label_name, label_description,
                record_account, record_balance, record_currency, record_date,
                current_records_store, current_labels_store, current_accounts_store):
    
    ctx = callback_context
    trigger_button = ctx.triggered[0]['prop_id'].split('.')[0]

    if data_type_store == 'accounts':
        updated_accounts = current_accounts_store
        
        if trigger_button == 'create-accounts-button':
            new_account = Account(
                name=account_name,
                label_id=account_label,
                country_code=account_country
            )
            client.accounts.create([new_account])
            
            updated_accounts = client.accounts.list().to_pandas().to_json()
            
        return not account_is_open, label_is_open, record_is_open, \
            current_records_store, current_labels_store, updated_accounts
    
    elif data_type_store == 'labels':
        updated_labels = current_labels_store
        
        if trigger_button == 'create-labels-button':
            new_label = Label(
                name=label_name,
                description=label_description,
            )
            client.labels.create([new_label])
            
            updated_labels = client.labels.list().to_pandas().to_json()
            
        return account_is_open, not label_is_open, record_is_open, \
            current_records_store, updated_labels, current_accounts_store
    
    elif data_type_store == 'records':
        updated_records = current_records_store
        
        if trigger_button == 'create-records-button':
            new_record = Record(
                account_id=record_account,
                currency=record_currency,
                balance=record_balance,
                date=record_date
            )
            client.records.create([new_record])
            
            updated_records = client.records.list().to_pandas().to_json()
            
        return account_is_open, label_is_open, not record_is_open, \
            updated_records, current_labels_store, current_accounts_store
    
    else:
        raise PreventUpdate
        
        
@app.callback(
    [Output('delete-modal','is_open'),
     Output('delete-table','columns'),
     Output('delete-table','data'),
     Output('delete-table', 'selected_rows'),
     Output('delete-alert', 'is_open')],
    [Input('delete-button','n_clicks'),
     Input('confirm-delete-button', 'n_clicks')],
    [State('delete-modal','is_open'),
     State('data-type-store', 'data'),
     State('view-table', 'data'),
     State('view-table', 'columns'),
     State('view-table', 'selected_rows'),
     State("master-records-store","data"),
     State("master-labels-store","data"),
     State("master-accounts-store","data"),
     State('delete-table', 'selected_rows'),
     State('delete-table', 'data'),
     State('delete-table', 'columns')]
)
def deleteModal(delete_clicks, confirm_delete_clicks, 
                modal_is_open, data_type, view_table_data, view_table_columns, view_table_selected_rows,
                current_records_store, current_labels_store, current_accounts_store, 
                delete_table_selected_rows, delete_table_data, delete_table_columns):
    
    if view_table_selected_rows and not modal_is_open:
        
        delete_table_data = itemgetter(*view_table_selected_rows)(view_table_data)
        if type(delete_table_data) == dict:
            delete_table_data = [delete_table_data]
            
        return True, view_table_columns, delete_table_data, [], False
            
    elif delete_table_selected_rows and modal_is_open:
        selected_delete_data = itemgetter(*delete_table_selected_rows)(delete_table_data)

        if type(selected_delete_data) == dict:
            selected_delete_data = [selected_delete_data]
        
        delete_ids = [obj['id'] for obj in selected_delete_data]
        
        getattr(client, data_type).delete(ids=delete_ids)
        
        return False, delete_table_columns, delete_table_data, [], False

    elif delete_clicks and not delete_table_selected_rows:
                
        return False, None, None, [], True

    else:
        
        raise PreventUpdate

    
@app.callback(
    [Output('view-table', 'columns'),
     Output('view-table', 'data'),
     Output('sidebar-content', 'children'),
     Output('data-type-store', 'data'),
     Output('view-table', 'selected_rows')],
    [Input('accounts-button', 'n_clicks'),
     Input('records-button', 'n_clicks'),
     Input('labels-button', 'n_clicks'),
     Input("create-accounts-button", "n_clicks"),
     Input("create-labels-button", "n_clicks"),
     Input("create-records-button", "n_clicks")],
    [State("master-records-store","data"),
     State("master-labels-store","data"),
     State("master-accounts-store","data"),
     State('data-type-store', 'data'),
     State('view-table', 'selected_rows')]  
)
def resource_type_selection(account_n, record_n, label_n, 
    create_account_n, create_label_n, create_record_n,
    records_store, labels_store, accounts_store, prev_data_type, view_table_selected_rows):
    
    ctx = callback_context
    trigger_button = ctx.triggered[0]['prop_id'].split('.')[0]

    if 'accounts' in trigger_button:
        
        if 'accounts' == prev_data_type:
            selected_rows = view_table_selected_rows
        else:
            selected_rows = []
        
        accounts_df = pd.read_json(accounts_store)
        data, columns = table_data_columns_formatter(accounts_df)
        return columns, data, account_filter_form, 'accounts', selected_rows
    
    elif 'records' in trigger_button:
        
        if 'records' == prev_data_type:
            selected_rows = view_table_selected_rows
        else:
            selected_rows = []
        
        records_df = pd.read_json(records_store)
        data, columns = table_data_columns_formatter(records_df)
        return columns, data, record_filter_form, 'records', selected_rows
    
    elif 'labels' in trigger_button:
        
        if 'labels' == prev_data_type:
            selected_rows = view_table_selected_rows
        else:
            selected_rows = []
        
        labels_df = pd.read_json(labels_store)
        data, columns = table_data_columns_formatter(labels_df)
        return columns, data, label_filter_form, 'labels', selected_rows
    
    else:
        
        raise PreventUpdate
    

def table_data_columns_formatter(df):
    data=df.to_dict('records')
    columns=[{'id': col, 'name': col} for col in df.columns]
    return data, columns