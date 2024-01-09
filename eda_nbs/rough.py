import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output


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

# # Example usage
# percentiles = ['.25', '.5', '.75', '.9', '.95', '.99']
# app = percentiles_plot(df, percentiles)
# app.run_server(debug=True, use_reloader=False)

# import dash
# import numpy as np
# import pandas as pd
# import plotly.graph_objects as go
# from dash import dcc, html
# from dash.dependencies import Input, Output


# def calculate_percentiles(df, channels, percentiles, year_column='publishingYear', views_column='viewCount'):
#     percentiles_data = {percentile: {} for percentile in percentiles}

#     for channel in channels:
#         channel_df = df[df['channelTitle'] == channel]
#         for year in channel_df[year_column].unique():
#             year_df = channel_df[channel_df[year_column] == year]
#             for percentile in percentiles:
#                 if percentile not in percentiles_data:
#                     percentiles_data[percentile] = {}
#                 if channel not in percentiles_data[percentile]:
#                     percentiles_data[percentile][channel] = {'x': [], 'y': []}
#                 value = year_df[views_column].quantile(float(percentile))
#                 percentiles_data[percentile][channel]['x'].append(year)
#                 percentiles_data[percentile][channel]['y'].append(value)

#     return percentiles_data


# def plot_percentiles(df, percentiles_data, popular_color='orange', unpopular_color='blue'):
#     fig = go.Figure()

#     for percentile, channels_data in percentiles_data.items():
#         for channel, data in channels_data.items():
#             color = popular_color if df[(df['channelTitle'] == channel) & (
#                 df['pop_unpop'] == 1)].any().any() else unpopular_color

#             trace = go.Scatter(
#                 x=data['x'],
#                 y=data['y'],
#                 mode='lines+markers',
#                 name=f'{channel} - {percentile}',
#                 line=dict(color=color),
#                 marker=dict(color=color)
#             )
#             fig.add_trace(trace)

#     fig.update_layout(
#         title='Percentiles for Selected Channels Over Years',
#         xaxis_title='Year',
#         yaxis_title='View Count',
#         legend_title='Channels and Percentiles'
#     )

#     return fig


# def percentiles_plot(df, percentiles):
#     app = dash.Dash(__name__)

#     app.layout = html.Div([
#         html.H1("Interactive Percentiles Plot"),
#         html.H3("Select Channels"),
#         dcc.Checklist(
#             id='channel-checklist-popular',
#             options=[{'label': title, 'value': title}
#                      for title in df[df['pop_unpop'] == 1]['channelTitle'].unique()],
#             # Default to the first popular channel
#             value=[df[df['pop_unpop'] == 1]['channelTitle'].unique()[0]],
#             inline=True,
#             style={'columnCount': 3, 'marginTop': 20}
#         ),
#         html.H3("Select Unpopular Channels"),
#         dcc.Checklist(
#             id='channel-checklist-unpopular',
#             options=[{'label': title, 'value': title}
#                      for title in df[df['pop_unpop'] == 0]['channelTitle'].unique()],
#             value=[],  # Default to no unpopular channels
#             inline=True,
#             style={'columnCount': 3, 'marginTop': 20}
#         ),
#         dcc.Graph(id='percentiles-plot')
#     ])

#     @app.callback(
#         Output('percentiles-plot', 'figure'),
#         [Input('channel-checklist-popular', 'value'),
#          Input('channel-checklist-unpopular', 'value')]
#     )
#     def update_percentiles_plot(selected_channels_popular, selected_channels_unpopular):
#         selected_channels = selected_channels_popular + selected_channels_unpopular
#         percentiles_data = calculate_percentiles(
#             df, selected_channels, percentiles)
#         return plot_percentiles(df, percentiles_data)

#     return app


# # Example usage
# percentiles = ['.25', '.5', '.75', '.9', '.95', '.99']
# app = percentiles_plot(df, percentiles)
# app.run_server(debug=True, use_reloader=False)


# import dash
# import pandas as pd
# import plotly.graph_objects as go
# from dash import dcc, html
# from dash.dependencies import Input, Output


# def calculate_percentiles(df, channel, percentiles, year_column='publishingYear', views_column='viewCount'):
#     channel_df = df[df['channelTitle'] == channel]
#     percentiles_data = {}

#     for year in channel_df[year_column].unique():
#         year_df = channel_df[channel_df[year_column] == year]
#         percentiles_values = year_df[views_column].quantile(
#             percentiles).tolist()
#         percentiles_data[year] = percentiles_values

#     return pd.DataFrame(percentiles_data, index=percentiles)


# def create_line_plot_from_percentiles(df, percentiles_df, channel, popular_color='orange', unpopular_color='blue'):
#     traces = []

#     for year in percentiles_df.columns:
#         color = popular_color if df[(df['channelTitle'] == channel) & (df['pop_unpop'] == 1) & (
#             df['publishingYear'] == year)].any().any() else unpopular_color

#         trace = go.Scatter(
#             x=percentiles_df.index,
#             y=percentiles_df[year],
#             mode='lines+markers',
#             name=f'{channel} - {year}',
#             line=dict(color=color),
#             marker=dict(color=color)
#         )
#         traces.append(trace)

#     return traces


# def plot_percentiles(df, channels, percentiles, popular_color='orange', unpopular_color='blue'):
#     fig = go.Figure()

#     for channel in channels:
#         percentiles_df = calculate_percentiles(df, channel, percentiles)
#         traces = create_line_plot_from_percentiles(df,
#                                                    percentiles_df, channel, popular_color, unpopular_color)
#         fig.add_traces(traces)

#     fig.update_layout(
#         title='Percentiles for Selected Channels Over Years',
#         xaxis_title='Percentiles',
#         yaxis_title='View Count',
#         legend_title='Channels and Years'
#     )

#     return fig


# def percentiles_plot(df, percentiles):
#     app = dash.Dash(__name__)

#     app.layout = html.Div([
#         html.H1("Interactive Percentiles Plot"),
#         html.H3("Select Channels"),
#         dcc.Checklist(
#             id='channel-checklist-popular',
#             options=[{'label': title, 'value': title}
#                      for title in df[df['pop_unpop'] == 1]['channelTitle'].unique()],
#             # Default to the first popular channel
#             value=[df[df['pop_unpop'] == 1]['channelTitle'].unique()[0]],
#             inline=True,
#             style={'columnCount': 3, 'marginTop': 20}
#         ),
#         html.H3("Select Unpopular Channels"),
#         dcc.Checklist(
#             id='channel-checklist-unpopular',
#             options=[{'label': title, 'value': title}
#                      for title in df[df['pop_unpop'] == 0]['channelTitle'].unique()],
#             value=[],  # Default to no unpopular channels
#             inline=True,
#             style={'columnCount': 3, 'marginTop': 20}
#         ),
#         dcc.Graph(id='percentiles-plot')
#     ])

#     @app.callback(
#         Output('percentiles-plot', 'figure'),
#         [Input('channel-checklist-popular', 'value'),
#          Input('channel-checklist-unpopular', 'value')]
#     )
#     def update_percentiles_plot(selected_channels_popular, selected_channels_unpopular):
#         selected_channels = selected_channels_popular + selected_channels_unpopular
#         return plot_percentiles(df, selected_channels, percentiles)

#     return app
