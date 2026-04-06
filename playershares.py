import pandas as pd
import os

def add_team_centrality(df, team_col="Tm", stats=None, keep_team_totals=False):
    df_out = df.copy()

    if stats is None:
        stats = ["PTS", "AST", "ORB", "DRB", "STL", "BLK", "MP"]

    """
    If a player's team is "TOT" the column is ignored. "TOT" is when a player is on multiple teams. Their combined
    stats are listed. Not needed for our work.
    """
    df_out = df_out[df_out[team_col] != "TOT"]

    for stat in stats:
        team_total_col = f"{stat}_team"
        share_col = f"{stat}_share"

        df_out[team_total_col] = df_out.groupby(team_col)[stat].transform("sum")
        df_out[share_col] = df_out[stat] / df_out[team_total_col]

    """
    Removes the Team Total PTS/AST/ORB/DRB/STL/BLK/MP from the df. Can set the flag to True
    in function declaration if needed. 
    
    (Logic behind MP might be a little sketch)
    """
    if not keep_team_totals:
        df_out.drop(columns=[f"{stat}_team" for stat in stats], inplace=True)

    return df_out

data_directory = "NBA 1980's Data/1980's_CleanedData"

for file in os.listdir(data_directory):
    if file.startswith("~$"):
        continue
    if not file.startswith("Cleansed_NBA_") or not file.endswith(".xlsx"):
        continue

    file_path = os.path.join(data_directory, file)
    print(f"Processing {file}")

    df = pd.read_excel(file_path, sheet_name="Totals")

    df_out = add_team_centrality(df)

    output_file = os.path.join(data_directory, f"{file.split(".xlsx")[0]}_with_centrality.xlsx")
    df_out.to_excel(output_file, index=False)
