import pandas as pd
import numpy as np
from openpyxl import load_workbook

"""
Goals:
1. Calculate the team total PTS. As well as AST/REB(ORB/DRB?)/BLK/STL/MINs played

2. 

3. For each player, add the player share calc
"""

file = "NBA 1980's Data/1980's_CleanedData/Cleansed_NBA_1980-1981.xlsx"

df = pd.read_excel(file, sheet_name="Totals")

df_test = df.copy()

df_test['PTS_team'] = df_test.groupby("Tm")["PTS"].transform("sum")

df_test['PTS_team']

team_pts_df = df_test.groupby("Tm", as_index=False)["PTS"].sum(.sort_values(by="PTS", ascending=False))
team_pts_df