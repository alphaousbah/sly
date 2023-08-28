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
                        label='Menu',
                        className='me-auto',  # The following navitems will be on the right of navbar
                    ),
                    dbc.NavLink('Link 4', href='#'),
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


def header_nav(module):
    directory_name = get_directory(module)['directory']
    page_name = get_directory(module)['page']

    if page_name != directory_name:
        string_title = 'VAV Agro SL 2024 / ' + directory_name.capitalize() + ' / ' + page_name.capitalize()
    else:
        string_title = 'VAV Agro SL 2024 / ' + directory_name.capitalize()

    title = html.H5(string_title, className='title')

    nav_middle = dbc.Nav([
        dbc.NavLink([
            html.Div(page['name'], className='ms-2'),
        ],
            href=page['relative_path'], active='exact'
        )
        for page in dash.page_registry.values()
        if page_navloc(page['path']) == 'middle'
    ],
        pills=True,
        className='nav_middle',
    )

    nav_bottom = dbc.Nav([
        dbc.NavLink([
            html.Div(page['name'], className='ms-2'),
        ],
            href=page['relative_path'],
            active='exact'
        )
        for page in dash.page_registry.values()
        if page_navloc(page['path']) == 'bottom' and str(page['path']).startswith('/' + directory_name)
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


def page_navloc(pathname):
    # Step 1: Look for the pages that need to be put on the top nav
    page_name = str(pathname).split('/')[-1]

    if page_name in ['search', 'create']:
        return 'top'
    # Step 2: Put hte other pages in middle or bottom nav
    else:
        count_slash = str(pathname).count('/')
        match count_slash:
            case 1:
                # The pathname has only one slash : the module is in the pages directory
                return 'middle'
            case 2:
                # The pathname has 2 slashes : the module is in a subdirectory of the pages directory
                return 'bottom'


def get_id_page(module):
    directory_name = get_directory(module)['directory']
    page_name = get_directory(module)['page']

    if page_name != directory_name:
        id_page = directory_name + '-' + page_name + '-'
    else:
        id_page = page_name

    return id_page


def query_to_list(query):
    # https://stackoverflow.com/questions/1958219/how-to-convert-sqlalchemy-row-object-to-a-python-dict
    return [{col.name: str(getattr(record, col.name)) for col in record.__table__.columns} for record in query]
