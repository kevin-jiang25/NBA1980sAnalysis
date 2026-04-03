from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path.home() / "Documents" / "NBA1980s" / "NBA 1980's Data" / "1980's_CleanedData"

SEASONS = [
    "1980-1981", "1981-1982", "1982-1983", "1983-1984", "1984-1985",
    "1985-1986", "1986-1987", "1987-1988", "1988-1989", "1989-1990"
]

TOP_N = 20
MIN_GAMES = 20
MIN_MINUTES_PER_GAME = 15

# -----------------------------
# Helpers
# -----------------------------
def clean_names_simple(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    df = df.loc[:, ~pd.Series(df.columns).str.startswith("Unnamed").values]
    return df


def safe_read_sheet(file_path: Path, sheet_name: str) -> pd.DataFrame | None:
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name)
    except Exception as e:
        print(f"Could not read {sheet_name} from {file_path}: {e}")
        return None


def prepare_one_season(season: str) -> pd.DataFrame | None:
    file_path = DATA_DIR / f"Cleansed_NBA_{season}.xlsx"

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return None

    per_game = safe_read_sheet(file_path, "PerGame")
    totals = safe_read_sheet(file_path, "Totals")   # kept here to match your structure
    advanced = safe_read_sheet(file_path, "Advanced")

    if per_game is None or totals is None or advanced is None:
        return None

    per_game = clean_names_simple(per_game)
    totals = clean_names_simple(totals)
    advanced = clean_names_simple(advanced)

    per_game_keep = [
        "Player", "Pos", "Age", "Tm", "G", "MP", "PTS", "TRB", "AST",
        "STL", "BLK", "TOV", "FG%", "3P%", "2P%", "eFG%", "FT%", "Season"
    ]

    advanced_keep = [
        "Player", "Pos", "Age", "Tm", "G", "MP", "PER", "TS%", "USG%",
        "OWS", "DWS", "WS", "WS/48", "OBPM", "DBPM", "BPM", "VORP", "Season"
    ]

    per_game = per_game[[col for col in per_game_keep if col in per_game.columns]]
    advanced = advanced[[col for col in advanced_keep if col in advanced.columns]]

    # Merge like your R script:
    # left_join(advanced %>% select(-Pos, -Age, -G, -MP), by = c("Player", "Tm", "Season"))
    adv_drop_cols = [col for col in ["Pos", "Age", "G", "MP"] if col in advanced.columns]
    advanced_for_merge = advanced.drop(columns=adv_drop_cols)

    merge_keys = [col for col in ["Player", "Tm", "Season"] if col in per_game.columns and col in advanced_for_merge.columns]
    if len(merge_keys) < 2:
        print(f"Not enough merge keys found for {season}. Available keys: {merge_keys}")
        return None

    merged = per_game.merge(advanced_for_merge, how="left", on=merge_keys)

    numeric_cols = [
        "Age", "G", "MP", "PTS", "TRB", "AST", "STL", "BLK", "TOV",
        "FG%", "3P%", "2P%", "eFG%", "FT%",
        "PER", "TS%", "USG%", "OWS", "DWS", "WS", "WS/48",
        "OBPM", "DBPM", "BPM", "VORP"
    ]

    for col in numeric_cols:
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")

    # NOTE:
    # In your R script, MP is filtered as MP >= min_minutes_per_game.
    # If MP is total minutes instead of minutes-per-game, this is very lenient.
    # I'm keeping it exactly as written for now.
    if "G" in merged.columns and "MP" in merged.columns:
        merged = merged[(merged["G"] >= MIN_GAMES) & (merged["MP"] >= MIN_MINUTES_PER_GAME)]

    return merged


def get_top_metric(df: pd.DataFrame, metric: str, n: int = 20) -> pd.DataFrame | None:
    if metric not in df.columns:
        return None

    keep_cols = [col for col in ["Player", "Tm", metric] if col in df.columns]
    top_df = (
        df[keep_cols]
        .dropna(subset=[metric])
        .sort_values(by=metric, ascending=False)
        .head(n)
        .reset_index(drop=True)
    )
    return top_df


