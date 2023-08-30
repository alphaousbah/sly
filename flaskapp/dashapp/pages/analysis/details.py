import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *

dash.register_page(__name__, path_template='/analysis/details/<analysis_id>')


def layout(analysis_id=None):
    analysis_id = str(analysis_id).split('/')[-1]
    return html.Div([
        header_nav(__name__, analysis_id),
        html.Div([
            dbc.Row([
                dbc.Col([
                    f'Details for analysis {analysis_id}'
                ])
            ])
        ], className='div-standard')
    ])
