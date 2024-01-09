import dash
import pandas as pd
import plotly.graph_objs as go
from dash import dcc, html
from dash.dependencies import Input, Output


# Bar Plots using dropdown list
def dynamic_bar_plot(df):
    # Create JupyterDash app
    app = dash.Dash(__name__)

    # Unique channels and years for dropdown options
    channels_options = [{'label': channel, 'value': channel}
                        for channel in df['channelTitle'].unique()]
    years_options = [{'label': year, 'value': year}
                     for year in df['publishingYear'].unique()]

    # Layout of the app
    app.layout = html.Div([
        html.H1("Monthly Views by Channel"),
        dcc.Dropdown(
            id='channel-dropdown',
            options=channels_options,
            # Default to the first channel
            value=[channels_options[0]['value']],
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
            channel_data = df[df['channelTitle'] == channel].groupby(
                'publishingYear')['viewCount'].sum().reset_index()
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
    channels_options = [{'label': channel, 'value': channel}
                        for channel in df['channelTitle'].unique()]
    years_options = [{'label': year, 'value': year}
                     for year in df['publishingYear'].unique()]

    # Layout of the app
    app.layout = html.Div([
        html.H1("Monthly Views by Channel"),
        dcc.Checklist(
            id='channel-toggle',
            options=channels_options,
            # Default to the first channel
            value=[channels_options[0]['value']],
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
            channel_data = df[df['channelTitle'] == channel].groupby(
                'publishingYear')['viewCount'].sum().reset_index()
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


def create_bar_plot(filtered_df, title):
    traces = []
    for channel in filtered_df['channelTitle'].unique():
        channel_data = filtered_df[filtered_df['channelTitle'] == channel]
        trace = go.Bar(
            x=channel_data['publishingMonthName'],
            y=channel_data['likeCount'],
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


def create_bar_plot(filtered_df, title, y_column):
    traces = []
    for channel in filtered_df['channelTitle'].unique():
        channel_data = filtered_df[filtered_df['channelTitle'] == channel]
        trace = go.Bar(
            x=channel_data['publishingMonthName'],
            y=channel_data[y_column],  # Use the selected numerical column
            name=channel
        )
        traces.append(trace)

    layout = go.Layout(
        barmode='group',
        title=title,
        xaxis=dict(title='Month'),
        yaxis=dict(title=f'Total {y_column.capitalize()}')  # Update y-axis title
    )

    return {'data': traces, 'layout': layout}


def create_line_plot(filtered_df, title, y_column):
    traces = []
    for channel in filtered_df['channelTitle'].unique():
        channel_data = filtered_df[filtered_df['channelTitle'] == channel]

        # Assign colors based on popularity
        color = '#FFA500'  # Default color (Orange)
        if channel_data['pop_unpop'].iloc[0] == 0:
            color = '#1F77B4'  # Blue for unpopular channels

        # Aggregate data by summing up the selected numerical column for each month
        aggregated_data = channel_data.groupby(
            'publishingYear').agg({y_column: 'sum'}).reset_index()

        trace = go.Scatter(
            x=aggregated_data['publishingYear'],
            y=aggregated_data[y_column],  # Use the selected numerical column
            mode='lines+markers',
            name=channel,
            line=dict(color=color),
            marker=dict(color=color)
        )
        traces.append(trace)

    layout = go.Layout(
        title=title,
        xaxis=dict(title='Year'),
        yaxis=dict(title=f'Total {y_column.capitalize()}')  # Update y-axis title
    )

    return {'data': traces, 'layout': layout}


def dynamic_view_plots(df):
    # Create JupyterDash app with suppress_callback_exceptions=True
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    pop_titles = [{'label': title, 'value': title}
                  for title in df[df['pop_unpop'] == 1]['channelTitle'].unique()]
    unpop_titles = [{'label': title, 'value': title}
                    for title in df[df['pop_unpop'] == 0]['channelTitle'].unique()]

    numerical_columns = [{'label': column, 'value': column}
                         for column in df.select_dtypes('number').columns]

    # Layout of the app
    app.layout = html.Div([
        html.H1("Monthly and Yearly Views by Channel"),

        # Channel Selection Checklist with Title
        html.Div([
            html.H3("Select Channels"),

            # Checklists for Popular and Unpopular Channels
            dcc.Checklist(
                id='channel-checklist-popular',
                options=pop_titles,
                value=[pop_titles[0]['label']],  # Default to the first channel
                inline=True,
                style={'columnCount': 3, 'rowCount': 2, 'marginTop': 20}
            ),

            dcc.Checklist(
                id='channel-checklist-unpopular',
                options=unpop_titles,
                value=[unpop_titles[0]['label']],
                inline=True,
                style={'columnCount': 3, 'rowCount': 2, 'marginTop': 20}
            ),
        ]),

        # Year Selection Checklist with Title and Spacing
        html.Div([
            html.H3("Select Years"),
            dcc.Checklist(
                id='year-checklist-bar-plots',
                options=[{'label': year, 'value': year}
                         for year in df['publishingYear'].unique()],
                value=df['publishingYear'].unique(),  # Default to all years
                inline=True,
                style={'columnCount': 3, 'rowCount': 2, 'marginTop': 20}
            ),
        ]),

        # Dropdown for selecting numerical column
        html.Div([
            html.H3("Select Numerical Column"),
            dcc.Dropdown(
                id='numerical-column-dropdown',
                options=numerical_columns,
                value=numerical_columns[0]['value'],  # Default to the first numerical column
                style={'width': '50%'}
            ),
        ]),

        dcc.Checklist(
            id='year-checklist-line-plots',
            options=[{'label': year, 'value': year}
                     for year in df['publishingYear'].unique()],
            value=df['publishingYear'].unique(),  # Default to all years
            inline=True,
            style={'columnCount': 3, 'rowCount': 2, 'marginTop': 20}
        ),

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
         Input('year-checklist-bar-plots', 'value'),
         Input('numerical-column-dropdown', 'value')]
    )
    def update_bar_plots(selected_channels_popular, selected_channels_unpopular, selected_years, selected_column):
        filtered_df_popular = df[(df['pop_unpop'] == 1) & (df['channelTitle'].isin(
            selected_channels_popular)) & (df['publishingYear'].isin(selected_years))]
        bar_plot_a = create_bar_plot(
            filtered_df_popular, title=f'Monthly {selected_column.capitalize()} for Popular Channels', y_column=selected_column)

        filtered_df_unpopular = df[(df['pop_unpop'] == 0) & (df['channelTitle'].isin(
            selected_channels_unpopular)) & (df['publishingYear'].isin(selected_years))]
        bar_plot_b = create_bar_plot(
            filtered_df_unpopular, title=f'Monthly {selected_column.capitalize()} for Unpopular Channels', y_column=selected_column)

        return bar_plot_a, bar_plot_b

    # Callback to update line plots
    @app.callback(
        [Output('line-plot-a', 'figure'),
         Output('line-plot-b', 'figure'),
         Output('line-plot-c', 'figure')],
        [Input('channel-checklist-popular', 'value'),
         Input('channel-checklist-unpopular', 'value'),
         Input('year-checklist-line-plots', 'value'),
         Input('numerical-column-dropdown', 'value')]
    )
    def update_line_plots(selected_channels_popular, selected_channels_unpopular, selected_years, selected_column):
        filtered_df_popular = df[(df['pop_unpop'] == 1) & (df['channelTitle'].isin(
            selected_channels_popular)) & (df['publishingYear'].isin(selected_years))]
        line_plot_a = create_line_plot(
            filtered_df_popular, title=f'Yearly Trend for Popular Channels - {selected_column.capitalize()}', y_column=selected_column)

        filtered_df_unpopular = df[(df['pop_unpop'] == 0) & (df['channelTitle'].isin(
            selected_channels_unpopular)) & (df['publishingYear'].isin(selected_years))]
        line_plot_b = create_line_plot(
            filtered_df_unpopular, title=f'Yearly Trend for Unpopular Channels - {selected_column.capitalize()}', y_column=selected_column)

        all_channels = df[(df['channelTitle'].isin(selected_channels_popular)) | (
            df['channelTitle'].isin(selected_channels_unpopular))]
        line_plot_c = create_line_plot(
            all_channels, title=f'Yearly Trend for All Selected Channels - {selected_column.capitalize()}', y_column=selected_column)

        return line_plot_a, line_plot_b, line_plot_c

    return app



def calculate_percentiles(df, channels, percentiles, year_column='publishingYear', views_column='viewCount'):
    percentiles_data = {percentile: {} for percentile in percentiles}

    for channel in channels:
        channel_df = df[df['channelTitle'] == channel]
        for percentile in percentiles:
            if percentile not in percentiles_data:
                percentiles_data[percentile] = {}
            if channel not in percentiles_data[percentile]:
                percentiles_data[percentile][channel] = {'x': [], 'y': []}

            for year in channel_df[year_column].unique():
                year_df = channel_df[channel_df[year_column] == year]
                if not year_df.empty:
                    value = year_df[views_column].quantile(float(percentile))
                    percentiles_data[percentile][channel]['x'].append(year)
                    percentiles_data[percentile][channel]['y'].append(value)

    return percentiles_data


def plot_percentiles(df, channels, percentiles_data, percentile, popular_color='orange', unpopular_color='blue'):
    fig = go.Figure()

    for channel in channels:
        if channel in percentiles_data[percentile]:
            data = percentiles_data[percentile][channel]
            color = popular_color if df[(df['channelTitle'] == channel) & (
                df['pop_unpop'] == 1)].any().any() else unpopular_color

            trace = go.Scatter(
                x=data['x'],
                y=data['y'],
                mode='lines+markers',
                name=f'{channel} - {percentile}',
                line=dict(color=color),
                marker=dict(color=color)
            )
            fig.add_trace(trace)

    fig.update_layout(
        title=f'Percentile {percentile} for Selected Channels Over Years',
        xaxis_title='Year',
        yaxis_title='View Count',
        showlegend=True,
        legend_title='Channels',
    )

    return fig


def percentiles_plot(df, percentiles):
    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.H1("Interactive Percentiles Plot"),
        html.H3("Select Channels"),
        dcc.Checklist(
            id='channel-checklist-popular',
            options=[{'label': title, 'value': title}
                     for title in df[df['pop_unpop'] == 1]['channelTitle'].unique()],
            # Default to the first popular channel
            value=[df[df['pop_unpop'] == 1]['channelTitle'].unique()[0]],
            inline=True,
            style={'columnCount': 3, 'marginTop': 20}
        ),
        html.H3("Select Unpopular Channels"),
        dcc.Checklist(
            id='channel-checklist-unpopular',
            options=[{'label': title, 'value': title}
                     for title in df[df['pop_unpop'] == 0]['channelTitle'].unique()],
            value=[],  # Default to no unpopular channels
            inline=True,
            style={'columnCount': 3, 'marginTop': 20}
        ),
        # Generate dcc.Graph components dynamically
        *[dcc.Graph(id=f'line-plot-pr{percentile.replace(".", "")}') for percentile in percentiles]
    ])

    @app.callback(
        [Output(f'line-plot-pr{percentile.replace(".", "")}', 'figure')
         for percentile in percentiles],
        [Input('channel-checklist-popular', 'value'),
         Input('channel-checklist-unpopular', 'value')]
    )
    def update_percentiles_plot(selected_channels_popular, selected_channels_unpopular):
        selected_channels = selected_channels_popular + selected_channels_unpopular
        percentiles_data = calculate_percentiles(
            df, selected_channels, percentiles)

        # Generate figures for each percentile
        figures = [plot_percentiles(
            df, selected_channels, percentiles_data, percentile) for percentile in percentiles]
        return figures

    return app