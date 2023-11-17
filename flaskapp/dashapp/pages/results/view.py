# https://stackoverflow.com/questions/9916878/importing-modules-in-python-best-practice/29193752#29193752import dash
from dash import html, dcc, dash_table, callback, Output, Input, State, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import dash_mantine_components as dmc
from flaskapp.dashapp.pages.utils import *
from flaskapp.extensions import db
from flaskapp.models import *
import pandas as pd

directory = get_directory(__name__)['directory']
page = get_directory(__name__)['page']
dash.register_page(__name__, path_template=f'/{directory}/{page}/<analysis_id>', order=2)
page_id = get_page_id(__name__)


def layout(analysis_id, resultfile_id=None):
    analysis = db.session.get(Analysis, analysis_id)

    # Initialize the OEP and summary tables
    QUANTILES = [.999, .998, .996, .995, .99, .98, .9667, .96, .95, .9, .8, .5]
    df_oep = pd.DataFrame({
        'quantile': [f'{quantile:.2%}' for quantile in QUANTILES],
        'return period': [f'{1 / (1 - quantile):,.0f}' for quantile in QUANTILES],
        'proba': QUANTILES,
    })
    df_summary = pd.DataFrame({
        'quantile': ['Pure premium', 'Standard deviation'],
        'return period': ['', ''],
        'proba': ['', ''],
    })

    if resultfile_id:
        resultfile = db.session.get(ResultFile, resultfile_id)
    else:
        resultfile = db.session.query(ResultFile).order_by(ResultFile.id.desc()).first()

    if resultfile:
        # Set the title of the page
        title = resultfile.name.capitalize()

        # Get the layers of the result pricing relationship
        layertomodelfiles = resultfile.pricingrelationship.layertomodelfiles
        # Use set to get the layers without repetition
        # https://www.learnpython.org/en/Sets
        layers = [layertomodelfile.layer for layertomodelfile in layertomodelfiles]

        # Sort the layers by name
        layers = sorted(layers, key=lambda l: l.name)

        # Get the result year losses
        resultyearlosses = resultfile.resultyearlosses

        for layer in layers:
            # Get the year losses for the current layer
            layer_resultyearlosses = [
                resultyearloss for resultyearloss in resultyearlosses
                if resultyearloss.layertomodelfile.layer == layer
            ]
            recoveries = df_from_query(layer_resultyearlosses)[['year', 'recovery']]
            recoveries['recovery'] = recoveries['recovery'].astype(int)

            recoveries_by_year = recoveries.groupby('year')['recovery'].sum()
            df_oep[layer.name] = df_oep['proba'].map(lambda proba: f'{recoveries_by_year.quantile(proba):,.0f}')

            df_summary[layer.name] = [
                # Pure premium
                f'{recoveries_by_year.mean():,.0f}',
                # Standard deviation
                f'{recoveries_by_year.std():,.0f}',
            ]

    else:
        # Set the title of the page
        title = 'Process a pricing model to get the results'

    return html.Div([
        dcc.Store(id=page_id + 'store', data={'analysis_id': analysis_id, 'resultfile_id': resultfile_id}),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),
        get_nav_bottom(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div(title, className='h6 mb-3'),
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    # https://dash.plotly.com/dash-ag-grid/row-pinning
                    dag.AgGrid(
                        id=page_id + 'grid-oep',
                        rowData=df_oep.to_dict('records'),
                        columnDefs=[{'field': col} for col in df_oep.columns if col != 'proba'],
                        dashGridOptions={
                            'rowHeight': 40,
                            'pinnedBottomRowData': df_summary.to_dict('records'),
                        },
                        style={'height': 500},
                        className='ag-theme-alpine custom mb-2',
                    ),
                ]),
            ]),
            dbc.Row([
                dbc.Col([

                ]),
            ]),
            dbc.Row([
                dbc.Col([

                ]),
            ]),
            dbc.Row([
                dbc.Col([

                ]),
            ]),
            dbc.Row([
                dbc.Col([

                ]),
            ]),
        ], className='div-standard')
    ])
