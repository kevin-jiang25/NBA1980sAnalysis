from pathlib import Path

import pandas as pd

FILE_PATH = (
    Path.home()
    / "Code"
    / "NBA1980sAnalysis"
    / "NBA 1980's Data"
    / "1980's_CleanedData"
    / "Cleansed_NBA_1989-1990.xlsx"
)
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

TOTALS_KEEP = [
    "Player",
    "Tm",
    "Season",
    "G",
    "MP",
    "PTS",
    "TRB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PTS_share",
    "AST_share",
    "TRB_share",
    "STL_share",
    "BLK_share",
    "TOV_share",
    "MP_share",
]

ADVANCED_KEEP = [
    "Player",
    "Tm",
    "Season",
    "PER",
    "TS%",
    "WS/48",
    "WS",
    "BPM",
    "VORP",
]

Z_SCORE_COLUMNS = [
    "PTS",
    "TRB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "TS%",
    "PER",
    "WS/48",
    "PTS_share",
    "TRB_share",
    "AST_share",
    "MP_share",
]


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def read_source_data(file_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    totals_df = pd.read_excel(file_path, sheet_name="Totals")
    advanced_df = pd.read_excel(file_path, sheet_name="Advanced")
    return totals_df, advanced_df


def keep_columns(df: pd.DataFrame, keep_list: list[str]) -> pd.DataFrame:
    return df[[col for col in keep_list if col in df.columns]].copy()


def zscore_by_season(df: pd.DataFrame, col: str) -> pd.Series:
    return df.groupby("Season")[col].transform(
        lambda x: ((x - x.mean()) / x.std(ddof=0)) if x.std(ddof=0) != 0 else 0
    )


def add_z_score_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for col in Z_SCORE_COLUMNS:
        safe_name = col.replace("%", "_pct").replace("/", "")
        result[f"z_{safe_name}"] = zscore_by_season(result, col)
    return result


def add_scoring_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["production_score"] = (
        result["z_PTS"]
        + result["z_TRB"]
        + result["z_AST"]
        + 0.5 * result["z_STL"]
        + 0.5 * result["z_BLK"]
        - 0.5 * result["z_TOV"]
    )

    result["efficiency_score"] = (
        result["z_TS_pct"] + result["z_PER"] + result["z_WS48"]
    )

    result["dependence_score"] = (
        result["z_PTS_share"]
        + result["z_TRB_share"]
        + result["z_AST_share"]
        + result["z_MP_share"]
    )

    result["z_production_score"] = zscore_by_season(result, "production_score")
    result["z_efficiency_score"] = zscore_by_season(result, "efficiency_score")
    result["z_dependence_score"] = zscore_by_season(result, "dependence_score")

    result["custom_impact_v1"] = (
        0.4 * result["z_production_score"]
        + 0.3 * result["z_efficiency_score"]
        + 0.3 * result["z_dependence_score"]
    )

    result["dependence_rank"] = result.groupby("Season")["dependence_score"].rank(
        ascending=False, method="min"
    )
    result["per_rank"] = result.groupby("Season")["PER"].rank(
        ascending=False, method="min"
    )
    result["bpm_rank"] = result.groupby("Season")["BPM"].rank(
        ascending=False, method="min"
    )
    result["ws_rank"] = result.groupby("Season")["WS"].rank(
        ascending=False, method="min"
    )

    result["advanced_rank_avg"] = (
        result["per_rank"] + result["bpm_rank"] + result["ws_rank"]
    ) / 3
    result["burden_gap"] = result["advanced_rank_avg"] - result["dependence_rank"]

    result["custom_impact_rank"] = result.groupby("Season")["custom_impact_v1"].rank(
        ascending=False, method="min"
    )

    return result


def write_outputs(df: pd.DataFrame, output_dir: Path) -> None:
    pd.DataFrame({"column_name": df.columns}).to_csv(
        output_dir / "merged_columns.csv", index=False
    )
    df.head().to_csv(output_dir / "merged_head.csv", index=False)

    top_custom_impact_df = (
        df[
            [
                "Player",
                "Tm",
                "Season",
                "custom_impact_v1",
                "dependence_score",
                "dependence_rank",
                "advanced_rank_avg",
                "burden_gap",
            ]
        ]
        .sort_values("custom_impact_v1", ascending=False)
        .head(20)
    )
    top_custom_impact_df.to_csv(output_dir / "top_custom_impact.csv", index=False)

    top_burden_gap_df = (
        df[
            [
                "Player",
                "Tm",
                "Season",
                "dependence_score",
                "dependence_rank",
                "burden_gap",
            ]
        ]
        .sort_values("burden_gap", ascending=False)
        .head(20)
    )
    top_burden_gap_df.to_csv(output_dir / "top_burden_gap.csv", index=False)


def main() -> None:
    output_dir = ensure_output_dir()
    totals_df, advanced_df = read_source_data(FILE_PATH)

    totals_df = keep_columns(totals_df, TOTALS_KEEP)
    advanced_df = keep_columns(advanced_df, ADVANCED_KEEP)

    merged_df = totals_df.merge(advanced_df, on=["Player", "Tm", "Season"], how="left")
    merged_df = add_z_score_columns(merged_df)
    merged_df = add_scoring_columns(merged_df)

    write_outputs(merged_df, output_dir)


if __name__ == "__main__":
    main()
