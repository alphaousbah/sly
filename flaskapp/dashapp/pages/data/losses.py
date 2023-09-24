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
    analysis = db.session.query(Analysis).get(analysis_id)

    # Define the modal that is used to add a loss file
    modal_add_lossfile = html.Div([
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle('Upload Historic Loss File')),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label('Vintage', html_for=page_id + 'input-vintage', width=2),
                        dbc.Input(id=page_id + 'input-vintage', placeholder='Enter a value'),
                    ]),
                ], className='mb-2'),
                dbc.Row([
                    dbc.Col([
                        dbc.Label('Name', html_for=page_id + 'input-name', width=2),
                        dbc.Input(id=page_id + 'input-name', placeholder='Enter a value'),
                    ]),
                ], className='mb-2'),
                dbc.Row([
                    dbc.Col([
                        dbc.Textarea(
                            id=page_id + 'text-area',
                            placeholder='year premium loss loss_ratio' + '\n' + '2023 1000	500 0.5',
                            style={'width': '100%', 'height': 300},
                            className='mb-2',
                        ),
                        dbc.Button('Load', id=page_id + 'btn-load', className='mb-2 button'),
                        dbc.Alert(
                            'The loss file has been loaded',
                            id=page_id + 'alert-save',
                            is_open=False,
                            duration=2000,
                        ),
                    ]),
                ]),
            ]),
        ],
            id=page_id + 'modal-add-lossfile',
            size='md',
            is_open=False,
        ),
    ])

    return html.Div([
        dcc.Location(id=page_id + 'location'),
        dcc.Store(id=page_id + 'store'),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),
        get_nav_bottom(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    modal_add_lossfile,
                    dbc.Button('Add', id=page_id + 'btn-add', outline=True, color='primary', className='button'),
                    dbc.Button('Delete', id=page_id + 'btn-delete', outline=True, color='primary', className='button'),
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div(
                        get_table_lossfiles(page_id + 'table-lossfiles', analysis.histolossfiles),
                        id=page_id + 'div-table-lossfiles'
                    ),
                ], width=6),
                dbc.Col([
                    html.Div(id=page_id + 'div-table-losses'),
                ], width=6),
            ]),
        ], className='div-standard')
    ])


@callback(
    Output(page_id + 'modal-add-lossfile', 'is_open'),
    Input(page_id + 'btn-add', 'n_clicks'),
    State(page_id + 'modal-add-lossfile', 'is_open'),
)
def toggle_modal(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@callback(
    Output(page_id + 'alert-save', 'is_open'),
    Output(page_id + 'div-table-lossfiles', 'children', allow_duplicate=True),
    Input(page_id + 'btn-load', 'n_clicks'),
    State(page_id + 'location', 'pathname'),
    State(page_id + 'text-area', 'value'),
    State(page_id + 'input-vintage', 'value'),
    State(page_id + 'input-name', 'value'),
    State(page_id + 'btn-load', 'is_open'),
    config_prevent_initial_callbacks=True
)
def create_lossfile(n_clicks, pathname, data, vintage, name, is_open):
    # Save the new loss file in the database
    analysis_id = str(pathname).split('/')[-1]  # https://dash.plotly.com/dash-core-components/location
    analysis = db.session.query(Analysis).get(analysis_id)
    lossfile = HistoLossFile(
        analysis_id=analysis.id,
        vintage=vintage,
        name=name
    )
    db.session.add(lossfile)
    db.session.commit()

    df_losses = pd.read_csv(StringIO(data), sep='\t')
    df_losses['loss_ratio'] = df_losses['loss_ratio'].str.replace(',', '.').astype(float)

    # Loop through the rows of a dataframe :
    # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    for index, row in df_losses.iterrows():
        loss = HistoLoss(
            lossfile_id=lossfile.id,
            year=row['year'],
            premium=row['premium'],
            loss=row['loss'],
            loss_ratio=row['loss_ratio']
        )
        db.session.add(loss)
        db.session.commit()

    # Update the loss files table after adding the new loss file
    table_lossfiles = get_table_lossfiles(page_id + 'table-lossfiles', analysis.histolossfiles)

    return not is_open, table_lossfiles


@callback(
    Output(page_id + 'div-table-losses', 'children', allow_duplicate=True),
    Input(page_id + 'table-lossfiles', 'active_cell'),
    config_prevent_initial_callbacks=True
)
def display_losses(active_cell):
    if active_cell:
        # https://stackoverflow.com/questions/55157682/hover-data-and-click-data-from-dash-table-on-dash
        lossfile_id = active_cell['row_id']
        lossfile = db.session.query(HistoLossFile).get(lossfile_id)

        table_losses = get_table_losses(page_id + 'table-losses', lossfile.losses)

        return table_losses

    raise PreventUpdate


@callback(
    Output(page_id + 'div-table-lossfiles', 'children'),
    Output(page_id + 'div-table-losses', 'children'),
    Input(page_id + 'btn-delete', 'n_clicks'),
    State(page_id + 'table-lossfiles', 'selected_row_ids'),
    State(page_id + 'location', 'pathname'),
)
def delete_lossfiles(n_clicks, selected_row_ids, pathname):
    if n_clicks is None or selected_row_ids is None:
        raise PreventUpdate

    # Identify and get the analysis
    analysis_id = str(pathname).split('/')[-1]
    analysis = db.session.query(Analysis).get(analysis_id)

    # Delete the selected loss files
    for lossfile_id in selected_row_ids:
        lossfile = db.session.query(HistoLossFile).get(lossfile_id)
        db.session.delete(lossfile)
        db.session.commit()

    # Update the loss files table
    table_lossfiles = get_table_lossfiles(page_id + 'table-lossfiles', analysis.histolossfiles)

    return table_lossfiles, None
