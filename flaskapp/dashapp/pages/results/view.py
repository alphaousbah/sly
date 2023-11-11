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
dash.register_page(__name__, path_template=f'/{directory}/{page}/<analysis_id>', order=2)
page_id = get_page_id(__name__)


def layout(analysis_id, resultfile_id=None):
    analysis = db.session.get(Analysis, analysis_id)

    if resultfile_id is None:
        resultfile_id = db.session.query(ResultFile).order_by(ResultFile.id.desc())

    resultfile = db.session.get(ResultFile, resultfile_id)

    # Get the layers of the result pricing relationship
    layertomodelfiles = resultfile.pricingrelationship.layertomodelfiles
    # Use set to get the layers without repetition
    # https://www.learnpython.org/en/Sets
    layers = set([layertomodelfile.layer for layertomodelfile in layertomodelfiles])
    resultyearlosses = resultfile.resultyearlosses

    # Initialize the OEP dataframe
    QUANTILES = [.999, .998, .996, .995, .99, .98, .966667, .96, .95, .9, .8, .5, .1]
    df_oep = pd.DataFrame({'quantile': QUANTILES})

    for layer in layers:
        # Get the year losses for the current layer
        layer_resultyearlosses = [
            resultyearloss for resultyearloss in resultyearlosses
            if resultyearloss.layertomodelfile.layer == layer
        ]
        recoveries = df_from_query(layer_resultyearlosses)[['year', 'recovery']]
        recoveries['recovery'] = recoveries['recovery'].astype(int)

        recoveries_by_year = recoveries.groupby('year')['recovery'].sum()
        df_oep[layer.name] = df_oep['quantile'].map(lambda proba: round(recoveries_by_year.quantile(proba)))

        print(df_oep)

    return html.Div([
        dcc.Store(id=page_id + 'store', data={'analysis_id': analysis_id, 'result_id': resultfile_id}),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),
        get_nav_bottom(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    dag.AgGrid(
                        id=page_id + 'grid-oep',
                        rowData=df_oep.to_dict('records'),
                        columnDefs=[
                            {'field': 'id', 'hide': True},
                            {
                                'field': 'name',
                                'checkboxSelection': True, 'headerCheckboxSelection': True,
                                'rowDrag': True,
                            },
                            {'field': 'premium', 'valueFormatter': {'function': 'd3.format(",d")(params.value)'}, },
                            {'field': 'deductible', 'valueFormatter': {'function': '(params.value) + "%"'}, },
                            {'field': 'limit', 'valueFormatter': {'function': '(params.value) + "%"'}, },
                            {'field': 'analysis_id'},
                            {'field': 'display_order'},
                            # {'field': 'display_order', 'hide': True},
                        ]
                        ,
                        getRowId='params.data.id',
                        defaultColDef={
                            'flex': True,
                            'editable': True,
                        },
                        dashGridOptions={'rowSelection': 'multiple', 'rowDragManaged': True, 'rowDragMultiRow': True,
                                         'animateRows': True},
                        persistence=True,
                        className='ag-theme-alpine custom mb-2',
                    ),
                ]),
            ]),
            dbc.Row([
                dbc.Col([

                ]),
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
            dbc.Row([
                dbc.Col([

                ]),
            ]),
        ], className='div-standard')
    ])
