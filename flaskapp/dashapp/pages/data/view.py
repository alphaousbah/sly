import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *

directory = get_directory(__name__)['directory']
page = get_directory(__name__)['page']
dash.register_page(__name__, path_template=f'/{directory}/{page}/<analysis_id>', order=1)


def layout(analysis_id=None):
    analysis_name = 'VAV Agro SL 2024'

    return html.Div([
        get_title(__name__, analysis_name),
        get_nav_middle(__name__, analysis_id),
        get_nav_bottom(__name__, analysis_id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Img(src='/dashapp/assets/under-construction.png')
                ])
            ])
        ], className='div-standard')
    ])