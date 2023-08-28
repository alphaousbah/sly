import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *

dash.register_page(__name__)


def layout():
    return html.Div([
        header_nav(__name__),
        html.Div([
            dbc.Row([
                dbc.Col([
                    'Content'
                ])
            ])
        ], className='div-standard')
    ])
