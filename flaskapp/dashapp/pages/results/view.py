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
    df_oep = pd.DataFrame(
        {
            'quantile': [f'{quantile:.2%}' for quantile in QUANTILES],
            'return period': [f'{1 / (1 - quantile):,.0f}' for quantile in QUANTILES],
            'proba': QUANTILES,
        }
    )
    df_summary = pd.DataFrame(
        {
            'quantile': ['Pure premium', 'Standard deviation'],
            'return period': [''] * 2,
            'proba': [''] * 2,
        },
        index=['Pure premium', 'Standard deviation']
    )

    if resultfile_id:
        resultfile = db.session.get(ResultFile, resultfile_id)
    else:
        # Get the last result file in none was provided via the url's query string
        resultfile = db.session.query(ResultFile).order_by(ResultFile.id.desc()).first()

    if resultfile:
        # Set the title of the page
        title = resultfile.name.capitalize()

        # Get the layers and model files for the result's pricing relationship
        # Use the set() function to get the layers without repetition
        # Sort the objects by name with the sorted() function
        layertomodelfiles = resultfile.pricingrelationship.layertomodelfiles

        modelfiles = set([layertomodelfile.modelfile for layertomodelfile in layertomodelfiles])
        modelfiles = sorted(modelfiles, key=lambda modelfile: modelfile.name)

        layers = set([layertomodelfile.layer for layertomodelfile in layertomodelfiles])
        layers = sorted(layers, key=lambda layer: layer.name)

        # Add rows to df_summary relating to the model files
        df_summary_index_ini = list(df_summary.index)

        for modelfile in modelfiles:
            df_summary.loc[len(df_summary)] = [f'PP {modelfile.name}'] + [''] * 2

        df_summary.index = df_summary_index_ini + [f'PP {modelfile.name}' for modelfile in modelfiles]

        """
        What df_summary looks like:

        index               quantile            return period       proba
        -------------------------------------------------------------------
        Pure premium        Pure premium        ''                  ''
        Standard deviation  Standard deviation  ''                  ''
        Model File 1        PP Model File 1     ''                  '' 
        Model File 2        PP Model File 1     ''                  ''
        ...

        """

        # Add columns to df_summary relating to the layers
        for layer in layers:
            df_summary[layer.name] = [''] * len(df_summary.index)

        """
        What df_summary looks like:
        
        index               quantile            return period       proba       Layer 1     Layer2
        ---------------------------------------------------------------------------------------------     
        Pure premium        Pure premium        ''                  ''          ''          ''
        Standard deviation  Standard deviation  ''                  ''          ''          ''
        Model File 1        PP Model File 1     ''                  ''          ''          ''
        Model File 2        PP Model File 1     ''                  ''          ''          ''
        ...
        
        """

        # Get the result file's year loss table
        resultyearlosses = resultfile.resultyearlosses

        for layer in layers:
            # Get the year loss table for the current layer
            resultyearlosses_for_layer = [
                resultyearloss for resultyearloss in resultyearlosses
                if resultyearloss.layertomodelfile.layer == layer
            ]

            if len(resultyearlosses_for_layer) > 0:
                recoveries = df_from_sqla(resultyearlosses_for_layer)[['year', 'recovery']]
                recoveries['recovery'] = recoveries['recovery'].astype(int)

                recoveries_by_year = recoveries.groupby('year')['recovery'].sum()
                df_oep[layer.name] = df_oep['proba'].map(lambda proba: f'{recoveries_by_year.quantile(proba):,.0f}')

                df_summary.at['Pure premium', layer.name] = f'{recoveries_by_year.mean():,.0f}'
                df_summary.at['Standard deviation', layer.name] = f'{recoveries_by_year.std():,.0f}'

            # Get the expected loss by loss model
            for modelfile in modelfiles:
                resultyearlosses_for_layer_and_modelfile = [
                    resultyearloss for resultyearloss in resultyearlosses_for_layer
                    if resultyearloss.layertomodelfile.modelfile == modelfile
                ]
                recoveries_modelfile = df_from_sqla(resultyearlosses_for_layer_and_modelfile)

                if len(recoveries_modelfile) > 0:
                    recoveries_modelfile['recovery'] = recoveries_modelfile['recovery'].astype(int)
                    df_summary.at[f'PP {modelfile.name}', layer.name] = round(recoveries_modelfile['recovery'].mean())

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
                        columnSize='responsiveSizeToFit',
                        dashGridOptions={
                            'rowHeight': 35,
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
