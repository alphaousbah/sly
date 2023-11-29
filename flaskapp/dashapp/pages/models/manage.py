import dash
from dash import html, dcc, callback, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
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
    df = df_from_sqla(analysis.modelfiles)

    return html.Div([
        dcc.Store(id=page_id + 'store', data={'analysis_id': analysis_id}),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),
        get_nav_bottom(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    get_button(page_id + 'btn-delete', 'Delete'),
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div(
                        dag.AgGrid(
                            id=page_id + 'grid-modelfiles',
                            rowData=df.to_dict('records'),
                            columnDefs=[
                                {
                                    'field': 'name',
                                    'checkboxSelection': True, 'headerCheckboxSelection': True,
                                    'rowDrag': True,
                                }
                            ],
                            getRowId='params.data.id',
                            columnSize='responsiveSizeToFit',
                            dashGridOptions={'rowSelection': 'multiple'},
                        ),
                        id=page_id + 'div-table-modelfiles'
                    ),
                ], width=4),
                dbc.Col([
                    'Display the OEP curve of the selected model file',
                ], width=8),
            ]),
        ], className='div-standard')
    ])
