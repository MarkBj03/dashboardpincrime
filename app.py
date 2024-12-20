import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from sklearn.cluster import KMeans
import base64
import io
import os
import datetime as dt
import datetime
from flask import Flask
today = dt.date.today()
last_7_days = today - dt.timedelta(days=7)
last_month = today - dt.timedelta(days=30)

# Initialize Dash app
server = Flask(__name__)
app = dash.Dash(__name__, server=server, routes_pathname_prefix='/')


# initialy create directory 
if not os.path.exists('uploaded_files'):
    os.makedirs('uploaded_files')

# open the rizalwitht.csv as main data
data = pd.read_csv("rizalwitht.csv", encoding='latin1')
data['DATE COMMITTED'] = pd.to_datetime(data['DATE COMMITTED'], errors='coerce')
data = data.dropna(subset=['LATITUDE', 'LONGITUDE', 'DATE COMMITTED'])

# Kmeans algo clustering
kmeans = KMeans(n_clusters=5, random_state=42)
data['Cluster'] = kmeans.fit_predict(data[['LATITUDE', 'LONGITUDE']])
data['Year'] = data['DATE COMMITTED'].dt.year
data['Month'] = data['DATE COMMITTED'].dt.month
data['Day'] = data['DATE COMMITTED'].dt.day
last_date = data['DATE COMMITTED'].max().date()
start_date = last_date - datetime.timedelta(days=7)
# App Layout
app.layout = html.Div([

    html.Div([
        html.Img(src='/assets/pincrimelogo.png', style={'height': '50px', 'width': '10%', 'marginRight': '10px'}),
        html.H1("Crime Data Analysis Dashboard", style={'textAlign': 'center'}),
        html.P("Explore crime patterns and clusters using data visualizations.",
               style={'textAlign': 'center', 'color': 'gray'})
    ], style={'font-family': 'Arial, sans-serif','padding': '20px', 'backgroundColor': '#f4f4f8'}),

    # Filters Section
    html.Div([
        html.Div([
            html.Label("Select Cluster:",style={'font-family': 'Arial, sans-serif',}),
            dcc.Dropdown(
                id='cluster-filter',
                options=[{'label': f'Cluster {i}', 'value': i} for i in sorted(data['Cluster'].unique())],
                value=None,
                placeholder="Select a cluster",
                multi=True
            )
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px','font-family': 'Arial, sans-serif', 'font-size': '14px'}),

        html.Div([
            html.Label("Crime Type:",style={'font-family': 'Arial, sans-serif',}),
            dcc.Dropdown(
                id='crime-type-filter',
                options=[{'label': crime, 'value': crime} for crime in data['INCIDENT TYPE'].unique()],
                value=None,
                placeholder="Select crime types",
                multi=True
            )
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px','font-family': 'Arial, sans-serif','font-size': '14px',}),

        # Default values for the date range
html.Div([
    # Label for Date Range
    html.Label("Date Range:", style={
        'font-family': 'Arial, sans-serif',
        'font-size': '14px',
        'display': 'inline-block',
        'margin-bottom': '5px'
    }),
    
# Get the last date in the dataset



# Date Range Filter
dcc.DatePickerRange(
    id='date-range-filter',
    start_date=start_date,  # Set to the calculated start date (7 days before the last date)
    end_date=last_date,    # Set to the last date in the dataset by default
    min_date_allowed=data['DATE COMMITTED'].min().date(),
    max_date_allowed=last_date,
    display_format='YYYY-MM-DD',
    style={
        'width': '100%',
        'font-family': 'Arial, sans-serif',
        'font-size': '14px',
        'display': 'inline-block',
        'margin-bottom': '10px'
    }
),
    # Dropdown for Quick Options
html.Label("Filter:", style={
        'font-family': 'Arial, sans-serif',
        'font-size': '14px',
        'display': 'inline-block',
        'margin-bottom': '5px'
    }),
dcc.Dropdown(
    id='quick-select-range',
    options=[
        {'label': 'Last 7 Days', 'value': '7d'},
        {'label': 'Last Month', 'value': '1m'},
        {'label': 'Last 2 Months', 'value': '2m'},
        {'label': 'Last 3 Months', 'value': '3m'},
        {'label': 'Last 4 Months', 'value': '4m'},
    ],
    placeholder="Select range",
    style={
        'width': '69%',
        'font-family': 'Arial, sans-serif',
        'font-size': '14px'
    }
)
], style={
    'width': '30%', 
    'display': 'inline-block',
    'padding': '10px',
    'vertical-align': 'top',
    'box-sizing': 'border-box'
})
    ], style={'borderBottom': '2px solid #ccc', 'padding': '2px'}),

# Summary Metrics Section
html.Div([
    html.H4("Summary Metrics", style={
        'textAlign': 'center',
        'font-family': 'Arial, sans-serif',
        'font-size': '24px',
        'fontWeight': 'bold',
        'margin-bottom': '20px',
        'color': '#333'
    }),
    html.Div([
        # Total Crimes Card
        html.Div([
            html.Div([
                html.Div("🔢", style={  # Add an emoji/icon
                    'font-size': '40px', 
                    'margin-bottom': '10px', 
                    'color': '#4CAF50'
                }),
                html.H5("Total Crimes", style={
                    'font-family': 'Arial, sans-serif', 
                    'color': '#666',
                    'margin-bottom': '5px'
                }),
                html.P(id='total-crimes', style={
                    'fontSize': '24px', 
                    'fontWeight': 'bold', 
                    'color': '#333'
                })
            ], style={
                'padding': '10px',
                'textAlign': 'center'
            })
        ], style={
            'flex': '1',
            'max-width': '300px',  # Ensure all cards have the same width
            'backgroundColor': '#fff',
            'border': '1px solid #ddd',
            'borderRadius': '10px',
            'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)',
            'margin': '10px',
            'padding': '20px'
        }),

        # Most Common Crime Card
        html.Div([
            html.Div([
                html.Div("🚨", style={  # Add an emoji/icon
                    'font-size': '40px', 
                    'margin-bottom': '10px', 
                    'color': '#FF5722'
                }),
                html.H5("Most Common Crime", style={
                    'font-family': 'Arial, sans-serif', 
                    'color': '#666',
                    'margin-bottom': '5px'
                }),
                html.P(id='common-crime', style={
                    'fontSize': '24px', 
                    'fontWeight': 'bold', 
                    'color': '#333'
                })
            ], style={
                'padding': '10px',
                'textAlign': 'center'
            })
        ], style={
            'flex': '1',
            'max-width': '300px',  # Ensure all cards have the same width
            'backgroundColor': '#fff',
            'border': '1px solid #ddd',
            'borderRadius': '10px',
            'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)',
            'margin': '10px',
            'padding': '20px'
        }),

        # Most Affected Area Card
        html.Div([
            html.Div([
                html.Div("📍", style={  # Add an emoji/icon
                    'font-size': '40px', 
                    'margin-bottom': '10px', 
                    'color': '#2196F3'
                }),
                html.H5("Most Affected Area", style={
                    'font-family': 'Arial, sans-serif', 
                    'color': '#666',
                    'margin-bottom': '5px'
                }),
                html.P(id='affected-area', style={
                    'fontSize': '24px', 
                    'fontWeight': 'bold', 
                    'color': '#333'
                })
            ], style={
                'padding': '10px',
                'textAlign': 'center'
            })
        ], style={
            'flex': '1',
            'max-width': '300px',  # Ensure all cards have the same width
            'backgroundColor': '#fff',
            'border': '1px solid #ddd',
            'borderRadius': '10px',
            'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)',
            'margin': '10px',
            'padding': '20px'
        }),
    ], style={
        'display': 'flex',
        'justifyContent': 'space-evenly',  # Evenly distribute the cards
        'align-items': 'stretch',  # Ensure all cards have the same height
        'flex-wrap': 'wrap',  # Allow wrapping on smaller screens
        'marginTop': '20px'  # Add some margin on top of the section
    })
], style={
    'backgroundColor': '#f9f9f9',
    'padding': '20px',
    'borderRadius': '10px',
    'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)',
    'marginTop': '20px'
})

,

    # Converting the data into graphs and etc
    html.Div([
        html.Div([ 
            dcc.Graph(id='map-view')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            dcc.Graph(id='crime-type-bar')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ]),

    html.Div([
        html.Div([ 
            dcc.Graph(id='time-trend')
        ], style={'width': '100%', 'padding': '10px'})
    ]),

    # File upload section
    html.Div([
        html.Label("Upload CSV or Excel File:", style={'fontWeight': 'bold','font-family': 'Arial, sans-serif'}),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                html.Button('Upload File', style={'backgroundColor': '#FF0000', 'color': 'white', 'padding': '10px 20px', 'border': 'none', 'cursor': 'pointer'}),
                html.P("Drag and drop or click to select a file", style={'marginTop': '10px','font-family': 'Arial, sans-serif'})
            ]),
            multiple=False
        ),
        html.Div(id='output-data-upload'),
    ], style={'padding': '20px', 'textAlign': 'center'}),

    # Footer Section
    html.Div([
        html.P("Data Source: PNP Crime Records | PinCrime Dashboard",
               style={'textAlign': 'center', 'color': 'gray','font-family': 'Arial, sans-serif', 'font-size': '14px'})
    ], style={'borderTop': '2px solid #ccc', 'padding': '10px', 'marginTop': '20px','font-family': 'Arial, sans-serif', 'font-size': '14px'})
])

# Callback to handle file upload
@app.callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def save_uploaded_file(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        try:
            if filename.endswith('.csv'):
                try:
                    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                except UnicodeDecodeError:
                    df = pd.read_csv(io.StringIO(decoded.decode('latin1')))
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return html.Div([html.H5("Invalid file type. Please upload a CSV or XLSX file.")])

            file_path = os.path.join('uploaded_files', f"uploaded_{filename}")
            df.to_csv(file_path, index=False)

            return html.Div([
                html.H5(f"File {filename} uploaded successfully."),
                html.Hr(),
                html.Div(f"File saved as {file_path}")
            ])
        except Exception as e:
            return html.Div([html.H5("There was an error processing this file."), html.Div(f"Error: {str(e)}")])
    return html.Div("No file uploaded yet.",style={'font-family': 'Arial, sans-serif'})
@app.callback(
    [Output('quick-select-range', 'value'),
     Output('date-range-filter', 'start_date'),
     Output('date-range-filter', 'end_date')],
    [Input('quick-select-range', 'value'),
     Input('date-range-filter', 'start_date'),
     Input('date-range-filter', 'end_date')]
)
def update_date_range(selected_range, start_date, end_date):
    """ Update date range and dropdown based on selection """

    # If there is a custom date range (i.e., start_date or end_date is set), don't override it with quick select
    if start_date and end_date:
        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()

    # If no quick select range is selected
    if not selected_range:
        return selected_range, start_date, end_date

    # Calculate new start_date and end_date based on quick select
    if selected_range == '7d':
        start_date = last_date - dt.timedelta(days=7)
    elif selected_range == '1m':
        start_date = last_date - dt.timedelta(days=30)
    elif selected_range == '2m':
        start_date = last_date - dt.timedelta(days=60)
    elif selected_range == '3m':
        start_date = last_date - dt.timedelta(days=90)
    elif selected_range == '4m':
        start_date = last_date - dt.timedelta(days=120)
    else:
        start_date = last_date

    return selected_range, start_date, last_date



# Callback for updating visuals
@app.callback(
    [Output('map-view', 'figure'),
     Output('crime-type-bar', 'figure'),
     Output('time-trend', 'figure'),
     Output('total-crimes', 'children'),
     Output('common-crime', 'children'),
     Output('affected-area', 'children')],
    [Input('cluster-filter', 'value'),
     Input('crime-type-filter', 'value'),
     Input('date-range-filter', 'start_date'),
     Input('date-range-filter', 'end_date'),
     Input('crime-type-bar', 'clickData')]
)
def update_visuals(selected_clusters, selected_crime_types, start_date, end_date, bar_click):
    filtered_data = data.copy()

    # Filter by selected clusters, crime types, and date range
    if selected_clusters:
        filtered_data = filtered_data[filtered_data['Cluster'].isin(selected_clusters)]
    if selected_crime_types:
        filtered_data = filtered_data[filtered_data['INCIDENT TYPE'].isin(selected_crime_types)]
    if start_date and end_date:
        filtered_data = filtered_data[(filtered_data['DATE COMMITTED'] >= start_date) & (filtered_data['DATE COMMITTED'] <= end_date)]

    # If a crime type is clicked in the bar chart, filter for that crime
    

    # Map visualization
    map_fig = px.scatter_mapbox(
        filtered_data, 
        lat='LATITUDE', 
        lon='LONGITUDE', 
        color='Cluster',
        mapbox_style="carto-positron", 
        zoom=10, 
        title="Crime Clusters"
    )
    map_fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            zoom=10,
            center=dict(lat=filtered_data['LATITUDE'].mean(), lon=filtered_data['LONGITUDE'].mean())
        )
    )
    

    # Bar chart for crime types
    top_n = 10
    top_crimes = filtered_data.groupby('INCIDENT TYPE').size().nlargest(top_n).reset_index(name='Count')
    top_crimes = top_crimes.sort_values('Count', ascending=True)

    # Define the percentiles for binning
    percentiles = [
        top_crimes['Count'].min(),
        top_crimes['Count'].quantile(0.2),  # 20th percentile
        top_crimes['Count'].quantile(0.4),  # 40th percentile
        top_crimes['Count'].quantile(0.6),  # 60th percentile
        top_crimes['Count'].quantile(0.8),  # 80th percentile
        top_crimes['Count'].max()
    ]

    # Remove duplicates by converting to a set and back to a list, then sort the values
    percentiles = sorted(set(percentiles))

    # Define the categories for crime severity
    categories = ['Very Low Crime', 'Low Crime', 'Medium Crime', 'High Crime', 'Very High Crime']

    # Assign the crime severity using pd.cut, with duplicates='drop' to handle any duplicate edges
    top_crimes['Crime Severity'] = pd.cut(
        top_crimes['Count'], 
        bins=percentiles, 
        labels=categories, 
        include_lowest=True,
        duplicates='drop'  # Drop any duplicate bin edges
    )

    # Create the bar chart with color representing Crime Severity
    bar_fig = px.bar(
        top_crimes,
        y='INCIDENT TYPE', x='Count', 
        title=f"Top {top_n} Crime Type Distribution",
        orientation='h',
        color='Crime Severity',  # Map the color to the 'Crime Severity' column
        color_discrete_map={
            'Very Low Crime': 'blue', 
            'Low Crime': 'lightblue',
            'Medium Crime': 'yellow',
            'High Crime': 'orange',
            'Very High Crime': 'red'
        },
        labels={'Count': 'Crime Count', 'INCIDENT TYPE': 'Incident Type'}  # Optional: add labels for clarity
    )

    # Customizing the color legend labels based on crime severity
    bar_fig.update_layout(
        coloraxis_colorbar=dict(
            title="Crime Severity",  # Change the title of the colorbar
            tickvals=[0, 1, 2, 3, 4],  # Map tick values to the categories (0 to 4)
            ticktext=['Very Low Crime', 'Low Crime', 'Medium Crime', 'High Crime', 'Very High Crime'],  # Map the tick values to the custom labels
            showticksuffix="last",  # Remove numerical suffixes like counts
            ticks="outside",  # Make the ticks outside of the bar
            tickmode="array"  # Make sure to use the specified array of tick labels
        ),
        showlegend=True  # Ensure the legend shows up
    )

    # Time trend visualization
    trend_fig = px.line(
        filtered_data.groupby('DATE COMMITTED').size().reset_index(name='Count'),
        x='DATE COMMITTED', y='Count', title="Crime Trends Over Time"
    )

    # Group by month to get crime totals per month for the selected date range
    filtered_data['YearMonth'] = filtered_data['DATE COMMITTED'].dt.to_period('M')  # Group by year and month
    monthly_crimes = filtered_data.groupby('YearMonth').size()

    # Format the month names and totals
    monthly_crime_text = "\n".join([f"{month.strftime('%B %Y')}: {count} crimes" for month, count in monthly_crimes.items()])

    # Summary metrics
    total_crimes = len(filtered_data)
    common_crime = filtered_data['INCIDENT TYPE'].mode()[0] if not filtered_data.empty else "N/A"
    affected_area = filtered_data['BARANGAY'].mode()[0] if not filtered_data.empty else "N/A"

    return map_fig, bar_fig, trend_fig, monthly_crime_text, common_crime, affected_area

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Use Render's provided port
    app.run_server(host='0.0.0.0', port=port)

