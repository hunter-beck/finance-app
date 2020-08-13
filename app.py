import dash
import yaml
import dash_bootstrap_components as dbc

with open('config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)    

app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    suppress_callback_exceptions=True
)