import dash
from dash import html, dcc, dash_table, callback, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *
from flaskapp.extensions import db
from flaskapp.models import Analysis
import pandas as pd

dash.register_page(__name__, path='/')
page_id = get_page_id(__name__)


def layout():
    analyses = query_to_list(Analysis.query.all())

    # Create links to open an analysis from the datatable
    for analysis in analyses:
        for col in ['quote', 'name']:
            analysis[col] = '[' + analysis[col] + '](/dashapp/analysis/view/' + str(analysis['id']) + ')'

    df = pd.DataFrame(analyses)

    datatable = dash_table.DataTable(
        id=page_id + 'datatable',
        data=df.to_dict('records'),
        columns=[{'id': col, 'name': str(col).capitalize(), 'presentation': 'markdown'} for col in df.columns],
        hidden_columns=['id'],
        sort_by=[{'column_id': 'id', 'direction': 'asc'}],
        editable=False,
        filter_action='native',
        sort_action='native',
        sort_mode='multi',
        row_selectable='multi',
        selected_rows=[],
        page_action='native',
        page_current=0,
        page_size=10,
        css=[
            {'selector': 'p', 'rule': 'margin: 0'},
            {'selector': '.show-hide', 'rule': 'display: none'}
        ],
        style_header={
            'backgroundColor': 'whitesmoke',
            'padding': '0.5rem'
        },
        style_cell={
            'fontFamily': '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,'
                          '"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol",'
                          '"Noto Color Emoji"',
            'fontSize': '13px',
            'lineHeight': '1.5',
            'textAlign': 'left',
            'padding': '0.5rem',
            'border': '1px solid #dee2e6',
        },
        style_data_conditional=[
            # {'if': {'column_id': 'id'}, 'width': '10%'},
        ]
    )

    return html.Div([
        html.H5('Analysis Search', className='title'),
        html.Div([
            dbc.Row([
                dbc.Col([
                    dcc.Link(dbc.Button('Create', id=page_id + 'btn-create', className='button'),
                             href='/dashapp/analysis/create'),
                    dbc.Button('Copy', id=page_id + 'btn-copy', className='button'),
                    dbc.Button('Delete', id=page_id + 'btn-delete', className='button'),
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    datatable,
                ]),
            ]),
        ], className='div-standard'),
    ]),


# Add a modal to ask the user to confirm the deletion
@callback(
    Output(page_id + 'datatable', 'data'),
    Output(page_id + 'datatable', 'selected_rows'),
    Input(page_id + 'btn-delete', 'n_clicks'),
    State(page_id + 'datatable', 'selected_row_ids'),
)
def delete_analysis(n_clicks, selected_row_ids):
    if n_clicks is None or selected_row_ids is None:
        raise PreventUpdate

    for analysis_id in selected_row_ids:
        analysis_to_del = Analysis.query.get_or_404(analysis_id)
        db.session.delete(analysis_to_del)
        db.session.commit()

    analyses = query_to_list(Analysis.query.all())

    # Create links to analysis
    for analysis in analyses:
        for col in ['quote', 'name']:
            analysis[col] = '[' + analysis[col] + '](/dashapp/analysis/view/' + str(analysis['id']) + ')'

    df = pd.DataFrame(analyses)
    data = df.to_dict('records')

    return data, []
