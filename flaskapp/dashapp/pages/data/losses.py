import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *

directory = get_directory(__name__)['directory']
page = get_directory(__name__)['page']
dash.register_page(__name__, path_template=f'/{directory}/{page}/<analysis_id>')
page_id = get_page_id(__name__)


def layout(analysis_id=None):
    analysis_name = 'VAV Agro SL 2024'

    datatable = html.Div([

    ])

    return html.Div([
        get_title(__name__, analysis_name),
        get_nav_middle(__name__, analysis_id),
        get_nav_bottom(__name__, analysis_id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Button('Load', id=page_id + 'btn-load', className='button'),
                ])
            ]),
            dbc.Row([
                dbc.Col([

                ])
            ]),
        ], className='div-standard')
    ])
    #
