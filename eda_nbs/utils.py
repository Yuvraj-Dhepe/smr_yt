import pandas as pd
from dateutil import parser
import isodate
def add_pop_unpop_col(df: pd.DataFrame, pop: bool) -> pd.DataFrame:
    """
    Add column to dataframe with values 1 for popular channels and 0 for unpopular channels
    """
    if pop:
        df['pop_unpop'] = 1
    else:
        df['pop_unpop'] = 0
    return df


def combine_pop_unpop_df(pop_df:pd.DataFrame, unpop_df:pd.DataFrame) -> pd.DataFrame:
    """
    Combine popular and unpopular dataframes into one dataframe
    """
    df = pd.concat([pop_df, unpop_df], ignore_index=True, axis = 0)
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
    
    
def parse_cols(df: pd.DataFrame) -> pd.DataFrame:
    # Apply the parsing function to the 'publishedAt' column
    df['publishedAt'] = df['publishedAt'].apply(parse_published_at)

    # Drop rows with parsing errors and show the count
    num_dropped_rows = df['publishedAt'].isna().sum()
    print(f"Parser dropped {num_dropped_rows} rows")
    df.dropna(subset=['publishedAt'], inplace=True)

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
    df['durationSecs'] = df['duration'].apply(lambda x: isodate.parse_duration(x))
    df['durationSecs'] = df['durationSecs'].astype('timedelta64[s]')
    df.drop(['duration'],axis = 1, inplace=True)
    
    
    # Parse the tags column
    df['tagsstr'] = df.tags.apply(lambda x: 0 if x is None else str((x))) #tags were not in proper format so converting them to str
    df['tagsCount'] = df.tagsstr.apply(lambda x: 0 if (x == 0 or x =='nan') else len(eval(x)))
    df.drop(['tags'],axis = 1, inplace=True) 
    
    # Comments and likes per 1000 view ratio
    df['likeRatio'] = df['likeCount']/ df['viewCount'] * 1000
    df['commentRatio'] = df['commentCount']/ df['viewCount'] * 1000
    
    # Title character length
    df['titleLength'] = df['title'].apply(lambda x: len(x))
    

    return df
    
def remove_outliers(df, channel_column='channelTitle', year_column='publishingYear', month_column='publishingMonthName', views_column='viewCount', threshold=1.5):
    """
    Remove outliers for each channel, for each month, and for all years.

    Parameters:
    - df: DataFrame containing the data.
    - channel_column: Name of the column containing channel titles.
    - year_column: Name of the column containing publishing years.
    - month_column: Name of the column containing publishing months.
    - views_column: Name of the column containing view counts.
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

            # Iterate over unique months
            for month in year_df[month_column].unique():
                month_df = year_df[year_df[month_column] == month]

                # Calculate the IQR (Interquartile Range)
                q1 = month_df[views_column].quantile(0.25)
                q3 = month_df[views_column].quantile(0.75)
                iqr = q3 - q1

                # Define the upper and lower bounds to identify outliers
                lower_bound = q1 - threshold * iqr
                upper_bound = q3 + threshold * iqr

                # Remove outliers
                month_df_no_outliers = month_df[(month_df[views_column] >= lower_bound) & (month_df[views_column] <= upper_bound)]

                # Append the result to the final DataFrame
                df_no_outliers = pd.concat([df_no_outliers, month_df_no_outliers])

    return df_no_outliers