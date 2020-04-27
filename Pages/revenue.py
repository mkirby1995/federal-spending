import pandas as pd
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import cpi
cpi.update()

from app import app

rev = pd.read_csv('Assets/Revenues - Sheet1.csv')
# Remove newline char from columns
rev.columns = [col.replace("\n", "") for col in rev.columns]
# Set index to years
rev = rev.set_index('Year')


# Adjust for inflation
rev = rev.T
for i in range(1962, 2019):
    rev[i] = rev[i].apply(lambda x: cpi.inflate(x, i))
rev = rev.T


data_cols = rev.drop(columns = ['Total']).columns.to_list()
years = rev.index.to_list()
inf_adj_rev = go.Figure(data = [go.Bar(name = col, x = years, y = rev[col]) for col in data_cols])
# Change the bar mode
inf_adj_rev.update_layout(barmode='stack')


years = rev.index.to_list()
normalized_rev = go.Figure()
normalized_rev.add_trace(go.Scatter(
    x = years, y = rev['Individual Income Taxes'],
    mode='lines',
    stackgroup='one',
    groupnorm='percent', # sets the normalization for the sum of the stackgroup
    name = 'Individual Income Taxes'
))
for col in rev.columns.to_list()[1:-1]:
    normalized_rev.add_trace(go.Scatter(
        x = years, y = rev[col],
        mode='lines',
        stackgroup='one',
        name = col
    ))
normalized_rev.update_layout(
    showlegend=True,
    xaxis_type='category',
    yaxis=dict(
        type='linear',
        range=[1, 100],
        ticksuffix='%'))


column1 = dbc.Col(
    [
        dcc.Markdown(
            """
            # Federal Revenues
            """
        ),
        html.Div(
            id = 'div_4',
            style={'marginBottom': 25, 'marginTop': 25}
        ),
        dcc.Markdown(
            """
            """
        ),
    ], width = 12,
)

column2 = dbc.Col([
            dcc.Graph(
                id = 'plot',
                figure = inf_adj_rev,
                config = {'displayModeBar': False},
            ),
], width = 12)

column3 = dbc.Col([
            dcc.Graph(
                id = 'plot',
                figure = normalized_rev,
                config = {'displayModeBar': False},
            ),
], width = 12)

layout = [dbc.Row([column1]),
    dbc.Row([column2]),
    dbc.Row([column3])]
