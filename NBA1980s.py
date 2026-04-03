import pandas as pd
import numpy as np
from mysql.connector import Error
from openpyxl import load_workbook
from sqlalchemy import create_engine

def read_season_data(season_year):
    file_path = f"/Users/Kevin/Documents/NBA 1980's Data/NBA_{season_year}.xlsx"
    sheet_names = ["PerGame", "Totals", "Advanced"]
    season_dataframes = {}
    xls = pd.ExcelFile(file_path)  # Open the Excel file once and query its sheet names

    for sheet in sheet_names:
        if sheet in xls.sheet_names:  # Check if the sheet exists
            season_dataframes[sheet] = pd.read_excel(file_path, sheet_name=sheet)
        else:
            print(f"Sheet '{sheet}' not found in {file_path}. Skipping...")
    return season_dataframes


def analyze_season_data(season_year):
    season_data = read_season_data(season_year)

    # PerGame Data Cleansing and Analysis
    per_game_data = season_data["PerGame"]
    """
    In the 1980-1981 season, there is a lack of recordable data regarding who started.
    There is also the fact that  who started is not as important as the number of minutes they played. 
    There have been instances of someone who does not start averaging more minutes than a starter. 
    Kevin Mchale,a power forward for the Boston Celtics won two 6th man of the year awards in the 
    1980's has  averaged more minutes than Cedric Maxwell, a starter for the Boston Celtics.
    Therefore the game started (GS column will be removed). 
    """
    # Remove GS column
    if 'GS' in per_game_data.columns:
        per_game_data = per_game_data.drop(columns=['GS'])

    """
    Some of the data regarding 3 point shots is incorrect, and  not properly filled. I'll mark
    all players who have not attemped a three with a 3P% value of zero. This is not mathematically
    correct, but this is insignificant as not attempting a three is equivalent to not making three
    as they both add no value to their teams 
    """
    # Make 3P% value null if there were no 3's attempted along with no 3's made
    per_game_data.loc[(per_game_data['3P'] == 0) & (per_game_data['3PA'] == 0), '3P%'] = np.nan

    #Totals Data Cleansing
    totals_data = season_data["Totals"]
    # Replicate the 3P% adjustment logic for Totals sheet
    totals_data.loc[(totals_data['3P'] == 0) & (totals_data['3PA'] == 0), '3P%'] = 0

    #Advanced Data Cleansing
    advanced_data = season_data["Advanced"]
    #Remove empty columns
    advanced_data = advanced_data.dropna(axis=1, how='all')

    # Update the season_data dictionary with cleansed data
    season_data["PerGame"] = per_game_data
    season_data["Totals"] = totals_data
    season_data["Advanced"]= advanced_data

    return season_data
def save_dataframe_to_excel(dataframes, season_year, base_path="/Users/Kevin/Documents/NBA 1980's Data/"):
    filename = f"{base_path}Cleansed_NBA_{season_year}.xlsx"
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)



# Define seasons to analyze
season_years = ['1980-1981', '1981-1982', '1982-1983', '1983-1984', '1984-1985',
                '1985-1986', '1986-1987', '1987-1988', '1988-1989', '1989-1990']

# Store analyzed data for each season
analyzed_seasons_data = {}

for season_year in season_years:
    analyzed_seasons_data[season_year] = analyze_season_data(season_year)
    cleansed_data = analyze_season_data(season_year)
    save_dataframe_to_excel(cleansed_data, season_year)

"""
Export this data into MYSQL to do further cleansing, and analysis
and analysis.   
"""
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='nba_1980s',
            user='root',
            password='2566Tofu$'
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

def analyze_season_data(df, season_year):
    df['Season'] = season_year  # Add the season year to each row
    df = df.drop(columns=['GS'], errors='ignore')
    return df


def clean_dataframe(df):
    # Remove 'Unnamed' columns if they exist
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # Example: Fill NaN values with 0 or another appropriate value
    df.fillna(0, inplace=True)
    return df

def export_to_sql(engine, dataframe, table_name):
    dataframe.to_sql(table_name, con=engine, if_exists='append', index=False)

def read_and_export_season_data(season_years):
    engine = create_engine('mysql+mysqlconnector://root:2566Tofu$@localhost/nba_1980s')

    for season_year in season_years:
        prefix = "Cleansed_"
        file_path = f"/Users/Kevin/Documents/NBA 1980's Data/{prefix}NBA_{season_year}.xlsx"
        sheet_names = ["PerGame", "Totals", "Advanced"]
        table_map = {
            'PerGame': 'PerGame',
            'Totals': 'Totals',
            'Advanced': 'AdvancedStats'
        }

        for sheet_name, table_name in table_map.items():
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            export_to_sql(engine, df, table_name)

        print(f"Data from {season_year} exported successfully.")

# Define seasons to analyze
season_years = ['1980-1981', '1981-1982', '1982-1983', '1983-1984', '1984-1985',
                '1985-1986', '1986-1987', '1987-1988', '1988-1989', '1989-1990']

# Export data
read_and_export_season_data(season_years)
