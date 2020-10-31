import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import State, Input, Output

from app import app

button = dbc.Button('test', id='test-button')

test_app_layout = html.Div(
    [ 
        html.H1('TEST APP', id='text'),
        button
    ]
)

@app.callback(
    Output('text', 'children'),
    [Input('test-button', 'n_clicks')]
)
def test_button(n):
    return 'SUCCESS: ' + str(n)