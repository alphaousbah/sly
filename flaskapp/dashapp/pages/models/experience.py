import dash
from dash import html, dcc, dash_table, callback, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *
from flaskapp.extensions import db
from flaskapp.models import *
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
        dcc.Store(id=page_id + 'store'),
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
    config_prevent_initial_callbacks=True
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
        html.Div(id=page_id + 'div-model'),
    ]),


@callback(
    Output(page_id + 'div-model', 'children'),
    Output(page_id + 'store', 'data'),
    Input(page_id + 'slider-modeling-period', 'value'),
    State(page_id + 'table-losses', 'data'),
)
def display_model(slider_value, data):
    df = pd.DataFrame(data).astype(float)
    df['year'] = df['year'].astype(int)

    year_min = slider_value[0]
    year_max = slider_value[1]

    sample = df['loss_ratio'][(df['year'] >= year_min) & (df['year'] <= year_max)]

    # TODO: Create a function that takes a sample and return an evaluation of all parameters
    mean = np.mean(sample)
    std = np.std(sample)

    mu = np.log(mean / np.sqrt(1 + std ** 2 / mean ** 2))
    scale = np.exp(mu)
    s = np.sqrt(np.log((1 + std ** 2 / mean ** 2)))

    param_lognorm = {
        's': s,
        'scale': scale,
    }

    fit_lognorm = lognorm(s=s, scale=scale)

    x = np.linspace(fit_lognorm.ppf(0.01), fit_lognorm.ppf(0.99), 10000)

    df_model = pd.DataFrame(
        {
            'x': x.tolist(),
            'y': fit_lognorm.pdf(x).tolist()
        }
    )

    df_sample = pd.DataFrame(sample)

    fig = px.histogram(
        df_sample, x='loss_ratio',
        histnorm='probability density',
        nbins=15,
        range_x=[x[0], x[-1]],
    )

    fig.add_trace(px.line(df_model, x='x', y='y', color_discrete_sequence=['red']).data[0])

    layout = html.Div([
        dbc.Label('Distribution statitics'),
        html.Div(f'mean: {mean:.3f}'),
        html.Div(f'standard deviation: {std:.3f}', className='mb-3'),
        dcc.Graph(id=page_id + 'graph-distribution', figure=fig, className='mb-3'),
        dbc.Alert(
            'The year loss table has been saved',
            id=page_id + 'alert-save',
            color='success',
            is_open=False,
            duration=2000,
        ),
        dbc.Button(
            'Create the gross YLT',
            id=page_id + 'btn-create-model',
            outline=True,
            color='primary',
            className='button mb-3',
        ),
        html.Div(id=page_id + 'div-gross-ylt'),
    ]),

    return layout, param_lognorm


@callback(
    Output(page_id + 'div-gross-ylt', 'children'),
    Output(page_id + 'alert-save', 'is_open'),
    Input(page_id + 'btn-create-model', 'n_clicks'),
    State(page_id + 'store', 'data'),
    State(page_id + 'location', 'pathname'),
    config_prevent_initial_callbacks=True
)
def create_gross_ylt(n_clicks, data, pathname):
    # Identify and get the analysis
    analysis_id = str(pathname).split('/')[-1]
    analysis = db.session.query(Analysis).get(analysis_id)

    # Create the gross YLT
    s = data['s']
    scale = data['scale']

    fit_lognorm = lognorm(s=s, scale=scale)

    # TODO: Define a function that creates a Gross YLT based on s, scale and number of draws
    size = 1000
    years = range(1, size + 1)
    loss_ratios = fit_lognorm.rvs(size=size).tolist()

    df = pd.DataFrame(
        {
            'year': years,
            'amount': loss_ratios
        }
    )

    # TODO: Create an input for the name of the YLT
    # Save the year loss table in the database
    yearlosstable = YearLossTable(
        analysis_id=analysis.id,
        view='gross',
    )

    db.session.add(yearlosstable)
    db.session.commit()

    yearlosstable.name = f'YLT {yearlosstable.id}'
    db.session.commit()

    # Save the events of the year loss table in the database
    for index, row in df.iterrows():
        yearloss = YearLoss(
            yearlosstable_id=yearlosstable.id,
            year=row['year'],
            amount=row['amount']
        )
        db.session.add(yearloss)
        db.session.commit()

    table_yearlosses = dash_table.DataTable(
        data=df.to_dict('records'),
        css=get_datatable_css(),
        style_header=get_datatable_style_header(),
        style_cell=get_datatable_style_cell(),
    )

    return table_yearlosses, True
