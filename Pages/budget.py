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

bud = pd.read_csv('Assets/Revenues, Outlays, Deficits, Surpluses, and Debt Held by the Public - Sheet1.csv')
# Remove newline char from columns
bud.columns = [col.replace("\n", "") for col in bud.columns]
# Set index to years
bud = bud.set_index('Year')
bud['Postal Service (Deficit (-) or Surplus)'] = bud['Postal Service (Deficit (-) or Surplus)'].replace('n.a', 0)

sur_def = bud['Total (Deficit (-) or Surplus)'].to_list()
surplus = []
deficit = []
years = range(1962, 2020)

for i in range(len(years)):
    value = sur_def[i]
    adj_value = cpi.inflate(value, years[i])
    if adj_value > 0:
        surplus.append(adj_value)
        deficit.append(0)
    elif adj_value < 0:
        surplus.append(0)
        deficit.append(adj_value)

years = bud.index
sur_def_fig = go.Figure()
sur_def_fig.add_trace(go.Bar(x = years, y = [-1 * i for i in deficit],
                base = deficit,
                marker_color = 'crimson',
                name = 'Deficit'))

sur_def_fig.add_trace(go.Bar(x = years, y = surplus,
                base = 0,
                marker_color = 'lightslategrey',
                name = 'Surplus'
                ))


revenues = bud['Revenues'].to_list()
revs = []
for i in range(len(revenues)):
    revs.append(((revenues[i] - revenues[i - 1]) / revenues[i - 1]) * 100)
outlays = bud['Outlays'].to_list()
outs = []
for i in range(len(outlays)):
    outs.append(((outlays[i] - outlays[i - 1]) / outlays[i - 1]) * 100)
years = bud.index.to_list()

yoy_fig = go.Figure()
yoy_fig.add_trace(go.Scatter(
    x = years[1:],
    y = revs[1:],
    mode = 'lines+markers',
    name = 'Revenue Growth YOY'))

yoy_fig.add_trace(go.Scatter(
    x = years[1:],
    y = outs[1:],
    mode = 'lines+markers',
    name = 'Spending Growth YOY'))


column1 = dbc.Col(
    [
        dcc.Markdown(
            """
            # The Federal Budget
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
                figure = sur_def_fig,
                config = {'displayModeBar': False},
            ),
], width = 12)

column3 = dbc.Col([
            dcc.Graph(
                id = 'plot',
                figure = yoy_fig,
                config = {'displayModeBar': False},
            ),
], width = 12)

layout = [dbc.Row([column1]),
    dbc.Row([column2]),
    dbc.Row([column3])]
