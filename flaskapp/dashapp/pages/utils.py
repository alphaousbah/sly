import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from sqlalchemy import inspect


def navbar():
    return dbc.Navbar(
        dbc.Container([
            html.A(
                dbc.Row([
                    dbc.Col(html.Img(src='/dashapp/assets/sly-logo.png', height="30px")),
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
                    dbc.NavLink('Search', href='/dashapp/search'),
                    dbc.NavLink('Create', href='/dashapp/create'),
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


def header(title=''):
    return html.Div([
        html.H5(title, className='title'),
    ])


def header_nav(module, analysis_id):
    directory_name = get_directory(module)['directory']
    page_name = get_directory(module)['page']

    if page_name != directory_name:
        string_title = 'VAV Agro SL 2024 | ' + directory_name.capitalize() + ' | ' + page_name.capitalize()
    else:
        string_title = 'VAV Agro SL 2024 | ' + directory_name.capitalize()

    title = html.H5(string_title, className='title')

    nav_middle = dbc.Nav([
        dbc.NavLink([
            html.Div(page['name'], className='ms-2'),
        ],
            href=str(page['relative_path']).replace('none', str(analysis_id)),
            active='exact'
        )
        for page in dash.page_registry.values()
        if get_navloc(page['module']) == 'middle'
    ],
        pills=True,
        className='nav_middle',
    )

    nav_bottom = dbc.Nav([
        dbc.NavLink([
            html.Div(page['name'], className='ms-2'),
        ],
            href=str(page['relative_path']).replace('none', str(analysis_id)),
            active='exact'
        )
        for page in dash.page_registry.values()
        if get_navloc(page['module']) == 'bottom' and str(page['path']).startswith('/' + directory_name)
    ],
        pills=True,
        className='nav_bottom',
    )

    return html.Div([
        title,
        nav_middle,
        nav_bottom,
    ])


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
    index_pages = str(module).index('pages')
    substring = str(module)[index_pages:].split('.')
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


def query_to_list(query):
    # https://stackoverflow.com/questions/1958219/how-to-convert-sqlalchemy-row-object-to-a-python-dict
    return [{col.name: str(getattr(record, col.name)) for col in record.__table__.columns} for record in query]
