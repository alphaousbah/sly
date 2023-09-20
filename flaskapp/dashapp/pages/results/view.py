import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *

# Automate the path_template with the chapter and subchapter. Data and layers here

directory = get_directory(__name__)['directory']
page = get_directory(__name__)['page']
dash.register_page(__name__, path_template=f'/{directory}/{page}/<analysis_id>')


def layout(analysis_id):
    analysis_name = 'VAV Agro SL 2024'

    return html.Div([
        get_title(__name__, analysis_name),
        get_nav_middle(__name__, analysis_id),
        get_nav_bottom(__name__, analysis_id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    'Content View Results'
                ])
            ])
        ], className='div-standard')
    ])
