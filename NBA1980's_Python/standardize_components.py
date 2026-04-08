import pandas as pd
from pathlib import Path

file_path = Path.home() / "Documents" / "NBA1980s" / "NBA 1980's Data" / "1980's_CleanedData" / "Cleansed_NBA_1988-1989.xlsx"

totals_df = pd.read_excel(file_path, sheet_name="Totals")
advanced_df = pd.read_excel(file_path, sheet_name="Advanced")

# Keep only useful columns
totals_keep = [
    "Player", "Tm", "Season", "G", "MP", "PTS", "TRB", "AST", "STL", "BLK", "TOV",
    "PTS_share", "AST_share", "TRB_share", "STL_share", "BLK_share", "TOV_share", "MP_share"
]

advanced_keep = [
    "Player", "Tm", "Season", "PER", "TS%", "WS/48", "WS", "BPM", "VORP"
]

totals_df = totals_df[[col for col in totals_keep if col in totals_df.columns]]
advanced_df = advanced_df[[col for col in advanced_keep if col in advanced_df.columns]]

df = totals_df.merge(advanced_df, on=["Player", "Tm", "Season"], how="left")

print(df.columns)
print(df.head())
def zscore_by_season(df, col):
    return df.groupby("Season")[col].transform(
        lambda x: ((x - x.mean()) / x.std(ddof=0)) if x.std(ddof=0) != 0 else 0
    )

cols_to_zscore = [
    "PTS", "TRB", "AST", "STL", "BLK", "TOV",
    "TS%", "PER", "WS/48",
    "PTS_share", "TRB_share", "AST_share", "MP_share"
]

for col in cols_to_zscore:
    safe_name = col.replace("%", "_pct").replace("/", "")
    df[f"z_{safe_name}"] = zscore_by_season(df, col)

df["production_score"] = (
    df["z_PTS"]
    + df["z_TRB"]
    + df["z_AST"]
    + 0.5 * df["z_STL"]
    + 0.5 * df["z_BLK"]
    - 0.5 * df["z_TOV"]
)

df["efficiency_score"] = (
    df["z_TS_pct"]
    + df["z_PER"]
    + df["z_WS48"]
)

df["dependence_score"] = (
    df["z_PTS_share"]
    + df["z_TRB_share"]
    + df["z_AST_share"]
    + df["z_MP_share"]
)

df["z_production_score"] = zscore_by_season(df, "production_score")
df["z_efficiency_score"] = zscore_by_season(df, "efficiency_score")
df["z_dependence_score"] = zscore_by_season(df, "dependence_score")

df["custom_impact_v1"] = (
    0.4 * df["z_production_score"]
    + 0.3 * df["z_efficiency_score"]
    + 0.3 * df["z_dependence_score"]
)
df["dependence_rank"] = df.groupby("Season")["dependence_score"].rank(
    ascending=False,
    method="min"
)

df["per_rank"] = df.groupby("Season")["PER"].rank(ascending=False, method="min")
df["bpm_rank"] = df.groupby("Season")["BPM"].rank(ascending=False, method="min")
df["ws_rank"] = df.groupby("Season")["WS"].rank(ascending=False, method="min")

df["advanced_rank_avg"] = (
    df["per_rank"] + df["bpm_rank"] + df["ws_rank"]
) / 3

df["burden_gap"] = df["advanced_rank_avg"] - df["dependence_rank"]

print(
    df[["Player", "Tm", "Season", "custom_impact_v1", "dependence_score", "dependence_rank", "advanced_rank_avg", "burden_gap"]]
    .sort_values("custom_impact_v1", ascending=False)
    .head(20)
)

print(
    df[["Player", "Tm", "Season", "dependence_score", "dependence_rank", "burden_gap"]]
    .sort_values("burden_gap", ascending=False)
    .head(20)
)