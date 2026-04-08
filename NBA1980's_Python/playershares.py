from pathlib import Path

import pandas as pd

DATA_DIRECTORY = Path("NBA 1980's Data/1980's_CleanedData")
DEFAULT_STATS = ["PTS", "AST", "TRB", "STL", "BLK", "TOV", "MP"]
SHARE_COLUMNS = [
    "PTS_share",
    "AST_share",
    "TRB_share",
    "STL_share",
    "BLK_share",
    "TOV_share",
    "MP_share",
]


def iter_cleansed_excel_files(data_directory: Path):
    for file_path in sorted(data_directory.iterdir()):
        filename = file_path.name
        if (
            filename.startswith("~$")
            or not filename.startswith("Cleansed_NBA_")
            or file_path.suffix != ".xlsx"
            or "with_centrality" in filename
        ):
            continue
        yield file_path


def add_team_centrality(
    df: pd.DataFrame,
    team_col: str = "Tm",
    stats: list[str] | None = None,
    keep_team_totals: bool = False,
) -> pd.DataFrame:
    result = df.copy()
    stats = stats or DEFAULT_STATS

    # "TOT" rows combine multi-team seasons; we exclude them for team-share math.
    result = result[result[team_col] != "TOT"]

    for stat in stats:
        team_total_col = f"{stat}_team"
        share_col = f"{stat}_share"
        result[team_total_col] = result.groupby(team_col)[stat].transform("sum")
        result[share_col] = (result[stat] / result[team_total_col]).round(3)

    if not keep_team_totals:
        result = result.drop(columns=[f"{stat}_team" for stat in stats])

    return result


def update_totals_sheet(file_path: Path) -> None:
    sheets = pd.read_excel(file_path, sheet_name=None)
    sheets["Totals"] = add_team_centrality(sheets["Totals"])

    for sheet_name, sheet_df in sheets.items():
        if "Tm" in sheet_df.columns:
            sheets[sheet_name] = sheet_df.sort_values(by=["Tm", "Player"])

    with pd.ExcelWriter(file_path, engine="openpyxl", mode="w") as writer:
        for sheet_name, sheet_df in sheets.items():
            sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)


def validate_centrality(df: pd.DataFrame, filename: str) -> bool:
    print(f"\nValidating {filename}...")
    issues_found = False

    if "TOT" in df["Tm"].values:
        print("Found 'TOT' rows")
        issues_found = True

    for col in SHARE_COLUMNS:
        if col not in df.columns:
            print(f"Missing column: {col}")
            issues_found = True
            continue

        sums = df.groupby("Tm")[col].sum()
        bad_sums = sums[(sums < 0.99) | (sums > 1.01)]
        if not bad_sums.empty:
            print(f"{col} does not sum to ~1 for teams:")
            print(bad_sums.head())
            issues_found = True

    for col in SHARE_COLUMNS:
        if col in df.columns and not df[(df[col] < 0) | (df[col] > 1)].empty:
            print(f"Invalid values in {col}")
            issues_found = True

    if df[SHARE_COLUMNS].isna().sum().sum() > 0:
        print("Found NaNs in share columns")
        issues_found = True

    if not issues_found:
        print("Passed all checks!")

    return not issues_found


def process_all_files(data_directory: Path) -> None:
    for file_path in iter_cleansed_excel_files(data_directory):
        print(f"Processing {file_path.name}")
        update_totals_sheet(file_path)
        print(f"Updated {file_path.name}")


def validate_all_files(data_directory: Path) -> None:
    for file_path in iter_cleansed_excel_files(data_directory):
        sheets = pd.read_excel(file_path, sheet_name=None)
        validate_centrality(sheets["Totals"], file_path.name)


def main() -> None:
    process_all_files(DATA_DIRECTORY)
    validate_all_files(DATA_DIRECTORY)


if __name__ == "__main__":
    main()
