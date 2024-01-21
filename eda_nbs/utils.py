import isodate
import pandas as pd
from dateutil import parser


def add_pop_unpop_col(df: pd.DataFrame, pop: bool) -> pd.DataFrame:
    """
    Add column to dataframe with values 1 for popular channels and 0 for unpopular channels
    """
    if pop:
        df['pop_unpop'] = 1
    else:
        df['pop_unpop'] = 0
    return df


def combine_pop_unpop_df(pop_df: pd.DataFrame, unpop_df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine popular and unpopular dataframes into one dataframe
    """
    df = pd.concat([pop_df, unpop_df], ignore_index=True, axis=0)
    return df


def split_and_merge_by_views(df):
    # Split the original dataframe into two based on 'pop_unpop'
    df_pop = df[df['pop_unpop'] == 1]
    df_unpop = df[df['pop_unpop'] == 0]

    # Calculate the average number of views for each group
    avg_views_pop = df_pop['views'].mean()
    avg_views_unpop = df_unpop['views'].mean()

    # Function to create chunks based on average views
    def create_chunks(df, avg_views):
        chunk1 = df[df['views'] < avg_views]
        chunk2 = df[df['views'] >= avg_views]
        return chunk1, chunk2

    # Create chunks for popular and unpopular dataframes
    chunk1_pop, chunk2_pop = create_chunks(df_pop, avg_views_pop)
    chunk1_unpop, chunk2_unpop = create_chunks(df_unpop, avg_views_unpop)

    # Merge the chunks together
    chunk_combined_low_views = pd.concat([chunk1_pop, chunk1_unpop])
    chunk_combined_high_views = pd.concat([chunk2_pop, chunk2_unpop])

    return chunk_combined_low_views, chunk_combined_high_views


def parse_published_at(x):
    try:
        parsed_value = parser.parse(x)
        # Convert parsed_value to timezone-naive if it's timezone-aware
        return parsed_value.replace(tzinfo=None) if parsed_value.tzinfo else parsed_value
    except Exception as e:
        # print(f"Error parsing value: {x}, Error: {e}")
        return None


def parse_count(x):
    try:
        return int(x)
    except ValueError:
        # print(f"Removing row with viewCount as string: {x}")
        return None


def parse_cols(df: pd.DataFrame) -> pd.DataFrame:
    # Print total rows before parsing
    total_rows_before = len(df)
    print(f"Total rows before parsing: {total_rows_before}")

    # Apply the parsing function to the 'publishedAt' column
    df['publishedAt'] = df['publishedAt'].apply(parse_published_at)

    # Drop rows with parsing errors and show the count
    num_dropped_rows_published_at = df['publishedAt'].isna().sum()
    print(
        f"Parser dropped {num_dropped_rows_published_at} rows during 'publishedAt' parsing")

    # Remove rows where 'publishedAt' is not parsed
    df = df.dropna(subset=['publishedAt'])

    # Create publish day (in the week) column
    df['publishDayName'] = df['publishedAt'].apply(lambda x: x.strftime("%A"))

    # Convert 'publishedAt' column to datetime
    df['publishedAt'] = pd.to_datetime(df['publishedAt'])

    # Extract year, month, and time into separate columns
    df['publishingYear'] = df['publishedAt'].dt.year
    df['publishingMonth'] = df['publishedAt'].dt.month
    df['publishingTime'] = df['publishedAt'].dt.time

    # Get month name
    df['publishingMonthName'] = df['publishedAt'].dt.strftime("%B")

    # Dropping the 'publishedAt' column
    df.drop(['publishedAt'], axis=1, inplace=True)

    # Parse the duration column
    df['durationSecs'] = df['duration'].apply(
        lambda x: isodate.parse_duration(x))
    df['durationSecs'] = df['durationSecs'].astype('timedelta64[s]')
    df.drop(['duration'], axis=1, inplace=True)

    # Parse the tags column
    # tags were not in proper format so converting them to str
    df['tagsstr'] = df.tags.apply(lambda x: 0 if x is None else str((x)))
    df['tagsCount'] = df.tagsstr.apply(
        lambda x: 0 if (x == 0 or x == 'nan') else len(eval(x)))
    df.drop(['tags'], axis=1, inplace=True)

    # Apply the parsing function to the 'viewCount' column
    df['viewCount'] = df['viewCount'].apply(parse_count)
    df['likeCount'] = df['likeCount'].apply(parse_count)
    df['commentCount'] = df['commentCount'].apply(parse_count)

    # Drop rows where 'viewCount' is a string
    num_dropped_rows_viewcount = df['viewCount'].isna().sum()
    print(
        f"Parser dropped {num_dropped_rows_viewcount} rows during 'viewCount' parsing")

    # Remove rows where 'viewCount' is 0
    df = df[df['viewCount'] != 0]

    # Comments and likes per 1000 view ratio
    df['likeRatio'] = (df['likeCount'] / df['viewCount']) * 1000
    df['commentRatio'] = (df['commentCount'] / df['viewCount']) * 1000

    # Title character length
    df['titleLength'] = df['title'].apply(lambda x: len(x))

    # Print total rows after parsing
    total_rows_after = len(df)
    print(f"Total rows after parsing: {total_rows_after}")

    return df

# def remove_outliers(df, channel_column='channelTitle', year_column='publishingYear', month_column='publishingMonthName', column='viewCount', threshold=1.5):
#     """
#     Remove outliers for each channel, for each month, and for all years.

#     Parameters:
#     - df: DataFrame containing the data.
#     - channel_column: Name of the column containing channel titles.
#     - year_column: Name of the column containing publishing years.
#     - month_column: Name of the column containing publishing months.
#     - column: Name of the column containing view counts.
#     - threshold: Threshold for detecting outliers (default is 1.5).

#     Returns:
#     - DataFrame with outliers removed.
#     """
#     df_no_outliers = pd.DataFrame()

#     # Iterate over unique channels
#     for channel in df[channel_column].unique():
#         channel_df = df[df[channel_column] == channel]

#         # Iterate over unique years
#         for year in channel_df[year_column].unique():
#             year_df = channel_df[channel_df[year_column] == year]

#             # Iterate over unique months
#             for month in year_df[month_column].unique():
#                 month_df = year_df[year_df[month_column] == month]

#                 # Calculate the IQR (Interquartile Range)
#                 q1 = month_df[column].quantile(0.25)
#                 q3 = month_df[column].quantile(0.75)
#                 iqr = q3 - q1

#                 # Define the upper and lower bounds to identify outliers
#                 lower_bound = q1 - threshold * iqr
#                 upper_bound = q3 + threshold * iqr

#                 # Remove outliers
#                 month_df_no_outliers = month_df[(month_df[column] >= lower_bound) & (
#                     month_df[column] <= upper_bound)]

#                 # Append the result to the final DataFrame
#                 df_no_outliers = pd.concat(
#                     [df_no_outliers, month_df_no_outliers])

#     return df_no_outliers


def remove_outliers(df, channel_column='channelTitle', year_column='publishingYear', column='viewCount', threshold=1.5):
    """
    Remove outliers for each channel and each year.

    Parameters:
    - df: DataFrame containing the data.
    - channel_column: Name of the column containing channel titles.
    - year_column: Name of the column containing publishing years.
    - column: Name of the column containing view counts.
    - threshold: Threshold for detecting outliers (default is 1.5).

    Returns:
    - DataFrame with outliers removed.
    """
    df_no_outliers = pd.DataFrame()

    # Iterate over unique channels
    for channel in df[channel_column].unique():
        channel_df = df[df[channel_column] == channel]

        # Iterate over unique years
        for year in channel_df[year_column].unique():
            year_df = channel_df[channel_df[year_column] == year]

            # Calculate the IQR (Interquartile Range)
            q1 = year_df[column].quantile(0.25)
            q3 = year_df[column].quantile(0.75)
            iqr = q3 - q1

            # Define the upper and lower bounds to identify outliers
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            # Remove outliers
            year_df_no_outliers = year_df[(year_df[column] >= lower_bound) & (
                year_df[column] <= upper_bound)]

            # Append the result to the final DataFrame
            df_no_outliers = pd.concat(
                [df_no_outliers, year_df_no_outliers])

    return df_no_outliers


def pop_unpop_chunks(df):
    # Step 1: Sum up views for each channel
    summed_views_df = df.groupby(['channelTitle', 'pop_unpop'], as_index=False)[
        'viewCount'].sum()

    # Step 2: Find mean views for popular and unpopular channels
    mean_views_popular = summed_views_df[summed_views_df['pop_unpop'] == 1]['viewCount'].mean(
    )
    mean_views_unpopular = summed_views_df[summed_views_df['pop_unpop'] == 0]['viewCount'].mean(
    )

    # Step 3: Create lists based on mean views
    popular_channels = summed_views_df[summed_views_df['pop_unpop']
                                       == 1]['channelTitle']
    unpopular_channels = summed_views_df[summed_views_df['pop_unpop']
                                         == 0]['channelTitle']

    # Separate channels based on mean views
    popular_below_mean = popular_channels[summed_views_df[summed_views_df['pop_unpop']
                                                          == 1]['viewCount'] < mean_views_popular].tolist()
    popular_above_mean = popular_channels[summed_views_df[summed_views_df['pop_unpop']
                                                          == 1]['viewCount'] >= mean_views_popular].tolist()

    unpopular_below_mean = unpopular_channels[summed_views_df[summed_views_df['pop_unpop']
                                                              == 0]['viewCount'] < mean_views_unpopular].tolist()
    unpopular_above_mean = unpopular_channels[summed_views_df[summed_views_df['pop_unpop']
                                                              == 0]['viewCount'] >= mean_views_unpopular].tolist()

    return summed_views_df, mean_views_popular, mean_views_unpopular, popular_below_mean, popular_above_mean, unpopular_below_mean, unpopular_above_mean


def calculate_percentiles_df(df, percentiles, year_column='publishingYear', column='viewCount'):
    percentiles_data_popular = {percentile: {} for percentile in percentiles}
    percentiles_data_unpopular = {percentile: {} for percentile in percentiles}

    for channel in df.channelTitle.unique():
        channel_df = df[df['channelTitle'] == channel]
        for year in channel_df[year_column].unique():
            year_df = channel_df[channel_df[year_column] == year]
            for percentile in percentiles:
                if percentile not in percentiles_data_popular:
                    percentiles_data_popular[percentile] = {}
                if channel not in percentiles_data_popular[percentile]:
                    percentiles_data_popular[percentile][channel] = {}
                if channel_df['pop_unpop'].iloc[0] == 0:
                    # Unpopular channel
                    if percentile not in percentiles_data_unpopular:
                        percentiles_data_unpopular[percentile] = {}
                    if channel not in percentiles_data_unpopular[percentile]:
                        percentiles_data_unpopular[percentile][channel] = {}
                    value = year_df[column].quantile(
                        float(percentile)) / 1_000_000  # Convert to millions
                    percentiles_data_unpopular[percentile][channel][year] = value
                else:
                    # Popular channel
                    value = year_df[column].quantile(
                        float(percentile)) / 1_000_000  # Convert to millions
                    percentiles_data_popular[percentile][channel][year] = value

    # Create DataFrames for popular and unpopular channels
    df_percentiles_popular = pd.DataFrame.from_dict({(i, j): percentiles_data_popular[i][j]
                                                     for i in percentiles_data_popular.keys()
                                                     for j in percentiles_data_popular[i].keys()},
                                                    orient='index')

    df_percentiles_unpopular = pd.DataFrame.from_dict({(i, j): percentiles_data_unpopular[i][j]
                                                       for i in percentiles_data_unpopular.keys()
                                                       for j in percentiles_data_unpopular[i].keys()},
                                                      orient='index')

    # Transpose the DataFrames for better readability
    df_percentiles_popular = df_percentiles_popular.transpose()
    df_percentiles_unpopular = df_percentiles_unpopular.transpose()

    return df_percentiles_popular, df_percentiles_unpopular


def return_means_from_percentiles_for_given_years(df, percentiles, years, year_column='publishingYear', column='viewCount'):
    df_percentiles_popular, df_percentiles_unpopular = calculate_percentiles_df(
        df, percentiles, year_column, column)

    # Calculate means for popular channels
    means_popular = df_percentiles_popular.loc[years].describe()
    means_popular = means_popular.describe().loc[['mean']]
    means_popular = means_popular.rename(index={'mean': 'ViewMean'})
    means_popular = means_popular.transpose()
    means_popular = means_popular.sort_values(by='ViewMean', ascending=True)
    means_popular['pop_unpop'] = 1

    # Calculate cumulative average
    means_popular['cumulative_average'] = means_popular['ViewMean'].expanding().mean()

    # Repeat for unpopular channels
    means_unpopular = df_percentiles_unpopular.loc[years].describe()
    means_unpopular = means_unpopular.describe().loc[['mean']]
    means_unpopular = means_unpopular.rename(index={'mean': 'ViewMean'})
    means_unpopular = means_unpopular.transpose()
    means_unpopular = means_unpopular.sort_values(
        by='ViewMean', ascending=True)
    means_unpopular['pop_unpop'] = 0

    # Calculate cumulative average
    means_unpopular['cumulative_average'] = means_unpopular['ViewMean'].expanding(
    ).mean()

    # Combine both means_popular and means_unpopular into a single DataFrame
    means_df = pd.concat([means_popular, means_unpopular], axis=0)
    return means_df
