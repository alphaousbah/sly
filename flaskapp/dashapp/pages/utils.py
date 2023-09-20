"""
This module defines functions for generating components commonly used in a Dash web application,
such as navigation bars, page titles, and navigation menus.

Functions:
- `get_nav_top`: Generates the top navigation bar with links and a logo.
- `get_title`: Generates the page title based on the module and analysis name.
- `get_nav_middle`: Generates a navigation menu for the middle section of the page.
- `get_nav_bottom`: Generates a navigation menu for the bottom section of the page.
- `get_directory`: Extracts the directory and page names from a module string.
- `get_navloc`: Determines the navigation location based on the page name.
- `get_page_id`: Generates a unique page ID based on the directory and page names.
- `query_to_list`: Converts a SQLAlchemy query result to a list of dictionaries.

"""

# TODO: Update the doctring
import dash
from dash import html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd


def get_nav_top():
    return dbc.Navbar(
        dbc.Container([
            html.A(
                dbc.Row([
                    dbc.Col(html.Img(src='/dashapp/assets/logo-ccrre.png', height="30px")),
                    dbc.Col(dbc.NavbarBrand('SLy', className="ms-2")),
                ],
                    align='center',
                    className='g-0',
                ),
                href='#',
                style={'textDecoration': 'none'},
            ),
            dbc.NavbarToggler(id='navbar-toggler', n_clicks=0),
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavLink('Search', href='/dashapp/'),
                    dbc.NavLink('Create Analysis', href='/dashapp/analysis/create'),
                    dbc.DropdownMenu(
                        [
                            dbc.DropdownMenuItem('Entry 1'),
                            dbc.DropdownMenuItem('Entry 2'),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem('Entry 3'),
                        ],
                        nav=True,
                        in_navbar=True,
                        label='Dropdown',
                        className='me-auto',  # The following navitems will be on the right of the navbar
                    ),
                    dbc.NavLink('add@flask.login', href='#'),
                ],
                    className='w-100',
                ),
                id='navbar-collapse',
                is_open=False,
                navbar=True,
            ),
        ],
            fluid=True,
        ),
        color='dark',
        dark=True,
        className='mb-1',
    )


def get_title(module, analysis_name=None):
    directory_name = get_directory(module)['directory']
    page_name = get_directory(module)['page']

    if page_name != directory_name:
        string_title = analysis_name + ' | ' + directory_name.capitalize() + ' | ' + page_name.capitalize()
    else:
        string_title = analysis_name + ' | ' + directory_name.capitalize()

    title = html.Div(
        html.H5(string_title, className='title')
    )

    return title


def get_nav_middle(module, analysis_id):
    directory_name = get_directory(module)['directory']

    nav_middle = dbc.Nav([
        dbc.NavLink(
            str(chapter).capitalize(),
            href=f'/dashapp/{chapter}/view/{analysis_id}',
            active=(chapter == directory_name),
        )
        for chapter in ['analysis', 'data', 'model', 'results']
    ],
        pills=True,
        className='nav_middle',
    )

    return nav_middle


def get_nav_bottom(module, analysis_id):
    directory_name = get_directory(module)['directory']

    nav_bottom = dbc.Nav([
        dbc.NavLink(
            page['name'],
            href=str(page['relative_path']).replace('none', str(analysis_id)),
            active='exact'
        )
        for page in dash.page_registry.values()
        if get_navloc(page['module']) == 'bottom' and str(page['path']).startswith('/' + directory_name)
    ],
        pills=True,
        className='nav_bottom',
    )

    return html.Div(nav_bottom)


def get_directory(module):
    # # Run this script to understand the code of the function
    # module1 = 'flaskapp.dashapp/pages.data'
    # module2 = 'flaskapp.dashapp/pages.data.premiums'
    #
    # index_pages_module1 = module1.index('pages')
    # index_pages_module2 = module2.index('pages')
    #
    # directory1 = str(module1[index_pages_module1:]).split('.')[1]
    # directory2 = str(module2[index_pages_module2:]).split('.')[1]
    #
    # page1 = str(module1[index_pages_module1:]).split('.')[-1]
    # page2 = str(module2[index_pages_module2:]).split('.')[-1]
    #
    # print(directory1)  # data = the directory name we want
    # print(directory2)  # data = the directory name we want
    #
    # print(page1)  # data = the page name we want
    # print(page2)  # premiums = the page name we want
    index_string_pages = str(module).index('pages')
    substring = str(module)[index_string_pages:].split('.')
    directory_name = substring[1]
    page_name = substring[-1]

    return {'directory': directory_name, 'page': page_name}


