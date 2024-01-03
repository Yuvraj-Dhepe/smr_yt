import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Bar Plots using dropdown list
def dynamic_bar_plot(df):
    # Create JupyterDash app
    app = dash.Dash(__name__)

    # Unique channels and years for dropdown options
    channels_options = [{'label': channel, 'value': channel} for channel in df['channelTitle'].unique()]
    years_options = [{'label': year, 'value': year} for year in df['publishingYear'].unique()]

    # Layout of the app
    app.layout = html.Div([
        html.H1("Monthly Views by Channel"),
        dcc.Dropdown(
            id='channel-dropdown',
            options=channels_options,
            value=[channels_options[0]['value']],  # Default to the first channel
            multi=True,
            style={'width': '50%'}
        ),
        dcc.Dropdown(
            id='year-dropdown',
            options=years_options,
            value=years_options[0]['value'],  # Default to the first year
            multi=False,
            style={'width': '50%'}
        ),
        dcc.Graph(id='bar-chart'),
        html.Div(id='line-chart-container')  # Container for the line chart
    ])

    # Callback to update the bar chart based on dropdown selection
    @app.callback(
        Output('bar-chart', 'figure'),
        [Input('channel-dropdown', 'value'),
        Input('year-dropdown', 'value')]
    )
    def update_bar_chart(selected_channels, selected_year):
        filtered_df = df[(df['channelTitle'].isin(selected_channels)) &
                        (df['publishingYear'] == selected_year)]

        traces = []
        for channel in selected_channels:
            channel_data = filtered_df[filtered_df['channelTitle'] == channel]
            trace = go.Bar(
                x=channel_data['publishingMonthName'],
                y=channel_data['viewCount'],
                name=channel
            )
            traces.append(trace)

        layout = go.Layout(
            barmode='group',
            title=f'Monthly Views for Year {selected_year} for Selected Channels',
            xaxis=dict(title='Month'),
            yaxis=dict(title='Total Views')
        )

        return {'data': traces, 'layout': layout}

    # Callback to update the line chart based on dropdown selection
    @app.callback(
        Output('line-chart-container', 'children'),
        [Input('channel-dropdown', 'value')]
    )
    def update_line_chart(selected_channels):
        traces = []
        for channel in selected_channels:
            channel_data = df[df['channelTitle'] == channel].groupby('publishingYear')['viewCount'].sum().reset_index()
            trace = go.Scatter(
                x=channel_data['publishingYear'],
                y=channel_data['viewCount'],
                mode='lines+markers',
                name=channel
            )
            traces.append(trace)

        layout = go.Layout(
            title='Yearly Trend of Total Views for Selected Channels',
            xaxis=dict(title='Year'),
            yaxis=dict(title='Total Views')
        )

        line_chart = dcc.Graph(
            id='line-chart',
            figure={'data': traces, 'layout': layout}
        )

        return [line_chart]

    return app

# Plot that has toggle buttons of channelLists
def toggle_dynamic_bar_plot(df):
    app = dash.Dash(__name__)
    
    # Unique channels and years for dropdown options
    channels_options = [{'label': channel, 'value': channel} for channel in df['channelTitle'].unique()]
    years_options = [{'label': year, 'value': year} for year in df['publishingYear'].unique()]

    # Layout of the app
    app.layout = html.Div([
        html.H1("Monthly Views by Channel"),
        dcc.Checklist(
            id='channel-toggle',
            options=channels_options,
            value=[channels_options[0]['value']],  # Default to the first channel
            inline=True,
            style={'columnCount': 6}
        ),
        dcc.Dropdown(
            id='year-dropdown',
            options=years_options,
            value=years_options[0]['value'],  # Default to the first year
            multi=False,
            style={'width': '50%'}
        ),
        dcc.Graph(id='bar-chart'),
        html.Div(id='line-chart-container')  # Container for the line chart
    ])

    # Callback to update the bar chart based on dropdown selection
    @app.callback(
        Output('bar-chart', 'figure'),
        [Input('channel-toggle', 'value'),
        Input('year-dropdown', 'value')]
    )
    def update_bar_chart(selected_channels, selected_year):
        filtered_df = df[(df['channelTitle'].isin(selected_channels)) &
                        (df['publishingYear'] == selected_year)]

        traces = []
        for channel in selected_channels:
            channel_data = filtered_df[filtered_df['channelTitle'] == channel]
            trace = go.Bar(
                x=channel_data['publishingMonthName'],
                y=channel_data['viewCount'],
                name=channel
            )
            traces.append(trace)

        layout = go.Layout(
            barmode='group',
            title=f'Monthly Views for Year {selected_year} for Selected Channels',
            xaxis=dict(title='Month'),
            yaxis=dict(title='Total Views')
        )

        return {'data': traces, 'layout': layout}

    # Callback to update the line chart based on dropdown selection
    @app.callback(
        Output('line-chart-container', 'children'),
        [Input('channel-toggle', 'value')]
    )
    def update_line_chart(selected_channels):
        traces = []
        for channel in selected_channels:
            channel_data = df[df['channelTitle'] == channel].groupby('publishingYear')['viewCount'].sum().reset_index()
            trace = go.Scatter(
                x=channel_data['publishingYear'],
                y=channel_data['viewCount'],
                mode='lines+markers',
                name=channel
            )
            traces.append(trace)

        layout = go.Layout(
            title='Yearly Trend of Total Views for Selected Channels',
            xaxis=dict(title='Year'),
            yaxis=dict(title='Total Views')
        )

        line_chart = dcc.Graph(
            id='line-chart',
            figure={'data': traces, 'layout': layout}
        )

        return [line_chart]

    return app


