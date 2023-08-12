from dash import Input, Output, State
import plotly.express as px

from flaskapp.dashapp import df


def register_callbacks(dashapp):
    @dashapp.callback(
        Output('graph-content', 'figure'),
        Input('dropdown-selection', 'value')
    )
    def update_graph(value):
        dff = df[df.country == value]
        return px.line(dff, x='year', y='pop')
