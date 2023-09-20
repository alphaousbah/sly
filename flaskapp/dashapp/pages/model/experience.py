import dash
from dash import html, dcc, dash_table, callback, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *
from flaskapp.extensions import db
from flaskapp.models import Analysis, HistoLossFile
import pandas as pd
import numpy as np
from scipy.stats import lognorm
import plotly.express as px

directory = get_directory(__name__)['directory']
page = get_directory(__name__)['page']
dash.register_page(__name__, path_template=f'/{directory}/{page}/<analysis_id>')
page_id = get_page_id(__name__)


def layout(analysis_id):
    analysis = db.session.query(Analysis).get(analysis_id)

    return html.Div([
        dcc.Location(id=page_id + 'location'),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),
        get_nav_bottom(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Label('Select a loss file', html_for=page_id + 'select-lossfile'),
                    html.Div(
                        get_table_lossfiles(page_id + 'table-lossfiles', analysis.histolossfiles),
                        id=page_id + 'div-table-lossfiles',
                        className='mb-4',
                    ),
                    html.Div(id=page_id + 'div-model-parameters'),
                ], width=6),
                dbc.Col([
                    html.Div(id=page_id + 'div-table-losses'),
                ], width=6),
            ]),
        ], className='div-standard')
    ])


@callback(
    Output(page_id + 'div-table-losses', 'children'),
    Input(page_id + 'table-lossfiles', 'active_cell'),
    config_prevent_initial_callbacks=True,
)
def display_lossfile(active_cell):
    if active_cell:
        # Display the loss set
        # https://stackoverflow.com/questions/55157682/hover-data-and-click-data-from-dash-table-on-dash
        lossfile_id = active_cell['row_id']
        lossfile = db.session.query(HistoLossFile).get(lossfile_id)

        table_losses = get_table_losses(page_id + 'table-losses', lossfile.losses)

        return html.Div([
            dbc.Label('Selected loss file'),
            table_losses,
        ]),

    raise PreventUpdate


@callback(
    Output(page_id + 'div-model-parameters', 'children'),
    Input(page_id + 'table-losses', 'data'),
)
def display_model_parameters(data):
    df = pd.DataFrame(data)
    df['year'] = df['year'].astype(int)
    year_min = min(df['year'])
    year_max = max(df['year'])

    return html.Div([
        dbc.Label('Select a modeling period', html_for=page_id + 'slider-modeling-period'),
        dcc.RangeSlider(
            id=page_id + 'slider-modeling-period',
            min=year_min,
            max=year_max,
            step=1,
            value=[year_min + 1, year_max - 1],
            marks={year: f'{year}' for year in range(year_min, year_max + 1)},
            className='mb-3',
        ),
        html.Div(id=page_id + 'div-model-statistics'),
    ]),


@callback(
    Output(page_id + 'div-model-statistics', 'children'),
    Input(page_id + 'slider-modeling-period', 'value'),
    State(page_id + 'table-losses', 'data'),
)
def display_model_statistics(slider_value, data):
    df = pd.DataFrame(data).astype(float)
    df['year'] = df['year'].astype(int)

    year_min = slider_value[0]
    year_max = slider_value[1]

    sample_loss_ratio = df['loss_ratio'][(df['year'] >= year_min) & (df['year'] <= year_max)]

    mean_loss_ratio = np.mean(sample_loss_ratio)
    std_loss_ratio = np.std(sample_loss_ratio)

    mu = np.log(mean_loss_ratio / np.sqrt(1 + std_loss_ratio ** 2 / mean_loss_ratio ** 2))
    scale = np.exp(mu)
    s = np.sqrt(np.log((1 + std_loss_ratio ** 2 / mean_loss_ratio ** 2)))

    simulation = lognorm.rvs(s=s, scale=scale, size=10000)
    print(sample_loss_ratio)

    fig = None

    return html.Div([
        dbc.Label('Distribution statitics'),
        html.Div(f'mean: {mean_loss_ratio}'),
        html.Div(f'standard deviation: {std_loss_ratio}', className='mb-3'),
        dcc.Graph(id=page_id + 'graph-distribution', figure=fig),
        dbc.Button(
            'Create a lognormal model',
            id=page_id + 'btn-create-model',
            outline=True,
            color='primary',
            className='button',
        )
    ]),
