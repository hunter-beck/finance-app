import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import yaml
from dash.dependencies import State, Input, Output
from app import app
from apps import test_app, explore, analyze
from finance.client import Client  

with open('config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    
with open('secrets.yml') as file:
    users = yaml.load(file, Loader=yaml.FullLoader)['users']
    
client = Client(**config['database']) 

### NAVBAR ###

link_list = []

for link in config['navbar']:
    link_list.append(
        dbc.DropdownMenuItem(dbc.NavLink(link, href=config['navbar'][link], target="_blank"))
    )

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Explore", href="explore")),
        dbc.NavItem(dbc.NavLink("Analyze", href="analyze")),
        dbc.DropdownMenu(
            children=link_list,
            nav=True,
            in_navbar=True,
            label="Accounts",
            right=True
        ),
    ],
    brand="Finance Tool",
    fluid=True
)

### CROSS PAGE STORAGE ###

record_store = dcc.Store(
    id='master-records-store', 
    data=client.records.list().to_pandas().to_json()
)

label_store = dcc.Store(
    id='master-labels-store', 
    data=client.labels.list().to_pandas().to_json()
)

accounts_store = dcc.Store(
    id='master-accounts-store', 
    data=client.accounts.list().to_pandas().to_json()
)

app.layout = html.Div([
    navbar,
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    record_store,
    label_store,
    accounts_store
])


@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    
    if pathname == '/explore':
        return explore.layout
    elif pathname == '/test':
        return test_app.layout
    elif pathname == '/analyze':
        return analyze.layout
    else:
        return '404'        

if __name__ == "__main__":
    app.run_server(debug=True, port=config['app']['port'], host=config['app']['host'])