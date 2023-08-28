import dash
from dash import html, dcc, dash_table, callback, Output, Input, State
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *
from flaskapp.models import Analysis
from flaskapp.extensions import db
import pandas as pd

dash.register_page(__name__, nav_loc='top')

id_page = get_id_page(__name__)


def layout():
    print(id_page)
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Analysis Settings'),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Label('Analysis Name', html_for=id_page + 'input-form', width=2),
                            dbc.Col([
                                dbc.Input(id=id_page + 'input-name', placeholder='Enter a value'),
                            ]),
                        ], className='mb-2'),
                        dbc.Row([
                            dbc.Label('Client', html_for=id_page + 'input-client', width=2),
                            dbc.Col([
                                dbc.Input(id=id_page + 'input-client', placeholder='Enter a value'),
                            ]),
                        ], className='mb-2'),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button('Click', id=id_page + 'btn-create', n_clicks=0, className='button'),
                                html.Div(id=id_page + 'div-output'),
                            ]),
                        ]),
                    ]),
                ], className='card'),
            ], width=10),
        ]),
    ], className='div-standard')


@callback(
    Output(id_page + 'div-output', 'children'),
    Input(id_page + 'btn-create', 'n_clicks'),
    [
        State(id_page + 'input-name', 'value'),
        State(id_page + 'input-client', 'value'),
    ],
)
def update_div(n_clicks, name, client):
    if n_clicks > 0:
        new_analysis = Analysis(name=name, client=client)
        db.session.add(new_analysis)
        db.session.commit()
        return f'The analysis {name} for {client} has been created'
