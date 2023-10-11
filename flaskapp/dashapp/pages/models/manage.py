import dash
from dash import html, dcc, dash_table, callback, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *
from flaskapp.extensions import db
from flaskapp.models import *
import pandas as pd

directory = get_directory(__name__)['directory']
page = get_directory(__name__)['page']
dash.register_page(__name__, path_template=f'/{directory}/{page}/<analysis_id>')
page_id = get_page_id(__name__)


def layout(analysis_id):
    analysis = db.session.get(Analysis, analysis_id)

    return html.Div([
        dcc.Location(id=page_id + 'location'),
        dcc.Store(id=page_id + 'store'),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),
        get_nav_bottom(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Button('Delete', id=page_id + 'btn-delete', outline=True, color='primary', className='button mb-3'),
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div(
                        get_table_modelfiles(page_id + 'table-modelfiles', analysis.modelfiles),
                        id=page_id + 'div-table-modelfiles'
                    ),
                ], width=6),
                dbc.Col([
                    'Display the OEP curve of the selected model file',
                ], width=6),
            ]),
        ], className='div-standard')
    ])