def plot_top_metric(df: pd.DataFrame, metric: str, season_label: str, top_n: int = 15, save_dir: Path | None = None):
    if metric not in df.columns:
        return

    keep_cols = [col for col in ["Player", "Tm", metric] if col in df.columns]
    top_df = (
        df[keep_cols]
        .dropna(subset=[metric])
        .sort_values(by=metric, ascending=False)
        .head(top_n)
        .copy()
    )

    if top_df.empty:
        return

    top_df["Label"] = top_df["Player"] + " (" + top_df["Tm"] + ")"
    top_df = top_df.iloc[::-1]  # reverse for horizontal bar chart

    plt.figure(figsize=(10, 7))
    plt.barh(top_df["Label"], top_df[metric])
    plt.title(f"Top {top_n} {metric} for {season_label}")
    plt.xlabel(metric)
    plt.ylabel("")
    plt.tight_layout()

    if save_dir is not None:
        save_dir.mkdir(parents=True, exist_ok=True)
        safe_metric = metric.replace("/", "_").replace("%", "pct")
        plt.savefig(save_dir / f"{season_label}_{safe_metric}.png", dpi=300, bbox_inches="tight")

    plt.show()


# -----------------------------
# Analyze each season separately
# -----------------------------
season_results = {}

for season in SEASONS:
    print("\n=============================")
    print(f"Analyzing season: {season}")
    print("=============================")

    season_df = prepare_one_season(season)

    if season_df is None or season_df.empty:
        print(f"No usable data for {season}")
        continue

    season_results[season] = season_df

    print(f"\nRows loaded: {len(season_df)}")
    print("\nColumns:")
    print(list(season_df.columns))

    # Top players by metric for this season
    top_ws = get_top_metric(season_df, "WS", TOP_N)
    top_bpm = get_top_metric(season_df, "BPM", TOP_N)
    top_vorp = get_top_metric(season_df, "VORP", TOP_N)
    top_per = get_top_metric(season_df, "PER", TOP_N)
    top_ows = get_top_metric(season_df, "OWS", TOP_N)
    top_dws = get_top_metric(season_df, "DWS", TOP_N)

    print("\n=== Top Win Shares ===")
    print(top_ws)

    print("\n=== Top BPM ===")
    print(top_bpm)

    print("\n=== Top VORP ===")
    print(top_vorp)

    print("\n=== Top PER ===")
    print(top_per)

    print("\n=== Top Offensive Win Shares ===")
    print(top_ows)

    print("\n=== Top Defensive Win Shares ===")
    print(top_dws)

    # Correlation matrix for this season
    corr_cols = [
        "PTS", "TRB", "AST", "STL", "BLK", "PER", "TS%", "USG%",
        "OWS", "DWS", "WS", "WS/48", "OBPM", "DBPM", "BPM", "VORP"
    ]
    corr_cols = [col for col in corr_cols if col in season_df.columns]

    if len(corr_cols) > 1:
        print("\n=== Correlation Matrix ===")
        corr_matrix = season_df[corr_cols].corr()
        print(corr_matrix.round(2))

        season_tag = season.replace("-", "_")
        corr_matrix.to_csv(DATA_DIR / f"corr_matrix_{season_tag}.csv", index=True)

    # Save CSVs for this season
    season_tag = season.replace("-", "_")

    season_df.to_csv(DATA_DIR / f"season_data_{season_tag}.csv", index=False)

    if top_ws is not None:
        top_ws.to_csv(DATA_DIR / f"top_ws_{season_tag}.csv", index=False)
    if top_bpm is not None:
        top_bpm.to_csv(DATA_DIR / f"top_bpm_{season_tag}.csv", index=False)
    if top_vorp is not None:
        top_vorp.to_csv(DATA_DIR / f"top_vorp_{season_tag}.csv", index=False)
    if top_per is not None:
        top_per.to_csv(DATA_DIR / f"top_per_{season_tag}.csv", index=False)
    if top_ows is not None:
        top_ows.to_csv(DATA_DIR / f"top_ows_{season_tag}.csv", index=False)
    if top_dws is not None:
        top_dws.to_csv(DATA_DIR / f"top_dws_{season_tag}.csv", index=False)

    # Plots for this season
    plots_dir = DATA_DIR / "plots"
    plot_top_metric(season_df, "WS", season, 15, plots_dir)
    plot_top_metric(season_df, "BPM", season, 15, plots_dir)
    plot_top_metric(season_df, "VORP", season, 15, plots_dir)
    plot_top_metric(season_df, "PER", season, 15, plots_dir)

print("\nFinished seasonal analysis.")