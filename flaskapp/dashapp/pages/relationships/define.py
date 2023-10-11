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
    analysis = db.session.get(Analysis, analysis_id)

    # Get all the model files linked to the analysis
    available_modelfiles = []

    for modelfile in analysis.modelfiles:
        available_modelfiles.append({'value': modelfile.id, 'label': modelfile.name})

    # Create the select component for each layer and add it to the list select_yearlosstables
    component_select_modelfiles = []

    for layer in analysis.layers:

        # Get all the models files already linked to the layer
        selected_modelfiles = []

        for modelfile in layer.modelfiles:
            selected_modelfiles.append(modelfile.id)

        # Create the select component
        select_modelfiles = dmc.MultiSelect(
            id={'type': 'select-modelfiles', 'layer_id': layer.id},
            label=f'Layer {layer.name}',
            placeholder='Click here to select the model files',
            data=available_modelfiles,
            value=selected_modelfiles,
            clearable=True,
            className='mb-3',
        )

        component_select_modelfiles.append(select_modelfiles)

    return html.Div([
        dcc.Location(id=page_id + 'location'),
        dcc.Store(id=page_id + 'store'),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div(id=page_id + 'div-select-modelfiles', children=component_select_modelfiles),

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
    Input({'type': 'select-modelfiles', 'layer_id': ALL}, 'value'),
    config_prevent_initial_callbacks=True
)
def inform_relationships_modified(value):
    return True


@callback(
    Output(page_id + 'alert-relationships-modified', 'is_open'),
    Output(page_id + 'alert-save', 'is_open'),
    Input(page_id + 'btn-save', 'n_clicks'),
    State({'type': 'select-modelfiles', 'layer_id': ALL}, 'id'),
    State({'type': 'select-modelfiles', 'layer_id': ALL}, 'value'),
    config_prevent_initial_callbacks=True
)
def save_relationships(n_clicks, id_, value):
    # id_ is a list of dictionaries that contains the layer id for each select component
    # e.g. [{'type': 'select-modelfiles', 'layer_id': 1}, {'type': 'select-modelfiles', 'layer_id': 2}]
    # value is a list of the lists that give the ids of the selected model files for each layer
    # e.g. [[54, 65], [54], [54]]
    n_layers = len(id_)

    for i in range(n_layers):
        layer_id = id_[i]['layer_id']
        layer = db.session.get(Layer, layer_id)

        # Clear the previous relationships in the database
        layer.modelfiles.clear()
        db.session.commit()

        # Save new relationships in the database
        for modelfile_id in value[i]:
            modelfile = db.session.get(ModelFile, modelfile_id)
            layer.modelfiles.append(modelfile)
            db.session.commit()

    return False, True
