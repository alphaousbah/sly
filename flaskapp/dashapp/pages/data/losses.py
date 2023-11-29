import dash
from dash import html, dcc, callback, Output, Input, State, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
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
                        dbc.Button('Save', id=page_id + 'btn-save', className='mb-2 button'),
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
        dcc.Store(id=page_id + 'store', data={'analysis_id': analysis_id}),
        get_title(__name__, analysis.name),
        get_nav_middle(__name__, analysis.id),
        get_nav_bottom(__name__, analysis.id),

        html.Div([
            dbc.Row([
                dbc.Col([
                    modal_add_lossfile,
                    get_button(page_id + 'btn-add', 'Add'),
                    get_button(page_id + 'btn-delete', 'Delete'),
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div(
                        dag.AgGrid(
                            id=page_id + 'grid-lossfiles',
                            rowData=df_from_sqla(analysis.histolossfiles).to_dict('records'),
                            columnDefs=[
                                {'field': 'id', 'hide': True},
                                {'field': 'name', 'checkboxSelection': True, 'headerCheckboxSelection': True},
                                {'field': 'vintage'},
                            ],
                            getRowId='params.data.id',
                            defaultColDef={'flex': True, 'sortable': True, 'filter': True, 'floatingFilter': True},
                            columnSize='responsiveSizeToFit',
                            dashGridOptions={'rowSelection': 'multiple'},
                            className='ag-theme-alpine custom',
                        ),
                    ),
                ], width=4),
                dbc.Col([
                    html.Div(id=page_id + 'div-losses'),
                ], width=8),
            ]),
        ], className='div-standard')
    ])


@callback(
    Output(page_id + 'modal-add-lossfile', 'is_open', allow_duplicate=True),
    Input(page_id + 'btn-add', 'n_clicks'),
    config_prevent_initial_callbacks=True
)
def toggle_modal(n_clicks):
    return True


@callback(
    Output(page_id + 'modal-add-lossfile', 'is_open'),
    Output(page_id + 'grid-lossfiles', 'rowData', allow_duplicate=True),
    Output(page_id + 'text-area', 'value'),
    Output(page_id + 'input-vintage', 'value'),
    Output(page_id + 'input-name', 'value'),
    Input(page_id + 'btn-save', 'n_clicks'),
    State(page_id + 'store', 'data'),
    State(page_id + 'text-area', 'value'),
    State(page_id + 'input-vintage', 'value'),
    State(page_id + 'input-name', 'value'),
    config_prevent_initial_callbacks=True
)
def save_lossfile(n_clicks, data, value, vintage, name):
    # TODO: Add checking the input data properly and informing the user
    # TODO: Add informing the user if the input data is incorrect using a dbc.Alert
    if not (value and vintage and name):
        raise PreventUpdate

    # Save the new loss file in the database
    analysis_id = data['analysis_id']
    analysis = db.session.get(Analysis, analysis_id)
    lossfile = HistoLossFile(
        analysis_id=analysis.id,
        vintage=vintage,
        name=name
    )
    db.session.add(lossfile)
    db.session.commit()

    df_losses = pd.read_csv(StringIO(value), sep='\t')
    df_losses['loss_ratio'] = df_losses['loss_ratio'].str.replace(',', '.').astype(float)

    # Loop through the rows of a dataframe
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
    db.session.commit()  # Commit after the loop for DB performance

    # Update the loss files grid
    rowData = df_from_sqla(analysis.histolossfiles).to_dict('records')

    return False, rowData, None, None, None


@callback(
    Output(page_id + 'div-losses', 'children', allow_duplicate=True),
    Input(page_id + 'grid-lossfiles', 'cellClicked'),
    config_prevent_initial_callbacks=True
)
def display_losses(cellClicked):
    lossfile_id = cellClicked['rowId']
    lossfile = db.session.get(HistoLossFile, lossfile_id)

    grid_losses = dag.AgGrid(
        id=page_id + 'grid-oep',
        rowData=df_from_sqla(lossfile.losses).to_dict('records'),
        columnDefs=[
            {'field': 'year'},
            {'field': 'premium', 'valueFormatter': {'function': 'd3.format(",d")(params.value)'}},
            {'field': 'loss', 'valueFormatter': {'function': 'd3.format(",d")(params.value)'}},
            {'field': 'loss_ratio', 'valueFormatter': {'function': 'd3.format(".1%")(params.value)'}},
        ],
        columnSize='responsiveSizeToFit',
    )

    return grid_losses


@callback(
    Output(page_id + 'grid-lossfiles', 'rowData'),
    Output(page_id + 'div-losses', 'children'),
    Input(page_id + 'btn-delete', 'n_clicks'),
    State(page_id + 'store', 'data'),
    State(page_id + 'grid-lossfiles', 'selectedRows'),
)
def delete_lossfiles(n_clicks, data, selectedRows):
    if n_clicks is None or selectedRows is None:
        return no_update

    # TODO: Inform the user that the deletion was successful
    analysis_id = data['analysis_id']
    analysis = db.session.get(Analysis, analysis_id)

    # Delete the selected loss files
    for lossfile in selectedRows:
        lossfile = db.session.get(HistoLossFile, lossfile['id'])
        db.session.delete(lossfile)
    db.session.commit()  # Commit after the loop for DB performance

    # Update the loss files grid
    rowData = df_from_sqla(analysis.histolossfiles).to_dict('records')

    return rowData, None
