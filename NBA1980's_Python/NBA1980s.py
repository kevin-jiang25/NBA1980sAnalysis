from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

BASE_DATA_PATH = Path("/Users/Kevin/Documents/NBA 1980's Data")
RAW_FILE_TEMPLATE = "NBA_{season_year}.xlsx"
CLEAN_FILE_TEMPLATE = "Cleansed_NBA_{season_year}.xlsx"

SEASON_YEARS = [
    "1980-1981",
    "1981-1982",
    "1982-1983",
    "1983-1984",
    "1984-1985",
    "1985-1986",
    "1986-1987",
    "1987-1988",
    "1988-1989",
    "1989-1990",
]

SHEET_NAMES = ["PerGame", "Totals", "Advanced"]
TABLE_MAP = {"PerGame": "PerGame", "Totals": "Totals", "Advanced": "AdvancedStats"}
SQLALCHEMY_URL = "mysql+mysqlconnector://root:2566Tofu$@localhost/nba_1980s"


def raw_file_path(season_year: str) -> Path:
    return BASE_DATA_PATH / RAW_FILE_TEMPLATE.format(season_year=season_year)


def clean_file_path(season_year: str) -> Path:
    return BASE_DATA_PATH / CLEAN_FILE_TEMPLATE.format(season_year=season_year)


def read_season_data(season_year: str) -> dict[str, pd.DataFrame]:
    file_path = raw_file_path(season_year)
    season_dataframes: dict[str, pd.DataFrame] = {}

    xls = pd.ExcelFile(file_path)
    for sheet in SHEET_NAMES:
        if sheet in xls.sheet_names:
            season_dataframes[sheet] = pd.read_excel(file_path, sheet_name=sheet)
        else:
            print(f"Sheet '{sheet}' not found in {file_path}. Skipping...")

    return season_dataframes


def clean_per_game_data(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    if "GS" in result.columns:
        result = result.drop(columns=["GS"])
    result.loc[(result["3P"] == 0) & (result["3PA"] == 0), "3P%"] = np.nan
    return result


def clean_totals_data(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result.loc[(result["3P"] == 0) & (result["3PA"] == 0), "3P%"] = 0
    return result


def clean_advanced_data(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(axis=1, how="all")


def clean_season_data(season_year: str) -> dict[str, pd.DataFrame]:
    season_data = read_season_data(season_year)

    season_data["PerGame"] = clean_per_game_data(season_data["PerGame"])
    season_data["Totals"] = clean_totals_data(season_data["Totals"])
    season_data["Advanced"] = clean_advanced_data(season_data["Advanced"])

    return season_data


def save_dataframes_to_excel(dataframes: dict[str, pd.DataFrame], season_year: str) -> None:
    filename = clean_file_path(season_year)
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def process_and_save_all_seasons(season_years: list[str]) -> dict[str, dict[str, pd.DataFrame]]:
    analyzed_seasons_data: dict[str, dict[str, pd.DataFrame]] = {}

    for season_year in season_years:
        cleansed_data = clean_season_data(season_year)
        analyzed_seasons_data[season_year] = cleansed_data
        save_dataframes_to_excel(cleansed_data, season_year)

    return analyzed_seasons_data


def export_to_sql(engine, dataframe: pd.DataFrame, table_name: str) -> None:
    dataframe.to_sql(table_name, con=engine, if_exists="append", index=False)


def read_and_export_season_data(season_years: list[str]) -> None:
    engine = create_engine(SQLALCHEMY_URL)

    for season_year in season_years:
        file_path = clean_file_path(season_year)

        for sheet_name, table_name in TABLE_MAP.items():
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            export_to_sql(engine, df, table_name)

        print(f"Data from {season_year} exported successfully.")


def main() -> None:
    process_and_save_all_seasons(SEASON_YEARS)
    read_and_export_season_data(SEASON_YEARS)


if __name__ == "__main__":
    main()
