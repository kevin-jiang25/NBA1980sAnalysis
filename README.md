# NBA1980sAnalysis

## Project Question
Can team centrality and role burden reveal dimensions of player impact in the 1980s NBA that traditional box-score and advanced metrics do not fully capture?

## Main Framing
This is a measured-impact project, not a true-impact project.

It asks:
Which players appear more central to their teams' measurable production and burden than traditional advanced metrics alone would suggest?

This framing intentionally avoids claiming we can directly measure hidden factors like leadership, screening, defensive communication, gravity, or locker-room impact from this dataset alone.

## Hypothesis
Including team dependence and durability-related proxies should elevate some players relative to standard advanced-stat rankings.

## Core Framework
Impact is modeled as two broad dimensions:

1. Statistical Quality
- PER
- BPM
- WS
- TS%
- WS/48

2. Team Centrality
- Points share
- Assists share
- Rebounds share
- Minutes share
- Usage and durability (planned extensions)

Key idea:
Impact is not only quality, it is also centrality.

## Version 1 Index (Current)
The current implementation in `NBA1980's_Python/standardize_components.py` builds a **Custom Impact Index v1** from 3 components:

1. Production
- `z(PTS) + z(TRB) + z(AST) + 0.5*z(STL) + 0.5*z(BLK) - 0.5*z(TOV)`

2. Efficiency
- `z(TS%) + z(PER) + z(WS/48)`

3. Team Dependence (implemented)
- `z(PTS_share) + z(TRB_share) + z(AST_share) + z(MP_share)`

Index combination (implemented):
- `Custom Impact v1 = 0.4*z(Production) + 0.3*z(Efficiency) + 0.3*z(Dependence)`

Comparison baseline:
- `Advanced Rank Avg = average(rank(PER), rank(BPM), rank(WS))`

Role-burden lens:
- `Dependence Rank = rank(Dependence Score, descending by season)`
- `Burden Gap = Advanced Rank Avg - Dependence Rank`

Interpretation:
- Larger positive burden gap suggests a player appears more relied upon than their advanced-rank average alone would indicate.

## Current Output Files
The analysis writes these CSVs to `NBA1980's_Python/output/`:

- `merged_columns.csv`
- `merged_head.csv`
- `top_custom_impact.csv`
- `top_burden_gap.csv`

## Snapshot From Current Outputs (1989-1990)
Based on `top_custom_impact.csv`, the top Custom Impact v1 players include:
- Michael Jordan
- Hakeem Olajuwon
- David Robinson
- Magic Johnson
- Patrick Ewing

Based on `top_burden_gap.csv`, the highest burden-gap players include:
- J.R. Reid
- Rex Chapman
- Joe Wolf
- Jeff Turner
- Kevin Edwards

This supports the project direction: high centrality/burden signals can surface players differently than quality-only advanced rankings.

## Hidden Impact and Limits
This dataset can capture player impact well in:
- Bucket A: impact clearly visible in box stats
- Bucket B: impact partly visible in advanced stats

It is weaker for:
- Bucket C: impact only weakly visible in these features (screening, off-ball gravity, matchup deterrence, leadership effects)

These should be discussed as likely missing components, not claimed as measured.

## Next Steps
1. Expand Team Dependence with additional share terms from your drafted formula (e.g., STL/BLK/TOV-share effects if desired).
2. Add durability and trust proxies directly into the index (`G`, total minutes, team minute share weighting).
3. Add role-efficiency tests (low usage with high TS%/WS48) for low-volume high-value players.
4. Run this pipeline across all seasons in the 1980s and compare stability of burden-gap findings year over year.
