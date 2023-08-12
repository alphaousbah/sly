from dash import html, dcc

from flaskapp.dashapp import df

# https://dash.plotly.com/minimal-app
layout = html.Div([
    html.H1('Gapminder data', style={'textAlign': 'center'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])
