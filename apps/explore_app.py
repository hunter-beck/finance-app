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

table_placeholder = dash_table.DataTable(
    id='table',
    style_as_list_view=True,
    page_size=20
)

### CREATE POPUP ###
create_button = dbc.Button("Create", id='create-button', color='info')

MODAL_CREATE_BUTTON_STYLE = {
    'className':"mr-2",
    'color':'primary'
}

MODAL_CLOSE_BUTTON_STYLE = {
    'className':"mr-2",
    'color':'secondary'
}

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
                    "Close", id="close-create-account-modal", **MODAL_CLOSE_BUTTON_STYLE
                ),
                dbc.Button(
                    "Create", id="create-create-account-modal", **MODAL_CREATE_BUTTON_STYLE
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
                    "Close", id="close-create-label-modal", **MODAL_CLOSE_BUTTON_STYLE
                ),
                dbc.Button(
                    "Create", id="create-create-label-modal", **MODAL_CREATE_BUTTON_STYLE
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
        dbc.Input(id='create-record-date-input', placeholder='Date')
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
                    "Close", id="close-create-record-modal", **MODAL_CLOSE_BUTTON_STYLE
                ),
                dbc.Button(
                    "Create", id="create-create-record-modal", **MODAL_CREATE_BUTTON_STYLE
                )
            ]
        ),
    ],
    id="create-record-modal",
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
temp_val_store = dcc.Store(id='temp-val-store')
data_type_store = dcc.Store(id='data-type-store')

### LAYOUT ###
explore_app_layout = html.Div([
    data_type_store, 
    create_account_modal, create_label_modal, create_record_modal, 
    body
])

### CALLBACKS ###
@app.callback(
    [Output("create-account-modal", "is_open"),
     Output("create-label-modal", "is_open"),
     Output("create-record-modal", "is_open")],
    [Input('create-button', 'n_clicks'),
     Input("close-create-account-modal", "n_clicks"),
     Input("close-create-label-modal", "n_clicks"),
     Input("close-create-record-modal", "n_clicks"),
     Input("create-create-account-modal", "n_clicks"),
     Input("create-create-label-modal", "n_clicks"),
     Input("create-create-record-modal", "n_clicks")],
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
     State('create-record-date-input', 'value')],
)
def close_modal(create_n, close_account_n, close_label_n, close_record_n,
                create_account_n, create_label_n, create_record_n,
                data_type_store, account_is_open, label_is_open, record_is_open,
                account_name, account_description, account_label, account_country, 
                label_name, label_description,
                record_account, record_balance, record_currency, record_date):
    
    ctx = callback_context
    trigger_button = ctx.triggered[0]['prop_id'].split('.')[0]
        
    if data_type_store == 'accounts':
        if trigger_button == 'create-create-account-modal':
            new_account = Account(
                name=account_name,
                label_id=account_label,
                country_code=account_country
            )
            client.accounts.create(new_account)
            
        return not account_is_open, label_is_open, record_is_open
    
    elif data_type_store == 'labels':
        if trigger_button == 'create-create-label-modal':
            new_label = Label(
                name=label_name,
                description=label_description,
            )
            client.labels.create(new_label)
            
        return account_is_open, not label_is_open, record_is_open
    
    elif data_type_store == 'records':
        if trigger_button == 'create-create-record-modal':
            print(record_date)
            new_record = Record(
                account_id=record_account,
                currency=record_currency,
                balance=record_balance,
                date=record_date
            )
            client.records.create(new_record)
            
        return account_is_open, label_is_open, not record_is_open
    
    else:
        
        raise PreventUpdate
        
        
@app.callback(
    [Output('table', 'columns'),
     Output('table', 'data'),
     Output('sidebar-content', 'children'),
     Output('data-type-store', 'data')],
    [Input('accounts-button', 'n_clicks'),
     Input('records-button', 'n_clicks'),
     Input('labels-button', 'n_clicks'),
     Input("create-create-account-modal", "n_clicks"),
     Input("create-create-label-modal", "n_clicks"),
     Input("create-create-record-modal", "n_clicks")]
)
def accounts_selection(account_n, record_n, label_n, 
                       create_account_n, create_label_n, create_record_n):
    
    ctx = callback_context
    trigger_button = ctx.triggered[0]['prop_id'].split('.')[0]
    print(trigger_button)

    if 'account' in trigger_button:
        print('account')
        accounts_df = client.accounts.list().to_pandas()
        data, columns = table_data_columns_formatter(accounts_df)
        return columns, data, account_filter_form, 'accounts'
    elif 'record' in trigger_button:
        print('record')
        records_df = client.records.list().to_pandas()
        data, columns = table_data_columns_formatter(records_df)
        return columns, data, record_filter_form, 'records'
    elif 'label' in trigger_button:
        print('label')
        labels_df = client.labels.list().to_pandas()
        data, columns = table_data_columns_formatter(labels_df)
        return columns, data, label_filter_form, 'labels'
    else:
        raise PreventUpdate
    
def table_data_columns_formatter(df):
    data=df.to_dict('records')
    columns=[{'id': col, 'name': col} for col in df.columns]
    return data, columns