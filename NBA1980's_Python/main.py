from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# =========================================================
# PATHS
# =========================================================
DATA_DIR = Path.home() / "Documents" / "NBA1980s" / "NBA 1980's Data" / "1980's_CleanedData"
OUTPUT_DIR = Path.home() / "Documents" / "NBA1980s" / "NBA1980's_BasicAnalysisPython"

SEASONS = [
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

TOP_N_TABLE = 20
TOP_N_PLOT = 15
TOP_N_DECADE = 20
MIN_GAMES = 20
MIN_MINUTES_PER_GAME = 15

PLOT_FOLDERS = {
    "VORP": OUTPUT_DIR / "Top15VORP",
    "BPM": OUTPUT_DIR / "Top15BPM",
    "PER": OUTPUT_DIR / "Top15PER",
    "DWS": OUTPUT_DIR / "Top15DWS",
    "OWS": OUTPUT_DIR / "Top15OWS",
    "WS": OUTPUT_DIR / "Top15WS",
}
CORR_DIR = OUTPUT_DIR / "CorrelationMatrix"

ADVANCED_STATS = ["VORP", "BPM", "PER", "DWS", "OWS", "WS"]
TOTALS_STATS = [
    "PTS",
    "TRB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "MP",
    "FG",
    "FGA",
    "3P",
    "3PA",
    "FT",
    "FTA",
    "ORB",
    "DRB",
]

PER_GAME_KEEP = [
    "Player",
    "Pos",
    "Age",
    "Tm",
    "G",
    "MP",
    "PTS",
    "TRB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "FG%",
    "3P%",
    "2P%",
    "eFG%",
    "FT%",
    "Season",
]
ADVANCED_KEEP = [
    "Player",
    "Pos",
    "Age",
    "Tm",
    "G",
    "MP",
    "PER",
    "TS%",
    "USG%",
    "OWS",
    "DWS",
    "WS",
    "WS/48",
    "OBPM",
    "DBPM",
    "BPM",
    "VORP",
    "Season",
]

NUMERIC_MERGED_COLUMNS = [
    "Age",
    "G",
    "MP",
    "PTS",
    "TRB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "FG%",
    "3P%",
    "2P%",
    "eFG%",
    "FT%",
    "PER",
    "TS%",
    "USG%",
    "OWS",
    "DWS",
    "WS",
    "WS/48",
    "OBPM",
    "DBPM",
    "BPM",
    "VORP",
]
TOTALS_NUMERIC_COLUMNS = [
    "Age",
    "G",
    "MP",
    "PTS",
    "TRB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "FG",
    "FGA",
    "3P",
    "3PA",
    "FT",
    "FTA",
    "ORB",
    "DRB",
]


# =========================================================
# SETUP
# =========================================================
def setup_output_folders() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CORR_DIR.mkdir(parents=True, exist_ok=True)
    for folder in PLOT_FOLDERS.values():
        folder.mkdir(parents=True, exist_ok=True)


# =========================================================
# HELPERS
# =========================================================
def clean_names_simple(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result.columns = [str(col).strip() for col in result.columns]
    result = result.loc[:, ~pd.Series(result.columns).str.startswith("Unnamed").values]
    return result


def safe_read_sheet(file_path: Path, sheet_name: str) -> pd.DataFrame | None:
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name)
    except Exception as exc:
        print(f"Could not read {sheet_name} from {file_path}: {exc}")
        return None


def to_numeric_if_present(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    result = df.copy()
    for col in cols:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")
    return result


def get_merge_keys(left_df: pd.DataFrame, right_df: pd.DataFrame) -> list[str]:
    possible = ["Player", "Tm", "Season"]
    return [col for col in possible if col in left_df.columns and col in right_df.columns]


def filter_by_games_and_minutes(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    if "G" in result.columns and "MP" in result.columns:
        result = result[(result["G"] >= MIN_GAMES) & (result["MP"] >= MIN_MINUTES_PER_GAME)]
    return result


def season_file_path(season: str) -> Path:
    return DATA_DIR / f"Cleansed_NBA_{season}.xlsx"


def prepare_one_season(season: str) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    file_path = season_file_path(season)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return None, None

    per_game = safe_read_sheet(file_path, "PerGame")
    totals = safe_read_sheet(file_path, "Totals")
    advanced = safe_read_sheet(file_path, "Advanced")
    if per_game is None or totals is None or advanced is None:
        return None, None

    per_game = clean_names_simple(per_game)
    totals = clean_names_simple(totals)
    advanced = clean_names_simple(advanced)

    per_game = per_game[[col for col in PER_GAME_KEEP if col in per_game.columns]]
    advanced = advanced[[col for col in ADVANCED_KEEP if col in advanced.columns]]

    adv_drop_cols = [col for col in ["Pos", "Age", "G", "MP"] if col in advanced.columns]
    advanced_for_merge = advanced.drop(columns=adv_drop_cols)

    merge_keys = get_merge_keys(per_game, advanced_for_merge)
    if len(merge_keys) < 2:
        print(f"Not enough merge keys found for {season}. Available keys: {merge_keys}")
        return None, None

    merged = per_game.merge(advanced_for_merge, how="left", on=merge_keys)
    merged = to_numeric_if_present(merged, NUMERIC_MERGED_COLUMNS)
    merged = filter_by_games_and_minutes(merged)

    totals = to_numeric_if_present(totals, TOTALS_NUMERIC_COLUMNS)
    totals = filter_by_games_and_minutes(totals)

    return merged, totals


def get_top_metric(df: pd.DataFrame, metric: str, n: int = TOP_N_TABLE) -> pd.DataFrame | None:
    if metric not in df.columns:
        return None

    keep_cols = [col for col in ["Player", "Tm", metric] if col in df.columns]
    return (
        df[keep_cols]
        .dropna(subset=[metric])
        .sort_values(by=metric, ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def plot_top_metric(df: pd.DataFrame, metric: str, season_label: str, top_n: int = TOP_N_PLOT) -> None:
    if metric not in df.columns:
        return

    top_df = (
        df[[col for col in ["Player", "Tm", metric] if col in df.columns]]
        .dropna(subset=[metric])
        .sort_values(by=metric, ascending=False)
        .head(top_n)
        .copy()
    )
    if top_df.empty:
        return

    top_df["Label"] = top_df["Player"] + " (" + top_df["Tm"] + ")"
    top_df = top_df.iloc[::-1]

    plt.figure(figsize=(10, 7))
    plt.barh(top_df["Label"], top_df[metric])
    plt.title(f"Top {top_n} {metric} for {season_label}")
    plt.xlabel(metric)
    plt.ylabel("")
    plt.tight_layout()

    out_path = PLOT_FOLDERS[metric] / f"{season_label}_{metric}_top{top_n}.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


def save_correlation_outputs(df: pd.DataFrame, season_label: str) -> None:
    corr_cols = [
        "PTS",
        "TRB",
        "AST",
        "STL",
        "BLK",
        "PER",
        "TS%",
        "USG%",
        "OWS",
        "DWS",
        "WS",
        "WS/48",
        "OBPM",
        "DBPM",
        "BPM",
        "VORP",
    ]
    corr_cols = [col for col in corr_cols if col in df.columns]
    if len(corr_cols) <= 1:
        return

    corr_matrix = df[corr_cols].corr()

    csv_path = CORR_DIR / f"corr_matrix_{season_label.replace('-', '_')}.csv"
    corr_matrix.to_csv(csv_path, index=True)

    plt.figure(figsize=(12, 10))
    image = plt.imshow(corr_matrix, aspect="auto")
    plt.colorbar(image)
    plt.xticks(range(len(corr_cols)), corr_cols, rotation=90)
    plt.yticks(range(len(corr_cols)), corr_cols)
    plt.title(f"Correlation Matrix - {season_label}")
    plt.tight_layout()

    img_path = CORR_DIR / f"corr_matrix_{season_label.replace('-', '_')}.png"
    plt.savefig(img_path, dpi=300, bbox_inches="tight")
    plt.close()


def save_filtered_dataset(df: pd.DataFrame, season_label: str) -> None:
    output_path = OUTPUT_DIR / f"season_data_{season_label.replace('-', '_')}.csv"
    df.to_csv(output_path, index=False)


def save_advanced_top20_tables(df: pd.DataFrame, season_label: str) -> None:
    for metric in ADVANCED_STATS:
        top_df = get_top_metric(df, metric, TOP_N_TABLE)
        if top_df is not None and not top_df.empty:
            output_path = OUTPUT_DIR / f"top20_{metric}_{season_label.replace('-', '_')}.csv"
            top_df.to_csv(output_path, index=False)


def save_totals_top20_tables(totals_df: pd.DataFrame, season_label: str) -> None:
    if totals_df is None or totals_df.empty:
        return

    for stat in TOTALS_STATS:
        if stat not in totals_df.columns:
            continue

        keep_cols = [col for col in ["Player", "Tm", stat] if col in totals_df.columns]
        top_df = (
            totals_df[keep_cols]
            .dropna(subset=[stat])
            .sort_values(by=stat, ascending=False)
            .head(TOP_N_TABLE)
            .reset_index(drop=True)
        )

        if not top_df.empty:
            output_path = OUTPUT_DIR / f"top20_totals_{stat}_{season_label.replace('-', '_')}.csv"
            top_df.to_csv(output_path, index=False)


def save_decade_summary_graph(metric: str, season_results: dict[str, pd.DataFrame]) -> None:
    rows: list[dict[str, float | str]] = []

    for season, df in season_results.items():
        if metric not in df.columns:
            continue

        top_vals = (
            df[[metric]]
            .dropna()
            .sort_values(by=metric, ascending=False)
            .head(TOP_N_PLOT)[metric]
            .tolist()
        )
        if not top_vals:
            continue

        rows.append(
            {
                "Season": season,
                "Top15Mean": float(np.mean(top_vals)),
                "Top15Max": float(np.max(top_vals)),
                "Top15Min": float(np.min(top_vals)),
                "Top15Median": float(np.median(top_vals)),
            }
        )

    if not rows:
        return

    decade_df = pd.DataFrame(rows).sort_values("Season").reset_index(drop=True)
    decade_csv_path = PLOT_FOLDERS[metric] / f"decade_summary_{metric}.csv"
    decade_df.to_csv(decade_csv_path, index=False)

    x_vals = np.arange(len(decade_df))
    seasons = decade_df["Season"].tolist()

    plt.figure(figsize=(12, 7))
    plt.plot(x_vals, decade_df["Top15Mean"], marker="o", label="Top 15 Mean")
    plt.plot(x_vals, decade_df["Top15Median"], marker="s", label="Top 15 Median")
    plt.plot(x_vals, decade_df["Top15Max"], linestyle="--", label="Top 15 Max")
    plt.plot(x_vals, decade_df["Top15Min"], linestyle="--", label="Top 15 Min")
    plt.fill_between(x_vals, decade_df["Top15Min"], decade_df["Top15Max"], alpha=0.2)

    plt.xticks(x_vals, seasons, rotation=45, ha="right")
    plt.title(f"Decade Elite Trend for {metric} (Top 15 Each Season)")
    plt.xlabel("Season")
    plt.ylabel(metric)
    plt.legend()
    plt.tight_layout()

    output_path = PLOT_FOLDERS[metric] / f"decade_elite_trend_{metric}.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def save_true_decade_leaderboard(metric: str, season_results: dict[str, pd.DataFrame]) -> None:
    frames = []
    for season, df in season_results.items():
        if metric not in df.columns:
            continue

        temp = df.copy()
        temp["SeasonLabel"] = season

        keep_cols = [col for col in ["Player", "Tm", metric, "SeasonLabel"] if col in temp.columns]
        temp = temp[keep_cols].dropna(subset=[metric])
        frames.append(temp)

    if not frames:
        return

    decade_all = pd.concat(frames, ignore_index=True)
    top_decade = (
        decade_all.sort_values(by=metric, ascending=False)
        .head(TOP_N_DECADE)
        .reset_index(drop=True)
    )

    csv_path = PLOT_FOLDERS[metric] / f"decade_top{TOP_N_DECADE}_{metric}_player_seasons.csv"
    top_decade.to_csv(csv_path, index=False)

    top_decade["Label"] = (
        top_decade["Player"]
        + " ("
        + top_decade["Tm"]
        + ", "
        + top_decade["SeasonLabel"]
        + ")"
    )

    plot_df = top_decade.iloc[::-1]

    plt.figure(figsize=(12, 9))
    plt.barh(plot_df["Label"], plot_df[metric])
    plt.title(f"Top {TOP_N_DECADE} {metric} Player-Seasons of the 1980s")
    plt.xlabel(metric)
    plt.ylabel("")
    plt.tight_layout()

    img_path = PLOT_FOLDERS[metric] / f"decade_top{TOP_N_DECADE}_{metric}_player_seasons.png"
    plt.savefig(img_path, dpi=300, bbox_inches="tight")
    plt.close()


def run_season_analysis() -> dict[str, pd.DataFrame]:
    season_results: dict[str, pd.DataFrame] = {}

    for season in SEASONS:
        print("\n=============================")
        print(f"Analyzing season: {season}")
        print("=============================")

        season_df, totals_df = prepare_one_season(season)
        if season_df is None or season_df.empty:
            print(f"No usable merged data for {season}")
            continue

        season_results[season] = season_df

        print(f"\nRows loaded after filters: {len(season_df)}")
        print("\nColumns:")
        print(list(season_df.columns))

        save_filtered_dataset(season_df, season)
        save_advanced_top20_tables(season_df, season)
        save_totals_top20_tables(totals_df, season)

        for metric in ADVANCED_STATS:
            plot_top_metric(season_df, metric, season, TOP_N_PLOT)

        save_correlation_outputs(season_df, season)

    print("\nFinished seasonal analysis.")
    return season_results


def run_decade_summaries(season_results: dict[str, pd.DataFrame]) -> None:
    for metric in ADVANCED_STATS:
        save_decade_summary_graph(metric, season_results)
        save_true_decade_leaderboard(metric, season_results)

    print("\nFinished decade summary graphs and true decade leaderboards.")


def main() -> None:
    setup_output_folders()
    season_results = run_season_analysis()
    run_decade_summaries(season_results)


if __name__ == "__main__":
    main()
