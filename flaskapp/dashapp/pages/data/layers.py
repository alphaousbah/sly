import dash
from dash import html, dcc, dash_table, callback, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *
from flaskapp.extensions import db
from flaskapp.models import *
import pandas as pd
from io import StringIO

directory = get_directory(__name__)['directory']
page = get_directory(__name__)['page']
dash.register_page(__name__, path_template=f'/{directory}/{page}/<analysis_id>')
page_id = get_page_id(__name__)


def layout(analysis_id):
    analysis = db.session.get(Analysis, analysis_id)

    return html.Div([
        dcc.Location(id=page_id + 'location'),
        dcc.Store(id=page_id + 'store'),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),
        get_nav_bottom(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.DropdownMenu(
                        label='Add layers',
                        children=[
                            dbc.DropdownMenuItem('1', id=page_id + 'btn-create-1'),
                            dbc.DropdownMenuItem('2', id=page_id + 'btn-create-2'),
                            dbc.DropdownMenuItem('3', id=page_id + 'btn-create-3'),
                            dbc.DropdownMenuItem('4', id=page_id + 'btn-create-4'),
                            dbc.DropdownMenuItem('5', id=page_id + 'btn-create-5'),
                        ],
                        className='button',
                        toggle_style={
                            'color': '#2780e3',
                            'fontSize': '13px',
                            'background': '#f5f8fa',
                        }
                    ),
                    dbc.Button('Save Layers', id=page_id + 'btn-save', outline=True, color='primary',
                               className='button'),
                    dbc.Button('Delete Layers', id=page_id + 'btn-delete', outline=True, color='primary',
                               className='button'),
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div(
                        get_table_layers(page_id + 'table-layers', analysis.layers),
                        id=page_id + 'div-table-layers',
                        className='mb-2'
                    ),
                    html.Div([
                        dbc.Alert(
                            'The layers have been deleted',
                            id=page_id + 'alert-layers-deleted',
                            is_open=False,
                            duration=2000
                        ),
                        html.Div(id=page_id + 'div-layers-modified'),
                    ]),
                ], width=6)
            ]),
        ], className='div-standard')
    ])


# Callback that creates n layers with n defined by the click on the dropdown menu
for i in [1, 2, 3, 4, 5]:
    @callback(
        Output(page_id + 'div-table-layers', 'children', allow_duplicate=True),
        Input(page_id + f'btn-create-{i}', 'n_clicks'),
        State(page_id + 'location', 'pathname'),
        State(page_id + f'btn-create-{i}', 'children'),
        config_prevent_initial_callbacks=True
    )
    def create_layers(n_clicks, pathname, n_layers):  # n_layers = children property of btn-create
        analysis_id = str(pathname).split('/')[-1]
        analysis = db.session.get(Analysis, analysis_id)
        n_layers = int(n_layers[0])

        for i in range(1, n_layers + 1):
            layer = Layer(analysis_id=analysis.id)
            layer.deductible = 0
            layer.limit = 0
            db.session.add(layer)
            db.session.commit()

        # Update the layers table
        table_layers = get_table_layers(page_id + 'table-layers', analysis.layers)

        return table_layers


@callback(
    Output(page_id + 'div-table-layers', 'children'),
    Output(page_id + 'alert-layers-deleted', 'is_open'),
    Input(page_id + 'btn-delete', 'n_clicks'),
    State(page_id + 'table-layers', 'selected_row_ids'),
    State(page_id + 'location', 'pathname'),
)
def delete_layers(n_clicks, selected_row_ids, pathname):
    if n_clicks is None or selected_row_ids is None:
        raise PreventUpdate

    # Identify and get the analysis
    analysis_id = str(pathname).split('/')[-1]
    analysis = db.session.get(Analysis, analysis_id)

    # Delete the selected layers
    for layer_id in selected_row_ids:
        layer = db.session.get(Layer, layer_id)
        db.session.delete(layer)
        db.session.commit()

    # Update the layers table
    table_layers = get_table_layers(page_id + 'table-layers', analysis.layers)

    return table_layers, True


@callback(
    Output(page_id + 'div-layers-modified', 'children', allow_duplicate=True),
    Input(page_id + 'table-layers', 'data'),
    config_prevent_initial_callbacks=True
)
def inform_layers_modified(data):
    alert = dbc.Alert(
        'The layers have been modified. Save the changes with the Save button',
        id=page_id + 'alert-layers-modified',
        color='danger',
    )

    return alert


@callback(
    Output(page_id + 'div-layers-modified', 'children'),
    Input(page_id + 'btn-save', 'n_clicks'),
    State(page_id + 'table-layers', 'data'),
    config_prevent_initial_callbacks=True
)
def save_layers(n_clicks, data):
    for row in data:
        layer = db.session.get(Layer, row['id'])

        layer.premium = int(row['premium'])
        layer.deductible = int(row['deductible'])
        layer.limit = int(row['limit'])
        db.session.commit()

    alert = dbc.Alert(
        'The changes have been saved',
        id=page_id + 'alert-layers-modified',
        color='success',
        is_open=True,
        duration=2000,
    )
    return alert
