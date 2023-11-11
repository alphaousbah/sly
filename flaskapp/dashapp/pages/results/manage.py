import dash
from dash import html, dcc, dash_table, callback, Output, Input, State, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from flaskapp.dashapp.pages.utils import *
from flaskapp.extensions import db
from flaskapp.models import *
import pandas as pd
import time

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
                    get_button(page_id + 'btn-delete', 'Delete'),
                    dcc.Loading(
                        html.Div(
                            get_table_relationships(page_id + 'table-relationships', analysis.pricingrelationships),
                            id=page_id + 'div-table-relationships'
                        ),
                        id=page_id + 'loading-div-table-relationships',
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
def process_result(n_clicks, data, selected_row_ids):
    if n_clicks is None or selected_row_ids is None:
        raise PreventUpdate

    analysis_id = data['analysis_id']
    analysis = db.session.get(Analysis, analysis_id)
    is_open = False
    start = time.perf_counter()  # TODO: Timer

    for pricingrelationship_id in selected_row_ids:
        # Check if the pricing relationships has already been processed
        # If not, process and save the result file and the result year losses
        check = db.session.query(ResultFile). \
            filter_by(analysis_id=analysis_id, pricingrelationship_id=pricingrelationship_id).first()

        if not check:
            # Save the result file
            resultfile = ResultFile(
                name=db.session.get(PricingRelationship, pricingrelationship_id).name,
                analysis_id=analysis_id,
                pricingrelationship_id=pricingrelationship_id
            )
            db.session.add(resultfile)
            db.session.commit()

            # Save the result year losses
            for layertomodelfile in resultfile.pricingrelationship.layertomodelfiles:
                layer = layertomodelfile.layer
                modelfile = layertomodelfile.modelfile

                for modelyearloss in modelfile.modelyearlosses:
                    resultyearloss = ResultYearLoss(
                        name=modelyearloss.name,
                        resultfile_id=resultfile.id,
                        layertomodelfile_id=layertomodelfile.id,
                        year=modelyearloss.year,
                        # For the SL, the amount contains the simulated loss ratio
                        grossloss=layer.premium * modelyearloss.amount
                    )

                    # Apply the SL cover to get the recovery and net amount
                    resultyearloss.recovery = get_sl_recovery(
                        resultyearloss.grossloss,
                        layer.premium,
                        layer.limit,
                        layer.deductible,
                    )
                    resultyearloss.netloss = resultyearloss.grossloss - resultyearloss.recovery

                    db.session.add(resultyearloss)
                db.session.commit()  # Commit after the loop for DB performance

            is_open = True

    table_relationships = get_table_relationships(page_id + 'table-relationships', analysis.pricingrelationships)
    print(f'Elapsed time: {time.perf_counter() - start}')  # TODO: Timer
    return table_relationships, is_open