def get_navloc(module):
    page_name = str(module).split('.')[-1]

    match page_name:
        case 'search' | 'create':
            return 'top'
        case 'analysis' | 'data' | 'model' | 'results':
            return 'middle'
        case _:
            return 'bottom'


def get_page_id(module):
    directory_name = get_directory(module)['directory']
    page_name = get_directory(module)['page']

    if page_name != directory_name:
        page_id = directory_name + '-' + page_name + '-'
    else:
        page_id = page_name

    return page_id


def df_from_query(query):
    # https://stackoverflow.com/questions/1958219/how-to-convert-sqlalchemy-row-object-to-a-python-dict
    list_from_query = [{col.name: str(getattr(record, col.name)) for col in record.__table__.columns} for record in
                       query]
    df = pd.DataFrame(list_from_query)

    return df


def get_table_analyses(component_id, query):
    if query:
        df = df_from_query(query)

        # Create Markdown links to open an analysis from the table
        for col in ['quote', 'name']:
            df[col] = '[' + df[col] + '](/dashapp/analysis/view/' + df['id'].astype(str) + ')'

        return dash_table.DataTable(
            id=component_id,
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
            css=get_datatable_css(),
            style_header=get_datatable_style_header(),
            style_cell=get_datatable_style_cell(),
            style_data_conditional=[
                # Disable highlighting active cell
                {'if': {'state': 'selected'}, 'backgroundColor': 'inherit !important', 'border': 'inherit !important'},
            ]
        )

    return None


def get_table_layers(component_id, query):
    if query:
        df = df_from_query(query)

        return dash_table.DataTable(
            id=component_id,
            data=df.to_dict('records'),
            columns=[{'id': col, 'name': str(col).capitalize()} for col in df.columns],
            hidden_columns=['id', 'analysis_id'],
            sort_by=[{'column_id': 'id', 'direction': 'asc'}],
            editable=True,
            filter_action='none',
            sort_action='native',
            sort_mode='multi',
            row_selectable='multi',
            selected_rows=[],
            page_action='native',
            page_current=0,
            page_size=5,
            css=get_datatable_css(),
            style_header=get_datatable_style_header(),
            style_cell=get_datatable_style_cell(),
            style_data_conditional=[],
        )

    return None


def get_table_lossfiles(component_id, query):
    if query:
        df = df_from_query(query)

        return dash_table.DataTable(
            id=component_id,
            data=df.to_dict('records'),
            columns=[{'id': col, 'name': str(col).capitalize()} for col in df.columns],
            hidden_columns=['id', 'analysis_id'],
            sort_by=[{'column_id': 'id', 'direction': 'asc'}],
            editable=False,
            filter_action='native',
            sort_action='native',
            sort_mode='multi',
            row_selectable='multi',
            selected_rows=[],
            page_action='native',
            page_current=0,
            page_size=5,
            css=get_datatable_css(),
            style_header=get_datatable_style_header(),
            style_cell=get_datatable_style_cell(),
            style_data_conditional=[],
        )

    return None


def get_table_losses(component_id, query):
    if query:
        df = df_from_query(query)

        return dash_table.DataTable(
            id=component_id,
            data=df.to_dict('records'),
            columns=[{'id': col, 'name': str(col).capitalize()} for col in df.columns],
            hidden_columns=['id', 'loss_set_id'],
            sort_by=[{'column_id': 'year', 'direction': 'asc'}],
            editable=False,
            filter_action='none',
            sort_action='native',
            sort_mode='multi',
            row_selectable=False,
            selected_rows=[],
            page_action='native',
            page_current=0,
            page_size=10,
            css=get_datatable_css(),
            style_header=get_datatable_style_header(),
            style_cell=get_datatable_style_cell(),
            style_data_conditional=[],
        )

    return None


def get_datatable_style_header():
    return {
        'backgroundColor': 'whitesmoke',
        'padding': '0.5rem'
    }


def get_datatable_css():
    return [
        {'selector': 'p', 'rule': 'margin: 0'},
        {'selector': '.show-hide', 'rule': 'display: none'}
    ]


def get_datatable_style_cell():
    return {
        'fontFamily': '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,'
                      '"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol",'
                      '"Noto Color Emoji"',
        'fontSize': '13px',
        'lineHeight': '1.5',
        'textAlign': 'left',
        'padding': '0.5rem',
        'border': '1px solid #dee2e6',
    }
