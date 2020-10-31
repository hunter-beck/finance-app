import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import yaml
from dash.dependencies import State, Input, Output

from app import app
from apps import test_app, explore_app

with open('config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

### NAVBAR ###

link_list = []

for link in config['navbar']:
    link_list.append(
        dbc.DropdownMenuItem(dbc.NavLink(link, href=config['navbar'][link], target="_blank"))
    )

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Explore", href="explore")),
        dbc.DropdownMenu(
            children=link_list,
            nav=True,
            in_navbar=True,
            label="Accounts",
            right=True
        ),
    ],
    brand="Finance Tool",
    color="primary",
    dark=True,
    fluid=True
)

app.layout = html.Div([
    navbar,
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    
    if pathname == '/explore':
        return explore_app.explore_app_layout
    elif pathname == '/test':
        return test_app.test_app_layout
    else:
        return '404'
        

if __name__ == "__main__":
    app.run_server(debug=True)