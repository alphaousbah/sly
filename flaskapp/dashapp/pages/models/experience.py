import dash
from dash import html, dcc, dash_table, callback, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from flaskapp.dashapp.pages.utils import *
from flaskapp.extensions import db
from flaskapp.models import *
import pandas as pd
import numpy as np
from scipy.stats import lognorm
import plotly.express as px

directory = get_directory(__name__)['directory']
page = get_directory(__name__)['page']
dash.register_page(__name__, path_template=f'/{directory}/{page}/<analysis_id>', order=2)
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
                    html.Div('1. Select a loss file:', className='h5 mb-3'),
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
            html.Div('2. Selected loss file:', className='h5 mb-3'),
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
        dbc.Row([
            dbc.Col([
                html.Div('3. Select a modeling period:', className='h5 mb-3'),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dmc.Select(
                    id=page_id + 'select-start-modeling-period',
                    label='Start',
                    data=[{'value': year, 'label': year} for year in range(year_min, year_max + 1)],
                    value=year_min,
                ),
            ], width=4),
            dbc.Col([
                dmc.Select(
                    id=page_id + 'select-end-modeling-period',
                    label='End',
                    data=[{'value': year, 'label': year} for year in range(year_min, year_max + 1)],
                    value=year_max,
                ),
            ], width=4),
        ], className='mb-3'),
        dbc.Row([
            dbc.Col([
                html.Div(id=page_id + 'div-model'),
            ]),
        ]),
    ]),


@callback(
    Output(page_id + 'select-end-modeling-period', 'data'),
    Input(page_id + 'select-start-modeling-period', 'value'),
    State(page_id + 'table-losses', 'data'),
)
def update_options_year_max(value, data):
    year_min = value
    df = pd.DataFrame(data)
    year_max = int(max(df['year']))

    data = [{'value': year, 'label': year} for year in list(range(year_min + 1, year_max + 1))]

    return data


@callback(
    Output(page_id + 'div-model', 'children'),
    Output(page_id + 'store', 'data'),
    Input(page_id + 'select-start-modeling-period', 'value'),
    Input(page_id + 'select-end-modeling-period', 'value'),
    State(page_id + 'table-losses', 'data'),
)
def display_model(value_year_min, value_year_max, data):
    df = pd.DataFrame(data).astype(float)
    df['year'] = df['year'].astype(int)

    year_min = int(value_year_min)
    year_max = int(value_year_max)

    sample = df['loss_ratio'][(df['year'] >= year_min) & (df['year'] <= year_max)]

    param_lognorm = get_lognorm_param(sample)
    fit_lognorm = lognorm(s=param_lognorm['s'], scale=param_lognorm['scale'])

    x = np.linspace(fit_lognorm.ppf(0.01), fit_lognorm.ppf(0.99), 10000)

    df_model = pd.DataFrame({'x': x.tolist(), 'y': fit_lognorm.pdf(x).tolist()})
    df_sample = pd.DataFrame(sample)

    fig = px.histogram(
        df_sample, x='loss_ratio',
        histnorm='probability density',
        nbins=15,
        range_x=[x[0], x[-1]],
    )

    fig.add_trace(px.line(df_model, x='x', y='y', color_discrete_sequence=['red']).data[0])

    layout = html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label('Distribution statistics:'),
            ], width=5),
            dbc.Col([
                html.Div(f'mean: {param_lognorm["mean"]:.3f}'),
                html.Div(f'standard deviation: {param_lognorm["std"]:.3f}'),
            ], width=5),
        ], className='mb-3'),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id=page_id + 'graph-distribution', figure=fig),
            ]),
        ], className='mb-3'),
        dbc.Row([
            dbc.Col([
                dbc.Col([
                    html.Div('4. Create the gross YLT', className='h5 mb-3'),
                ]),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Alert(
                    'The year loss table has been saved',
                    id=page_id + 'alert-save',
                    color='success',
                    is_open=False,
                    duration=2000,
                ),
            ]),
        ], className='mb-3'),
        dbc.Row([
            dbc.Col([
                dmc.TextInput(
                    id=page_id + 'input-name-gross-ylt',
                    placeholder='Enter the name of the gross YLT',
                ),
            ]),
            dbc.Col([
                dbc.Button(
                    'Create',
                    id=page_id + 'btn-create-model',
                    outline=True,
                    color='primary',
                    className='button',
                ),
            ]),
        ], className='mb-3'),
        dbc.Row([
            dbc.Col([
                html.Div(id=page_id + 'div-gross-ylt'),
            ]),
        ]),
    ]),

    return layout, param_lognorm


@callback(
    Output(page_id + 'div-gross-ylt', 'children'),
    Output(page_id + 'alert-save', 'is_open'),
    Input(page_id + 'btn-create-model', 'n_clicks'),
    State(page_id + 'location', 'pathname'),
    State(page_id + 'store', 'data'),
    State(page_id + 'input-name-gross-ylt', 'value'),
    config_prevent_initial_callbacks=True
)
def create_gross_ylt(n_clicks, pathname, data, value):
    # Identify and get the analysis
    analysis_id = str(pathname).split('/')[-1]
    analysis = db.session.query(Analysis).get(analysis_id)

    # Create the gross YLT
    s = data['s']
    scale = data['scale']
    fit_lognorm = lognorm(s=s, scale=scale)

    # TODO: Create a global variable giving the size of the YLTs
    size = 1000
    years = range(1, size + 1)
    loss_ratios = fit_lognorm.rvs(size=size).tolist()

    df = pd.DataFrame({'year': years, 'amount': loss_ratios})

    # Save the year loss table in the database
    yearlosstable = YearLossTable(
        analysis_id=analysis.id,
        name=value,
        view='gross',
    )
    db.session.add(yearlosstable)
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
