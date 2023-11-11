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
    analysis = db.session.get(Analysis, analysis_id)

    if analysis.histolossfiles:
        table_lossfiles = get_table_lossfiles(page_id + 'table-lossfiles', analysis.histolossfiles)
    else:
        table_lossfiles = 'No loss files added to the analysis'

    return html.Div([
        dcc.Store(id=page_id + 'store', data={'analysis_id': analysis_id}),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),
        get_nav_bottom(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div('1. Select a loss file:', className='h5 mb-3'),
                    html.Div(
                        table_lossfiles,
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
        lossfile_id = active_cell['row_id']
        lossfile = db.session.get(HistoLossFile, lossfile_id)

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
                # Wrap the model div in a loading component
                dcc.Loading(
                    html.Div(id=page_id + 'div-model'),
                    id=page_id + 'loading-model',
                ),
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
    State(page_id + 'store', 'data'),
    State(page_id + 'table-losses', 'data'),
)
def display_model(value_year_min, value_year_max, data_store, data_table):
    df = pd.DataFrame(data_table)
    df['loss_ratio'] = df['loss_ratio'].astype(float)
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
                    html.Div('4. Save the loss model', className='h5 mb-3'),
                ]),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dmc.TextInput(
                    id=page_id + 'input-name-modelfile',
                    placeholder='Enter the name of the loss model',
                ),
            ], width=5),
            dbc.Col([
                get_button(page_id + 'btn-save-model', 'Save'),
            ], width=1),
        ], className='mb-3'),
        dbc.Row([
            dbc.Col([
                dbc.Alert(
                    'The loss model has been saved as a YLT',
                    id=page_id + 'alert-save',
                    color='success',
                    is_open=False,
                    duration=4000,
                ),
            ], width=6),
        ], className='mb-3'),
        dbc.Row([
            dbc.Col([
                dcc.Loading(
                    html.Div(id=page_id + 'div-modelyearloss'),
                    id=page_id + 'loading-div-modelyearloss',
                ),

            ]),
        ]),
    ]),

    data_store = data_store | param_lognorm  # Merge the 2 dictionaries with the '|' operator

    return layout, data_store


@callback(
    Output(page_id + 'div-modelyearloss', 'children'),
    Output(page_id + 'alert-save', 'is_open'),
    Input(page_id + 'btn-save-model', 'n_clicks'),
    State(page_id + 'store', 'data'),
    State(page_id + 'input-name-modelfile', 'value'),
    config_prevent_initial_callbacks=True
)
def save_loss_model(n_clicks, data, value):
    analysis_id = data['analysis_id']
    analysis = db.session.get(Analysis, analysis_id)

    # Save the model file
    modelfile = ModelFile(
        analysis_id=analysis.id,
        name=value,
    )
    db.session.add(modelfile)
    db.session.commit()

    # Create the model file year losses
    s = data['s']
    scale = data['scale']
    fit_lognorm = lognorm(s=s, scale=scale)

    NBYEARS = 10000  # TODO: Create a global constant giving the number of years
    years = range(1, NBYEARS + 1)
    loss_ratios = fit_lognorm.rvs(size=NBYEARS).tolist()

    df = pd.DataFrame({'year': years, 'amount': loss_ratios})

    # Save the model file year losses
    for index, row in df.iterrows():
        yearloss = ModelYearLoss(
            year=row['year'],
            amount=row['amount'],
            modelfile_id=modelfile.id
        )
        db.session.add(yearloss)
    db.session.commit()  # Commit after the loop for DB performance

    table_yearlosses = dash_table.DataTable(
        data=df.to_dict('records'),
        css=get_datatable_css(),
        style_header=get_datatable_style_header(),
        style_cell=get_datatable_style_cell(),
    )

    return table_yearlosses, True
