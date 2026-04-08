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

# for file in os.listdir(data_directory):
#     if (file.startswith("Cleansed_NBA_")
#         and file.endswith(".xlsx")
#         and not file.startswith("~$")
#         and "with_centrality" not in file):
#         continue

#     file_path = os.path.join(data_directory, file)
#     print(f"Processing {file}")

#     sheets = pd.read_excel(file_path, sheet_name=None)

#     sheets["Totals"] = add_team_centrality(sheets["Totals"])

#     for name, df in sheets.items():
#         if "Tm" in df.columns:
#             sheets[name] = df.sort_values(by=["Tm", "Player"])

#     with pd.ExcelWriter(file_path, engine="openpyxl", mode="w") as writer:
#         for name, df in sheets.items():
#             df.to_excel(writer, sheet_name=name, index=False)

#     print(f"Updated {file}")

def validate_centrality(df, filename):
    print(f"\nValidating {filename}...")

    issues = False

    # 1. Check TOT rows
    if "TOT" in df["Tm"].values:
        print("❌ Found 'TOT' rows")
        issues = True

    # 2. Check share sums
    share_cols = ["PTS_share", "AST_share", "ORB_share", "DRB_share", "STL_share", "BLK_share", "MP_share"]

    for col in share_cols:
        if col not in df.columns:
            print(f"⚠️ Missing column: {col}")
            issues = True
            continue

        sums = df.groupby("Tm")[col].sum()

        bad = sums[(sums < 0.99) | (sums > 1.01)]

        if not bad.empty:
            print(f"❌ {col} does not sum to ~1 for teams:")
            print(bad.head())
            issues = True

    # 3. Check invalid values
    for col in share_cols:
        if col in df.columns:
            if not df[(df[col] < 0) | (df[col] > 1)].empty:
                print(f"❌ Invalid values in {col}")
                issues = True

    # 4. Check NaNs
    if df[share_cols].isna().sum().sum() > 0:
        print("❌ Found NaNs in share columns")
        issues = True

    if not issues:
        print("✅ Passed all checks")

    return not issues

for filename in os.listdir(data_dir):
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