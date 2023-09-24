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
dash.register_page(__name__, path_template=f'/{directory}/{page}/<analysis_id>')
page_id = get_page_id(__name__)


def layout(analysis_id):
    analysis = db.session.query(Analysis).get(analysis_id)
    layers = analysis.layers

    select_yearlosstables = []

    for layer in layers:

        # Get all the year loss tables linked to the analysis
        available_yearlosstables = []

        for yearlosstable in analysis.yearlosstables:
            available_yearlosstables.append(
                {'value': yearlosstable.id, 'label': yearlosstable.name}
            )

        # Get the year loss tables that are already linked to the layer
        id_current_yearlosstables = []

        for yearlosstable in layer.yearlosstables:
            id_current_yearlosstables.append(yearlosstable.id)

        select = dmc.MultiSelect(
            id={'type': 'select-yearlosstable', 'layer_id': layer.id},
            label=f'Layer {layer.id} {layer}',
            placeholder='Click here to select the year loss tables',
            data=available_yearlosstables,
            value=id_current_yearlosstables,
            clearable=True,
            className='mb-3',
            # style={'width': 400, 'marginBottom': 20},
        )

        select_yearlosstables.append(select)

    return html.Div([
        dcc.Location(id=page_id + 'location'),
        dcc.Store(id=page_id + 'store'),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),
        # get_nav_bottom(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div(id=page_id + 'div-select-yearlosstables', children=select_yearlosstables),

                    # TODO: Create a function that creates a dbc button with all the usual arguments
                    dbc.Button(
                        'Save the relationships',
                        id=page_id + 'btn-save',
                        outline=True,
                        color='primary',
                        className='button',
                    ),
                    dbc.Alert(
                        'The relationships have been modified. Save the changes with the Save button',
                        id=page_id + 'alert-relationships-modified',
                        color='danger',
                        is_open=False,
                    ),
                    dbc.Alert(
                        'The relationships have been saved',
                        id=page_id + 'alert-save',
                        color='success',
                        is_open=False,
                        duration=2000,
                    ),
                ], width=4),
            ]),
        ], className='div-standard')
    ])


# https://dash.plotly.com/pattern-matching-callbacks
@callback(
    Output(page_id + 'alert-relationships-modified', 'is_open', allow_duplicate=True),
    Input({'type': 'select-yearlosstable', 'layer_id': ALL}, 'value'),
    config_prevent_initial_callbacks=True
)
def inform_relationships_modified(value):
    return True


@callback(
    Output(page_id + 'alert-relationships-modified', 'is_open'),
    Output(page_id + 'alert-save', 'is_open'),
    Input(page_id + 'btn-save', 'n_clicks'),
    State({'type': 'select-yearlosstable', 'layer_id': ALL}, 'id'),
    State({'type': 'select-yearlosstable', 'layer_id': ALL}, 'value'),
    config_prevent_initial_callbacks=True
)
def save_relationships(n_clicks, id, value):
    return False, True
