import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *

dash.register_page(__name__, path_template='/data/losses/<analysis_id>')


def layout(analysis_id=None):
    return html.Div([
        header_nav(__name__, analysis_id),
        html.Div([
            dbc.Row([
                dbc.Col([
                    'Content'
                ])
            ])
        ], className='div-standard')
    ])