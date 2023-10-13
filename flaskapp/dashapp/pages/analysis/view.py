import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from flaskapp.dashapp.pages.utils import *
from flaskapp.models import *
from flaskapp.extensions import db

directory = get_directory(__name__)['directory']
page = get_directory(__name__)['page']
dash.register_page(__name__, path_template=f'/{directory}/{page}/<analysis_id>')
page_id = get_page_id(__name__)


def layout(analysis_id):
    analysis = db.session.get(Analysis, analysis_id)

    return html.Div([
        dcc.Store(id=page_id + 'store', data={'analysis_id': analysis_id}),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('Analysis Settings'),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label('AGIR Quote', html_for=page_id + 'input-quote', width=2),
                                    dbc.Input(id=page_id + 'input-quote', value=analysis.quote),
                                ]),
                            ], className='mb-2'),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label('Analysis Name', html_for=page_id + 'input-name', width=2),
                                    dbc.Input(id=page_id + 'input-name', value=analysis.name),
                                ]),
                            ], className='mb-2'),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label('Client', html_for=page_id + 'input-client', width=2),
                                    dbc.Input(id=page_id + 'input-client', value=analysis.client),
                                ]),
                            ], className='mb-2'),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Update', id=page_id + 'btn-update', className='button'),
                                    dbc.Alert(
                                        "The analysis has been updated",
                                        id=page_id + 'alert-save',
                                        is_open=False,
                                        duration=4000,
                                    ),
                                ]),
                            ]),
                        ]),
                    ], className='card'),
                ], width=8),
            ]),

        ], className='div-standard')
    ])


@callback(
    Output(page_id + 'alert-save', 'is_open'),
    Input(page_id + 'btn-update', 'n_clicks'),
    State(page_id + 'store', 'data'),
    State(page_id + 'input-quote', 'value'),
    State(page_id + 'input-name', 'value'),
    State(page_id + 'input-client', 'value'),
    State(page_id + 'alert-save', 'is_open'),
    config_prevent_initial_callbacks=True
)
def update_analysis(n_clicks, data, quote, name, client, is_open):
    analysis_id = data['analysis_id']

    analysis = db.session.get(Analysis, analysis_id)
    analysis.quote = quote
    analysis.name = name
    analysis.client = client
    db.session.commit()

    return not is_open
