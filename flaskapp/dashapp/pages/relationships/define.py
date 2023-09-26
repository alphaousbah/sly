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

    # Get all the gross year loss tables linked to the analysis
    available_ylts = []

    for ylt in analysis.yearlosstables:
        available_ylts.append({'value': ylt.id, 'label': ylt.name})

    # Create the select component for each layer and add it to the list select_yearlosstables
    component_select_ylts = []

    for layer in analysis.layers:

        # Get all the gross year loss tables already linked to the layer
        # How to query with an association table :
        # https://stackoverflow.com/questions/21335607/querying-association-table-object-directly
        # https://stackoverflow.com/questions/3332991/sqlalchemy-filter-multiple-columns
        selected_ylts = []

        query_gross_ylts = db.session.query(yearlosstables) \
            .join(Layer).join(YearLossTable) \
            .filter(Layer.id == layer.id, YearLossTable.view == 'gross').all()

        for record in query_gross_ylts:
            # The first column (index = 0) of the association table contains the year loss table id
            selected_ylts.append(record[0])

        # Create the select component
        select_ylt = dmc.MultiSelect(
            id={'type': 'select-yearlosstable', 'layer_id': layer.id},
            label=f'Layer {layer.id} - {layer}',
            placeholder='Click here to select the year loss tables',
            data=available_ylts,
            value=selected_ylts,
            clearable=True,
            className='mb-3',
        )

        component_select_ylts.append(select_ylt)

    return html.Div([
        dcc.Location(id=page_id + 'location'),
        dcc.Store(id=page_id + 'store'),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),
        # get_nav_bottom(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div(id=page_id + 'div-select-yearlosstables', children=component_select_ylts),

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
def save_relationships(n_clicks, id_, value):
    # id_ is a list of dictionaries that contains the layer id for each select component
    # e.g. [{'type': 'select-yearlosstable', 'layer_id': 1}, {'type': 'select-yearlosstable', 'layer_id': 2}]
    # value is a list of the lists that give the ids of the selected year loss tables for each layer
    # e.g. [[54, 65], [54], [54]]
    n_layers = len(value)

    for i in range(n_layers):
        layer_id = id_[i]['layer_id']
        layer = db.session.query(Layer).get(layer_id)

        # Clear the previous relationships in the database
        layer.yearlosstables.clear()
        db.session.commit()

        # Save new relationships in the database
        for yearlosstable_id in value[i]:
            yearlosstable = db.session.query(YearLossTable).get(yearlosstable_id)
            layer.yearlosstables.append(yearlosstable)
            db.session.commit()

    return False, True
