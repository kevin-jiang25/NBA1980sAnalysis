import pandas as pd
import os

def add_team_centrality(df, team_col="Tm", stats=None, keep_team_totals=False):
    df_out = df.copy()

    if stats is None:
        stats = ["PTS", "AST", "TRB", "STL", "BLK", "TOV", "MP"]
    """
    If a player's team is "TOT" the column is ignored. "TOT" is when a player is on multiple teams. Their combined
    stats are listed. Not needed for our work.
    """
    df_out = df_out[df_out[team_col] != "TOT"]

    cols_to_remove = ["ORB_share", "DRB_share", "ORB_team", "DRB_team"]

    df_out.drop(columns=[col for col in cols_to_remove if col in df_out.columns], inplace=True)

    for stat in stats:
        team_total_col = f"{stat}_team"
        share_col = f"{stat}_share"

        df_out[team_total_col] = df_out.groupby(team_col)[stat].transform("sum")
        df_out[share_col] = (df_out[stat] / df_out[team_total_col]).round(3)

    """
    Removes the Team Total PTS/AST/ORB/DRB/STL/BLK/MP from the df. Can set the flag to True
    in function declaration if needed. 
    
    (Logic behind MP might be a little sketch)
    """
    if not keep_team_totals:
        df_out.drop(columns=[f"{stat}_team" for stat in stats], inplace=True)

    cols = list(df_out.columns)

    # remove TRB_share from current position
    cols.remove("TRB_share")

    # find where AST_share is
    ast_index = cols.index("AST_share")

    # insert TRB_share right after AST_share
    cols.insert(ast_index + 1, "TRB_share")

    # reassign column order
    df_out = df_out[cols]

    return df_out

data_directory = "NBA 1980's Data/1980's_CleanedData"

"""
Replaces the "Totals" in sheets with the updated info (shares) and writes to the xlsx files
"""

for file in os.listdir(data_directory):
    if (
        file.startswith("~$")
        or not file.startswith("Cleansed_NBA_")
        or not file.endswith(".xlsx")
        or "with_centrality" in file
    ):
        continue

    file_path = os.path.join(data_directory, file)
    print(f"Processing {file}")

    sheets = pd.read_excel(file_path, sheet_name=None)

    sheets["Totals"] = add_team_centrality(sheets["Totals"])

    for name, df in sheets.items():
        if "Tm" in df.columns:
            sheets[name] = df.sort_values(by=["Tm", "Player"])

    with pd.ExcelWriter(file_path, engine="openpyxl", mode="w") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)

    print(f"Updated {file}")

"""
Validates the changes.
1. Checks for 'TOT' rows
2. Checks if the new 'shares' columns add up to 1 for each team
3. Checks for empty cells
"""

def validate_centrality(df, filename):
    print(f"\nValidating {filename}...")

    issues = False

    if "TOT" in df["Tm"].values:
        print("Found 'TOT' rows")
        issues = True

    share_cols = ["PTS_share", "AST_share", "TRB_share", "STL_share", "BLK_share","TOV_share", "MP_share"]

    for col in share_cols:
        if col not in df.columns:
            print(f"Missing column: {col}")
            issues = True
            continue

        sums = df.groupby("Tm")[col].sum()

        bad = sums[(sums < 0.99) | (sums > 1.01)]

        if not bad.empty:
            print(f"{col} does not sum to ~1 for teams:")
            print(bad.head())
            issues = True

    for col in share_cols:
        if col in df.columns:
            if not df[(df[col] < 0) | (df[col] > 1)].empty:
                print(f"Invalid values in {col}")
                issues = True

    if df[share_cols].isna().sum().sum() > 0:
        print("Found NaNs in share columns")
        issues = True

    if not issues:
        print("Passed all checks!")

    return not issues

for filename in os.listdir(data_directory):
    if (
        filename.startswith("~$")
        or not filename.startswith("Cleansed_NBA_")
        or not filename.endswith(".xlsx")
        or "with_centrality" in filename
    ):
        continue

    file_path = os.path.join(data_directory, filename)

    sheets = pd.read_excel(file_path, sheet_name=None)

    df = sheets["Totals"]

    validate_centrality(df, filename)