import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.LITERA],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    suppress_callback_exceptions=True
)

server = app.server