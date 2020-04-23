import pandas as pd
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

from app import app


rev = pd.read_csv('Assets/Revenues - Sheet1.csv')
# Remove newline char from columns
rev.columns = [col.replace("\n", "") for col in rev.columns]
# Set index to years
rev = rev.set_index('Year')

mand = pd.read_csv('Assets/Mandatory Outlays - Sheet1.csv')
# Remove newline char from columns
mand.columns = [col.replace("\n", "") for col in mand.columns]
# Set index to years
mand = mand.set_index('Year')
# Fill n.a.
mand['Medicarea'] = mand['Medicarea'].replace('n.a.', 0)

dis = pd.read_csv('Assets/Discretionary Outlays  - Sheet1.csv')
# Remove newline char from columns
dis.columns = [col.replace("\n", "") for col in dis.columns]
# Set index to years
dis = dis.set_index('Year')


def get_sankey_nodes(year):
    rev_cols = rev.columns.to_list()[:-1]
    mand_cols = mand.columns.to_list()[:-2]
    dis_cols = dis.columns.to_list()[:-1]

    node_cols = [str(year)] + rev_cols + mand_cols + dis_cols
    return node_cols


def get_sankey_links(year, node_cols):
    # Get revenue links
    rev_cols = rev.columns.to_list()[:-1]
    mand_cols = mand.columns.to_list()[:-2]
    dis_cols = dis.columns.to_list()[:-1]

    node_cols = [str(year)] + rev_cols + mand_cols + dis_cols
    rev_links = []
    for col in rev_cols:
        source = node_cols.index(col)
        target = node_cols.index(str(year))
        value = rev.loc[year, col]
        color = '#b8ffcb'
        rev_links.append((source, target, value, color))

    # Get mand links
    mand_links = []
    for col in mand_cols:
        source = node_cols.index(str(year))
        target = node_cols.index(col)
        value = mand.loc[year, col]
        color = '#ffc65c'
        mand_links.append((source, target, value, color))

    # Get dis links
    dis_links = []
    for col in dis_cols:
        source = node_cols.index(str(year))
        target = node_cols.index(col)
        value = dis.loc[year, col]
        color = '#8ffdff'
        dis_links.append((source, target, value, color))

    link_df = pd.DataFrame(rev_links + mand_links + dis_links,
                           columns = ['sources', 'targets', 'values', 'colors'])
    return link_df

fig_frames = []
for year in rev.index:
    node_cols = get_sankey_nodes(year)
    link_df = get_sankey_links(year, node_cols)
    fig_frames.append(go.Frame(data=[
        go.Sankey(
            node = dict(
                pad = 15,
                thickness = 20,
                line = dict(color = "black", width = 0.5),
                label = node_cols,
                color = "#cfcfcf"
            ),
            link = dict(
                source = link_df['sources'],
                target = link_df['targets'],
                value = link_df['values'],
                label = link_df['values'],
                color = link_df['colors']
            )
        )]
    ))


node_cols = get_sankey_nodes(1962)
link_df = get_sankey_links(1962, node_cols)


fig = go.Figure(
    data = [go.Sankey(
            node = dict(
                pad = 15,
                thickness = 20,
                line = dict(color = "black", width = 0.5),
                label = node_cols,
                color = "#cfcfcf"
            ),
            link = dict(
                source = link_df['sources'],
                target = link_df['targets'],
                value = link_df['values'],
                label = link_df['values'],
                color = link_df['colors']
            )
        )],
    layout = dict(
        title_text = "Congressional Fiscal Policy",
        updatemenus = [dict(
            type = "buttons",
            buttons = [dict(
                label = "Play",
                method = "animate",
                args = [None]
                )]
        )]),
    frames = fig_frames
)



column1 = dbc.Col(
    [
        dcc.Markdown(
            """
            # Federal Fiscal Policy
            """
        ),
        html.Div(
            id = 'div_4',
            style={'marginBottom': 25, 'marginTop': 25}
        ),
        dcc.Markdown(
            """
            Federal fiscal policy is the means by which the U.S. Government raises funds and distributes them.
            """
        ),
    ], width = 5,
)

column2 = dbc.Col([
            dcc.Graph(
                id = 'plot',
                figure = fig,
                config = {'displayModeBar': False},
            ),
])

layout = [dbc.Row([column1, column2])]
