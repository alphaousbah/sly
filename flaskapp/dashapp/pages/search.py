import dash
from dash import html, dcc, dash_table, callback, clientside_callback, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flaskapp.dashapp.pages.utils import *
from flaskapp.extensions import db
from flaskapp.models import Analysis
import pandas as pd

dash.register_page(__name__, nav_loc='top')

id_page = get_id_page(__name__)


def layout():
    for page in dash.page_registry.values():
        print(page['path'])
        print(page_navloc(page['path']))

    analyses = query_to_list(Analysis.query.all())
    df = pd.DataFrame(analyses)

    datatable = dash_table.DataTable(
        id=id_page + 'datatable',
        data=df.to_dict('records'),
        columns=[{'name': str(col).capitalize(), 'id': col, "selectable": True} for col in df.columns],
        # columns=[{'id': x, 'name': x, 'presentation': 'markdown'} if x == 'name' else {'id': x, 'name': x} for x in
        #          df.columns],
        # markdown_options={"html": True},
        editable=False,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        row_selectable="multi",
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=10,
        style_table={
            "fontFamily": '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,'
                          '"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol",'
                          '"Noto Color Emoji"'
        },
        style_header={
            'backgroundColor': 'whitesmoke',
            'padding': '0.75rem'
        },
        style_cell={
            "fontFamily": '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,'
                          '"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol",'
                          '"Noto Color Emoji"',
            'fontSize': '13px',
            'lineHeight': '0.7',
            'textAlign': 'left',
            'padding': '0.7rem',
            'border': '1px solid #dee2e6',
        },
        # style_data_conditional=[
        #     {'if': {'column_id': 'id'}, 'width': '10%'},
        # ]
    )

    return html.Div([
        header('Analysis Search'),
        html.Div([
            dbc.Row([
                dbc.Col([
                    dcc.Link(dbc.Button('Create', id=id_page + 'btn-create', className='button'),
                             href='/dashapp/create'),
                    dbc.Button('Copy', id=id_page + 'btn-copy', className='button'),
                    dbc.Button('Delete', id=id_page + 'btn-delete', className='button'),
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
    Output(id_page + 'datatable', 'data'),
    Output(id_page + 'datatable', 'selected_rows'),
    Input(id_page + 'btn-delete', 'n_clicks'),
    State(id_page + 'datatable', 'selected_row_ids'),
)
def delete_analysis(n_clicks, selected_row_ids):
    if n_clicks is None or selected_row_ids is None:
        raise PreventUpdate

    for id in selected_row_ids:
        analysis_to_del = Analysis.query.get_or_404(id)
        db.session.delete(analysis_to_del)
        db.session.commit()

    analyses = query_to_list(Analysis.query.all())
    df = pd.DataFrame(analyses)
    data = df.to_dict('records')

    return data, []
