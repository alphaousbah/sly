import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from flaskapp.dashapp.pages.utils import *
from flaskapp.models import Analysis
from flaskapp.extensions import db

directory = get_directory(__name__)['directory']
page = get_directory(__name__)['page']
dash.register_page(__name__, path_template=f'/{directory}/{page}/<analysis_id>', order=1)
page_id = get_page_id(__name__)


def layout(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)

    return html.Div([
        dcc.Location(id=page_id + 'location'),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader('Analysis Settings'),
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Label('AGIR Quote', html_for=page_id + 'input-quote', width=2),
                                        dbc.Col([
                                            dbc.Input(id=page_id + 'input-quote', value=analysis.quote),
                                        ]),
                                    ], className='mb-2'),
                                    dbc.Row([
                                        dbc.Label('Analysis Name', html_for=page_id + 'input-name', width=2),
                                        dbc.Col([
                                            dbc.Input(id=page_id + 'input-name', value=analysis.name),
                                        ]),
                                    ], className='mb-2'),
                                    dbc.Row([
                                        dbc.Label('Client', html_for=page_id + 'input-client', width=2),
                                        dbc.Col([
                                            dbc.Input(id=page_id + 'input-client', value=analysis.client),
                                        ]),
                                    ], className='mb-2'),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button('Update', id=page_id + 'btn-update', className='button'),
                                            dbc.Alert(
                                                "The analysis has been updated",
                                                id=page_id + 'alert-update',
                                                is_open=False,
                                                duration=2000,
                                            ),
                                        ]),
                                    ]),
                                ]),
                            ], className='card'),
                        ], width=10),
                    ]),
                ])
            ])
        ], className='div-standard')
    ])


@callback(
    Output(page_id + 'alert-update', 'is_open'),
    Input(page_id + 'btn-update', 'n_clicks'),
    State(page_id + 'location', 'pathname'),
    State(page_id + 'input-quote', 'value'),
    State(page_id + 'input-name', 'value'),
    State(page_id + 'input-client', 'value'),
    State(page_id + 'alert-update', 'is_open'),
    config_prevent_initial_callbacks=True
)
def update_analysis(n_clicks, pathname, quote, name, client, is_open):
    analysis_id = str(pathname).split('/')[-1]

    analysis = Analysis.query.get_or_404(analysis_id)
    analysis.quote = quote
    analysis.name = name
    analysis.client = client
    db.session.commit()

    return not is_open
