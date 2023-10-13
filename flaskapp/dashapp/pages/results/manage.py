import dash
from dash import html, dcc, dash_table, callback, Output, Input, State, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from flaskapp.dashapp.pages.utils import *
from flaskapp.extensions import db
from flaskapp.models import *
import pandas as pd

directory = get_directory(__name__)['directory']
page = get_directory(__name__)['page']
dash.register_page(__name__, path_template=f'/{directory}/{page}/<analysis_id>', order=1)
page_id = get_page_id(__name__)


def layout(analysis_id):
    analysis = db.session.get(Analysis, analysis_id)

    return html.Div([
        dcc.Store(id=page_id + 'store', data={'analysis_id': analysis_id}),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),
        get_nav_bottom(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    get_button(page_id + 'btn-process', 'Process'),
                    html.Div(
                        get_table_relationships(page_id + 'table-relationships', analysis.pricingrelationships),
                        id=page_id + 'div-table-relationships'
                    ),
                ], width=5, className='mb-2'),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Alert(
                        'The result has been saved',
                        id=page_id + 'alert_save',
                        color='success',
                        is_open=False,
                        duration=4000,
                    ),
                ], width=5),
            ]),
            dbc.Row([
                dbc.Col([

                ]),
            ]),
        ], className='div-standard')
    ])


@callback(
    Output(page_id + 'div-table-relationships', 'children'),
    Output(page_id + 'alert_save', 'is_open'),
    Input(page_id + 'btn-process', 'n_clicks'),
    State(page_id + 'store', 'data'),
    State(page_id + 'table-relationships', 'selected_row_ids'),
)
def save_result(n_clicks, data, selected_row_ids):
    if n_clicks is None or selected_row_ids is None:
        raise PreventUpdate

    analysis_id = data['analysis_id']
    analysis = db.session.get(Analysis, analysis_id)

    for pricingrelationship_id in selected_row_ids:
        result = Result(
            name=db.session.get(PricingRelationship, pricingrelationship_id).name,
            analysis_id=analysis_id,
            pricingrelationship_id=pricingrelationship_id
        )
        db.session.add(result)
        db.session.commit()

    table_relationships = get_table_relationships(page_id + 'table-relationships', analysis.pricingrelationships)

    return table_relationships, True
