import dash
from dash import html, dcc, dash_table, callback, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *
from flaskapp.models import Analysis
from flaskapp.extensions import db

dash.register_page(__name__)
page_id = get_page_id(__name__)


def layout():
    return html.Div([
        html.H5('Create Analysis', className='title'),
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('Analysis Settings'),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Label('AGIR Quote', html_for=page_id + 'input-quote', width=2),
                                dbc.Col([
                                    dbc.Input(id=page_id + 'input-quote', placeholder='Enter a value'),
                                ]),
                            ], className='mb-2'),
                            dbc.Row([
                                dbc.Label('Analysis Name', html_for=page_id + 'input-name', width=2),
                                dbc.Col([
                                    dbc.Input(id=page_id + 'input-name', placeholder='Enter a value'),
                                ]),
                            ], className='mb-2'),
                            dbc.Row([
                                dbc.Label('Client', html_for=page_id + 'input-client', width=2),
                                dbc.Col([
                                    dbc.Input(id=page_id + 'input-client', placeholder='Enter a value'),
                                ]),
                            ], className='mb-2'),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Create', id=page_id + 'btn-create', n_clicks=0, className='button'),
                                    html.Div(id=page_id + 'div-output'),
                                ]),
                            ]),
                        ]),
                    ], className='card'),
                ], width=10),
            ]),
        ], className='div-standard'),
    ])


@callback(
    Output(page_id + 'div-output', 'children'),
    Input(page_id + 'btn-create', 'n_clicks'),
    State(page_id + 'input-quote', 'value'),
    State(page_id + 'input-name', 'value'),
    State(page_id + 'input-client', 'value'),
    config_prevent_initial_callbacks=True
)
def create_analysis(n_clicks, quote, name, client):
    analysis = Analysis(quote=quote, name=name, client=client)
    db.session.add(analysis)
    db.session.commit()
    return f'The analysis {name} for {client} has been created'
