import dash
from dash import html, dcc, dash_table, callback, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *
from flaskapp.extensions import db
from flaskapp.models import *
import pandas as pd

dash.register_page(__name__, path='/')
page_id = get_page_id(__name__)


def layout():
    return html.Div([
        html.H5('Analysis Search', className='title'),
        html.Div([
            dbc.Row([
                dbc.Col([
                    dcc.Link(dbc.Button('Create', id=page_id + 'btn-create', className='button'),
                             href='/dashapp/analysis/create'),
                    dbc.Button('Copy', id=page_id + 'btn-copy', className='button'),
                    dbc.Button('Delete', id=page_id + 'btn-delete', className='button'),
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div(
                        get_table_analyses(page_id + 'table-analyses', Analysis.query.all()),
                        id=page_id + 'div-table-analyses'
                    ),
                    # html.Div(
                    #     get_table_analyses(page_id + 'table_analyses', Analysis.query.all()),
                    #     id=page_id + 'div-table-analyses'
                    # ),
                ], width=6),
            ]),
        ], className='div-standard'),
    ]),


# TODO: Add a modal to ask the user to confirm the deletion
@callback(
    Output(page_id + 'div-table-analyses', 'children'),
    Input(page_id + 'btn-delete', 'n_clicks'),
    State(page_id + 'table-analyses', 'selected_row_ids'),
)
def delete_analyses(n_clicks, selected_row_ids):
    print('entered callback')
    if n_clicks is None or selected_row_ids is None:
        raise PreventUpdate

    # Delete selected analyses
    for analysis_id in selected_row_ids:
        analysis = db.session.get(Analysis, analysis_id)
        db.session.delete(analysis)
        db.session.commit()

    # Update the analyses table
    table_analyses = get_table_analyses(page_id + 'table-analyses', Analysis.query.all())

    return table_analyses