# Multiple Plots based on channel Selection
def create_bar_plot(filtered_df, title):
    traces = []
    for channel in filtered_df['channelTitle'].unique():
        channel_data = filtered_df[filtered_df['channelTitle'] == channel]
        trace = go.Bar(
            x=channel_data['publishingMonthName'],
            y=channel_data['viewCount'],
            name=channel
        )
        traces.append(trace)

    layout = go.Layout(
        barmode='group',
        title=title,
        xaxis=dict(title='Month'),
        yaxis=dict(title='Total Views')
    )

    return {'data': traces, 'layout': layout}

def create_line_plot(filtered_df, title):
    traces = []
    for channel in filtered_df['channelTitle'].unique():
        channel_data = filtered_df[filtered_df['channelTitle'] == channel]

        # Aggregate data by summing up views for each month
        aggregated_data = channel_data.groupby('publishingYear').agg({'viewCount': 'sum'}).reset_index()

        trace = go.Scatter(
            x=aggregated_data['publishingYear'],
            y=aggregated_data['viewCount'],
            mode='lines+markers',
            name=channel
        )
        traces.append(trace)

    layout = go.Layout(
        title=title,
        xaxis=dict(title='Year'),
        yaxis=dict(title='Total Views')
    )

    return {'data': traces, 'layout': layout}

def dynamic_plots(df, channel_titles):
    # Create JupyterDash app with suppress_callback_exceptions=True
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    pop_channels = [{'label': title, 'value': title} for title in df[df['pop_unpop'] == 1]['channelTitle'].unique()]
    unpop_channels = [{'label': title, 'value': title} for title in df[df['pop_unpop'] == 0]['channelTitle'].unique()]
    # Layout of the app
    app.layout = html.Div([
        html.H1("Monthly and Yearly Views by Channel"),
        
        html.Div([
            html.H3("Select Channels"),
            
            # Checklists for Popular and Unpopular Channels
            dcc.Checklist(
                id='channel-checklist-popular',
                options=pop_channels,
                value=[pop_channels[0]['value']],  # Default to the first channel
                inline=True,
                style={'width': '50%', 'columnCount': 3, 'rowCount': 2, 'marginLeft': 20}
            ),
            
            dcc.Checklist(
                id='channel-checklist-unpopular',
                options=unpop_channels,
                value=[unpop_channels[0]['value']],  # Default to the first channel
                inline=True,
                style={'width': '50%', 'columnCount': 3, 'rowCount': 2, 'marginLeft': 20}
            ),
        ]),
        html.Div([
            html.H3("Select Years"),
            dcc.Checklist(
                id='year-checklist-bar-plots',
                options=[{'label': year, 'value': year} for year in df['publishingYear'].unique()],
                value=df['publishingYear'].unique(),  # Default to all years
                inline=True,
                style={'width': '50%', 'columnCount': 6, 'rowCount': 3, 'marginTop':20}
            ),
        ]),
        dcc.Graph(id='bar-plot-a'),
        dcc.Graph(id='bar-plot-b'),
        dcc.Graph(id='line-plot-a'),
        dcc.Graph(id='line-plot-b'),
        dcc.Graph(id='line-plot-c'),
    ])

    # Callback to update bar plots
    @app.callback(
        [Output('bar-plot-a', 'figure'),
         Output('bar-plot-b', 'figure')],
        [Input('channel-checklist-popular', 'value'),
         Input('channel-checklist-unpopular', 'value'),
         Input('year-checklist-bar-plots', 'value')]
    )
    def update_bar_plots(selected_channels, selected_years):
        filtered_df_popular = df[(df['pop_unpop'] == 1) & (df['channelTitle'].isin(selected_channels)) & (df['publishingYear'].isin(selected_years))]
        bar_plot_a = create_bar_plot(filtered_df_popular, title=f'Monthly Views for Popular Channels')

        filtered_df_unpopular = df[(df['pop_unpop'] == 0) & (df['channelTitle'].isin(selected_channels)) & (df['publishingYear'].isin(selected_years))]
        bar_plot_b = create_bar_plot(filtered_df_unpopular, title=f'Monthly Views for Unpopular Channels')

        return bar_plot_a, bar_plot_b

    # Callback to update line plots
    @app.callback(
        [Output('line-plot-a', 'figure'),
         Output('line-plot-b', 'figure'),
         Output('line-plot-c', 'figure')],
        [Input('channel-checklist', 'value')]
    )
    def update_line_plots(selected_channels):
        filtered_df_popular = df[(df['pop_unpop'] == 1) & (df['channelTitle'].isin(selected_channels))]
        line_plot_a = create_line_plot(filtered_df_popular, title=f'Yearly Trend for Popular Channels')

        filtered_df_unpopular = df[(df['pop_unpop'] == 0) & (df['channelTitle'].isin(selected_channels))]
        line_plot_b = create_line_plot(filtered_df_unpopular, title=f'Yearly Trend for Unpopular Channels')

        all_channels = df[df['channelTitle'].isin(selected_channels)]
        line_plot_c = create_line_plot(all_channels, title=f'Yearly Trend for All Selected Channels')

        return line_plot_a, line_plot_b, line_plot_c

    return app