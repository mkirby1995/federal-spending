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


dis = pd.read_csv('Assets/Discretionary Outlays  - Sheet1.csv')
# Remove newline char from columns
dis.columns = [col.replace("\n", "") for col in dis.columns]
# Set index to years
dis = dis.set_index('Year')


mand = pd.read_csv('Assets/Mandatory Outlays - Sheet1.csv')
# Remove newline char from columns
mand.columns = [col.replace("\n", "") for col in mand.columns]
# Set index to years
mand = mand.set_index('Year')
# Fill n.a.
mand['Medicarea'] = mand['Medicarea'].replace('n.a.', 0)


new_dis = dis.drop(columns = ['Total'])
new_mand = mand.drop(columns = ['Total', 'Memorandum: Major Health Care Programs (Net)c'])
spend = new_dis.join(new_mand, how = 'inner')
spend = spend.T
for i in range(1962, 2019):
    spend[i] = spend[i].astype('float')
    spend[i] = spend[i].apply(lambda x: cpi.inflate(x, i))
spend = spend.T


data_cols = spend.drop(columns = ['Offsetting Receipts']).columns.to_list()
years = spend.index.to_list()
inf_adj_spend = go.Figure(data = [go.Bar(name = col, x = years, y = spend[col]) for col in data_cols])
# Change the bar mode
inf_adj_spend.update_layout(barmode='stack')


years = spend.index.to_list()
normalized_spend = go.Figure()
normalized_spend.add_trace(go.Scatter(
    x = years, y = spend['Defense'],
    mode='lines',
    stackgroup='one',
    groupnorm='percent', # sets the normalization for the sum of the stackgroup
    name = 'Defense'
))
for col in spend.columns.to_list()[1:-1]:
    normalized_spend.add_trace(go.Scatter(
        x = years, y = spend[col],
        mode='lines',
        stackgroup='one',
        name = col
    ))
normalized_spend.update_layout(
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
            # Federal Spending
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
                figure = inf_adj_spend,
                config = {'displayModeBar': False},
            ),
], width = 12)

column3 = dbc.Col([
            dcc.Graph(
                id = 'plot',
                figure = normalized_spend,
                config = {'displayModeBar': False},
            ),
], width = 12)

layout = [dbc.Row([column1]),
          dbc.Row([column2]),
          dbc.Row([column3])]
