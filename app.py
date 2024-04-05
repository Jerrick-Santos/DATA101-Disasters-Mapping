# Import package
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import json
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from pathlib import Path



# Incorporate data

# Load GeoJson
# Opening JSON file
f = open("DATA101-Disasters-Mapping\data\DATA101_MAP_DATA.geojson")
map_data = json.load(f)

disasters_df = pd.read_csv("DATA101-Disasters-Mapping\data\data101_adaptability_score.csv")
adaptability_score_df = pd.read_csv('DATA101-Disasters-Mapping\data\data101_disasters.csv')
pop_density_df = pd.read_csv('DATA101-Disasters-Mapping\data\data101_pop_density.csv')
timeseries_df = pd.read_csv('DATA101-Disasters-Mapping\data\data101_timeseries.csv')
beneficiaries_df = pd.read_csv('DATA101-Disasters-Mapping\data\data101_beneficiaries_df.csv')
disaster_by_haztype_df = pd.read_csv('DATA101-Disasters-Mapping\data\data101_disaster_by_haztype.csv')

choropleth_options = ["Disasters", "Population Density"]

# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.FLATLY]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = dbc.Container([
    dbc.Row([
        html.Div('Dashboard', className="text-primary text-center fs-3")
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H5("Region"),
            dcc.Dropdown(
                id="region_dropdown", 
                options=[{'label': reg, 'value': reg} for reg in sorted(disasters_df['Region'].unique())],
            )
        ], width=6),
        dbc.Col([
            html.H5("Hazard Category"),
            dcc.Dropdown(
                id="hazcategory_dropdown", 
                options=[{'label': category, 'value': category} for category in sorted(timeseries_df['Hazard Category'].unique())],
            )
        ], width=3),
        dbc.Col([
            html.H5("Hazard Type"),
            dcc.Dropdown(id='haztype_dropdown')
        ], width=3)
    ]), 
    
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                choropleth_options,
                'Disasters',
                id='choropleth_radio',
            ),
            dcc.Loading(
                id="choropleth-loading",
                type="default",
                children=dcc.Graph(id='choropleth')
            ),
        ], width=6),
        dbc.Col([
            
            dbc.Row([
                    dbc.Col([
                        html.Div('Adaptability Score', className="text-primary text-center fs-3")
                    ], width=6),
                    dbc.Col([
                        html.Div('Hazard Type Bar', className="text-primary text-center fs-3"),
                        dcc.Graph(id='bar_haztype')
                    ], width=6),
                ]),
            
            dbc.Row([
                html.Div('Timeseries Line', className="text-primary text-center fs-3")
                ]),
            
            dbc.Row([
                html.Div('Beneficiaries Bar', className="text-primary text-center fs-3")
                ]),
            
        ], width=6),

    ]),
    


], fluid=True)

# Add controls to build the interaction

@callback(
    Output('haztype_dropdown', 'options'),
    Input('hazcategory_dropdown', 'value'))
def set_haztype_options(selected_category):
    return [{'label': i, 'value': i} for i in timeseries_df[timeseries_df['Hazard Category'] == selected_category]['Hazard Type'].unique()]


@app.callback(
    Output("choropleth", "figure"),
    [Input("region_dropdown", "value"),
     Input("hazcategory_dropdown", "value"),
     Input("haztype_dropdown", "value"),
     Input("choropleth_radio", "value")]
)
def choropleth(region, hazcategory, haztype, radio):
    
    if radio == "Disasters":
        dff = disasters_df.copy()
        target = "Total Disasters"
    elif radio == "Population Density": # Population Density
        dff = pop_density_df.copy()
        target = "Population Density"
    
    if region is not None:
        dff = dff[dff['Region'] == region]

    if hazcategory is not None and haztype is None and radio == "Disasters": 
        target = hazcategory
    elif hazcategory is not None and haztype is not None and radio == "Disasters":
        target = haztype

    fig = px.choropleth(dff,
                           geojson=map_data,
                           locations="Region",
                           color=target,
                            featureidkey="properties.Region",
                           color_continuous_scale='Blues')
    fig.update_geos(fitbounds="locations", visible=False)


    return fig


@app.callback(
    Output("bar_haztype", "figure"),
    [Input("region_dropdown", "value"),
     Input("haztype_dropdown", "value")]
)
def haztype_bar(region, haztype):
    
    target = "Region"
    dff = disaster_by_haztype_df.copy()
    
    if region is not None:
        dff = dff[dff['Region'] == region]
        target = "Hazard Type"
        
    if haztype is not None:
        dff = dff[dff['Hazard Type'] == haztype]


    fig = px.bar(dff, x=target, y="Count", color="Hazard Type")
    fig.update_layout(yaxis_title="Number of Disasters per Hazard Type")
    fig.show()


    return fig


if __name__ == '__main__':
    app.run_server()