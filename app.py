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

disasters_df = pd.read_csv("DATA101-Disasters-Mapping\data\data101_disasters.csv")
adaptability_score_df = pd.read_csv('DATA101-Disasters-Mapping\data\data101_finalz_adaptability_score.csv')
pop_density_df = pd.read_csv('DATA101-Disasters-Mapping\data\data101_pop_density.csv')
timeseries_df = pd.read_csv('DATA101-Disasters-Mapping\data\data101_timeseries.csv')
beneficiaries_df = pd.read_csv('DATA101-Disasters-Mapping\data\data101_beneficiaries_df.csv')
disaster_by_haztype_df = pd.read_csv('DATA101-Disasters-Mapping\data\data101_disaster_by_haztype.csv')

choropleth_options = ["Disasters", "Population Density"]
score_options = ["Adaptability Score", "Indicators"]

month_mapping = {
    '01': 'January',
    '02': 'February',
    '03': 'March',
    '04': 'April',
    '05': 'May',
    '06': 'June',
    '07': 'July',
    '08': 'August',
    '09': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December'
}

# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.FLATLY]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = dbc.Container([
    dbc.Row([
        html.Div("Mapping Adaptive Capacities of Disaster Prone Areas by Evaluating Vulnerabilities through Poverty Indicators (2020)", className="text-primary text-center fs-3")
    ], style={'margin-bottom': '20px'}),
    
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
    ], style={'margin-bottom': '20px'}), 
    
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                choropleth_options,
                'Disasters',
                id='choropleth_radio',
            ),
            dcc.Loading(
                id="choropleth-loading",
                type="circle",
                children=dcc.Graph(id='choropleth')
            ),
        ], width=5),
        dbc.Col([
            
            dbc.Row([
                    dbc.Col([
                        dcc.RadioItems(
                        score_options,
                        'Adaptability Score',
                        id='score_radio',
                        ),
                        dcc.Loading(
                            id="adaptability_score-loading",
                            type="circle",
                            children=dcc.Graph(id='adaptability_score')
                            ),
                        
                    ], width=4),

                    dbc.Col([
                            dcc.Loading(
                            id="bar_haztype-loading",
                            type="circle",
                            children=dcc.Graph(id='bar_haztype')
                            ),
                    ], width=8),
                ])
            
        ], width=7),

    ]),
    dbc.Row([
        dbc.Col([
                dcc.Loading(
                id="hazTypeMonth_line-loading",
                type="circle",
                children=dcc.Graph(id='hazTypeMonth_line')
                ),
                ], width=6),
            
        dbc.Col([
                dcc.Loading(
                id="benefits_cluster-loading",
                type="circle",
                children=dcc.Graph(id='benefits_cluster')
                ),
        ], width=6),
    ]),
    


], fluid=True)

# Add controls to build the interaction

@app.callback(
    Output('haztype_dropdown', 'options'),
    Input('hazcategory_dropdown', 'value'))
def set_haztype_options(selected_category):
    return [{'label': i, 'value': i} for i in timeseries_df[timeseries_df['Hazard Category'] == selected_category]['Hazard Type'].unique()]

# Choropleth 
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
        color_choice = "Blues"
    elif radio == "Population Density": # Population Density
        dff = pop_density_df.copy()
        target = "Population Density"
        color_choice = "OrRd"
    
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
                           color_continuous_scale=color_choice)
    fig.update_geos(fitbounds="locations", visible=False)


    return fig

# Adaptability Score
# - bar graph (y - score; x - indicators)
@app.callback(
    Output("adaptability_score", "figure"),
        [Input("region_dropdown", "value"),
        Input("score_radio", "value")]
    )
def adaptability_score(region, radio):

    dff = adaptability_score_df.copy()
    reg="PH"
    
    
    if region is not None:
        reg = region

    if radio == "Adaptability Score":
        # data
        adpt_score = adaptability_score_df[(adaptability_score_df['Region'] == reg) & (adaptability_score_df['Score Type'] == 'Adaptability Score')]['Score'].values[0]
        progress = adpt_score
        df = pd.DataFrame({'names' : ['score',' '],
                        'values' :  [progress, 5 - progress]})

        # plotly
        fig = px.pie(df, values='values', names='names', hole=0.8,
                    color_discrete_sequence=['blue', 'white']) 
        fig.update_layout(showlegend=False)
        fig.update_traces(textinfo='none')
        fig.data[0].textfont.color = 'white'
        fig.add_annotation(text=str(adpt_score), x=0.5, y=0.5, font=dict(color='black', size=20), showarrow=False)

    elif radio == "Indicators": 
        filtered_score = adaptability_score_df[(adaptability_score_df['Region'] == reg) & (adaptability_score_df['Score Type'] != 'Adaptability Score')]
        fig = px.bar(filtered_score.sort_values(by='Score', ascending=True), x="Score", y="Score Type", orientation='h')


    return fig


# Hazard Types and Frequency
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


    fig = px.bar(dff, x="Count", y=target, color="Hazard Type", orientation='h')
    fig.update_layout(yaxis_title="Number of Disasters per Hazard Type")
    fig.update_layout(barmode='stack')

    return fig

# Received Benefits
@app.callback(
    Output("benefits_cluster", "figure"),
    [Input("region_dropdown", "value")]
)
def benefits_cluster(region):
    
    target = "Region"
    dff = beneficiaries_df.copy()
    
    if region is not None:
        dff = dff[dff['Region'] == region]
        target = "Income Classification"

    fig = px.bar(dff, x=target, y="Percentage", color="Income Classification",
                text="Percentage", # Specify the column containing text to display on bars
                labels={"Percentage": "% of Households"}) # Set the label for the text

    # Set the chart title
    fig.update_layout(title="% Households that RECEIVED Benefits per Income Bracket (2020)")

    # Set the y-axis title
    fig.update_yaxes(title="% of Households")


    return fig

# Hazard Type and Count per Month
@app.callback(
    Output("hazTypeMonth_line", "figure"),
    [Input("region_dropdown", "value"),
    Input("haztype_dropdown", "value")]
)
def hazTypeMonth_line(region, haztype):


    filtered_timeseries = timeseries_df.copy()

    if region is not None:
        filtered_timeseries = filtered_timeseries[filtered_timeseries['Region'] == region]

        
    if haztype is not None:
        filtered_timeseries = filtered_timeseries[filtered_timeseries['Hazard Type'] == haztype]
    

    time_series = filtered_timeseries[["adm1_psgc", "Date of Event (start)", "Hazard Type"]]

    # Change dtype to datetime
    time_series['Date of Event (start)'] = pd.to_datetime(time_series['Date of Event (start)'])
    
    # Group by month and hazard type
    format_time_series = time_series.groupby([time_series['Date of Event (start)'].dt.strftime('%m'), "Hazard Type"])["Hazard Type"].count().sort_values().reset_index(name='Count')
    format_time_series = format_time_series.sort_values(by='Date of Event (start)', ascending=True)

    # Step 3: Change Numeric Month Format to Character (e.g., 01 = Jan)
    format_time_series['Date of Event (start)'] = format_time_series['Date of Event (start)'].map(month_mapping)

    # Create line plot
    fig = px.line(format_time_series, x='Date of Event (start)', y='Count', color='Hazard Type', markers=True)
    fig.update_layout(
        title="Line Plot - Regions and Hazard Category",
        yaxis_title="Number of Disasters",
        yaxis_range=[0, 15]
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)