# NBA1980sAnalysis

## Overview
This project analyzes NBA Player impact in the 1980s by combining traditional advanced metrics with a new concept: **team centrality** - how much a player contributes to their team's total production.

We built a custom metric, **Custom Impact Index v1** and compare it against standard advanced stats to identify players who may be undervalued or carry a larger role relative to traditional rankings.

## Project Question
Can team centrality and role burden reveal dimensions of player impact in the 1980s NBA that traditional box-score and advanced metrics do not fully capture?

## Key Idea
Player impact is not just about efficiency or quality - it is also about how central a player is to their team's production.

We separate:

- **How good a player is**

- **How much their team depends on them**

## Hypothesis
Including team dependence and durability-related proxies should elevate some players relative to standard advanced-stat rankings.

## Methodology
We model player impact using three components:

### 1. Production
Box-score contributions:
- Points, total rebounds, assists, steals, blocks, turnovers

### 2. Efficiency
Advanced Metrics:
- TS%, PER, WS/48

### 3. Team Centrality
Player share of team totals:
- Points share
- Assists share
- Rebounds share
- Minutes share

### Custom Impact Index v1
Our current implementation of the Custom Impact v1 combines these components:

0.4 * Production + 0.3 * Efficiency + 0.3 * Team Centrality

Production
- `z(PTS) + z(TRB) + z(AST) + 0.5*z(STL) + 0.5*z(BLK) - 0.5*z(TOV)`

Efficiency
- `z(TS%) + z(PER) + z(WS/48)`

Team Dependence
- `z(PTS_share) + z(TRB_share) + z(AST_share) + z(MP_share)`


(All components are standardized using z-scores.)

## Burden Gap Analysis

We compare our metric to traditional advanced stats:
- Advanced Rank Avg = average(rank(PER), rank(BPM), rank(WS))
- Dependence Rank = rank based on team centrality

### Burden Gap
- Burden Gap = Advanced Rank Avg - Dependence Rank

Interpretation:
- Larger positive burden gap suggests a player appears more relied upon than their advanced-rank average alone would indicate.
- Lower/negative burden gap suggest a player is efficient, but less central to team production.

## Current Output Files
The analysis writes these CSVs to `NBA1980's_Python/output/`:

- `merged_columns.csv`
- `merged_head.csv`
- `top_custom_impact.csv`
- `top_burden_gap.csv`

## Key Findings From Current Outputs (1989-1990)
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

### Interpretation
Our results show that traditional stars remain dominant under the combined metric. However, role and burden metrics surface additional players who appear to be highly relied on by their teams, but aren't as highly ranked by advanced stats alone.


## Limitations
This project is limited to box-score and derived statistics.

It does not capture:
- Defensive positioning and communication
- Screening and off-ball movement
- Leadership and team dynamics

As a result, the analysis reflects **measurable impact**, not total player impact. While we can somewhat measure impact beyond what is traditionally measured, we can't look at things that can't be quantified.
