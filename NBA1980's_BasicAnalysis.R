library(readxl)
library(dplyr)
library(purrr)
library(stringr)
library(ggplot2)

# -----------------------------
# Pick your cleaned-data folder
# -----------------------------
data_dir <- dirname(file.choose())

seasons <- c(
  "1980-1981", "1981-1982", "1982-1983", "1983-1984", "1984-1985",
  "1985-1986", "1986-1987", "1987-1988", "1988-1989", "1989-1990"
)

top_n <- 20
min_games <- 20
min_minutes_per_game <- 15

# -----------------------------
# Helpers
# -----------------------------
clean_names_simple <- function(df) {
  names(df) <- str_trim(names(df))
  df <- df[, !str_detect(names(df), "^Unnamed"), drop = FALSE]
  df
}

safe_read_sheet <- function(file_path, sheet_name) {
  tryCatch(
    read_excel(file_path, sheet = sheet_name),
    error = function(e) {
      message("Could not read ", sheet_name, " from ", file_path)
      return(NULL)
    }
  )
}

prepare_one_season <- function(season) {
  file_path <- file.path(data_dir, paste0("Cleansed_NBA_", season, ".xlsx"))
  
  if (!file.exists(file_path)) {
    message("File not found: ", file_path)
    return(NULL)
  }
  
  per_game <- safe_read_sheet(file_path, "PerGame")
  totals <- safe_read_sheet(file_path, "Totals")
  advanced <- safe_read_sheet(file_path, "Advanced")
  
  if (is.null(per_game) || is.null(totals) || is.null(advanced)) {
    return(NULL)
  }
  
  per_game <- clean_names_simple(per_game)
  totals <- clean_names_simple(totals)
  advanced <- clean_names_simple(advanced)
  
  per_game_keep <- c(
    "Player", "Pos", "Age", "Tm", "G", "MP", "PTS", "TRB", "AST",
    "STL", "BLK", "TOV", "FG%", "3P%", "2P%", "eFG%", "FT%", "Season"
  )
  
  advanced_keep <- c(
    "Player", "Pos", "Age", "Tm", "G", "MP", "PER", "TS%", "USG%",
    "OWS", "DWS", "WS", "WS/48", "OBPM", "DBPM", "BPM", "VORP", "Season"
  )
  
  per_game <- per_game %>% select(any_of(per_game_keep))
  advanced <- advanced %>% select(any_of(advanced_keep))
  
  merged <- per_game %>%
    left_join(
      advanced %>% select(-any_of(c("Pos", "Age", "G", "MP"))),
      by = c("Player", "Tm", "Season")
    )
  
  numeric_cols <- c(
    "Age", "G", "MP", "PTS", "TRB", "AST", "STL", "BLK", "TOV",
    "FG%", "3P%", "2P%", "eFG%", "FT%",
    "PER", "TS%", "USG%", "OWS", "DWS", "WS", "WS/48",
    "OBPM", "DBPM", "BPM", "VORP"
  )
  
  for (col in numeric_cols) {
    if (col %in% names(merged)) {
      merged[[col]] <- suppressWarnings(as.numeric(merged[[col]]))
    }
  }
  
  merged <- merged %>%
    filter(G >= min_games, MP >= min_minutes_per_game)
  
  merged
}

get_top_metric <- function(df, metric, n = 20) {
  if (!metric %in% names(df)) return(NULL)
  
  df %>%
    select(Player, Tm, all_of(metric)) %>%
    filter(!is.na(.data[[metric]])) %>%
    arrange(desc(.data[[metric]])) %>%
    slice_head(n = n)
}

plot_top_metric <- function(df, metric, season_label, top_n = 15) {
  if (!metric %in% names(df)) return(NULL)
  
  top_df <- df %>%
    select(Player, Tm, all_of(metric)) %>%
    filter(!is.na(.data[[metric]])) %>%
    arrange(desc(.data[[metric]])) %>%
    slice_head(n = top_n) %>%
    mutate(Label = paste0(Player, " (", Tm, ")")) %>%
    mutate(Label = factor(Label, levels = rev(Label)))
  
  ggplot(top_df, aes(x = Label, y = .data[[metric]])) +
    geom_col() +
    coord_flip() +
    labs(
      title = paste("Top", top_n, metric, "for", season_label),
      x = NULL,
      y = metric
    ) +
    theme_minimal()
}

# -----------------------------
# Analyze each season separately
# -----------------------------
season_results <- list()

for (season in seasons) {
  cat("\n=============================\n")
  cat("Analyzing season:", season, "\n")
  cat("=============================\n")
  
  season_df <- prepare_one_season(season)
  
  if (is.null(season_df) || nrow(season_df) == 0) {
    cat("No usable data for", season, "\n")
    next
  }
  
  season_results[[season]] <- season_df
  
  cat("\nRows loaded:", nrow(season_df), "\n")
  cat("\nColumns:\n")
  print(names(season_df))
  
  # Top players by metric for this season
  top_ws <- get_top_metric(season_df, "WS", top_n)
  top_bpm <- get_top_metric(season_df, "BPM", top_n)
  top_vorp <- get_top_metric(season_df, "VORP", top_n)
  top_per <- get_top_metric(season_df, "PER", top_n)
  top_ows <- get_top_metric(season_df, "OWS", top_n)
  top_dws <- get_top_metric(season_df, "DWS", top_n)
  
  cat("\n=== Top Win Shares ===\n")
  print(top_ws)
  
  cat("\n=== Top BPM ===\n")
  print(top_bpm)
  
  cat("\n=== Top VORP ===\n")
  print(top_vorp)
  
  cat("\n=== Top PER ===\n")
  print(top_per)
  
  cat("\n=== Top Offensive Win Shares ===\n")
  print(top_ows)
  
  cat("\n=== Top Defensive Win Shares ===\n")
  print(top_dws)
  
  # Correlation matrix for this season
  corr_cols <- c(
    "PTS", "TRB", "AST", "STL", "BLK", "PER", "TS%", "USG%",
    "OWS", "DWS", "WS", "WS/48", "OBPM", "DBPM", "BPM", "VORP"
  )
  corr_cols <- intersect(corr_cols, names(season_df))
  
  if (length(corr_cols) > 1) {
    cat("\n=== Correlation Matrix ===\n")
    print(round(cor(season_df[, corr_cols], use = "pairwise.complete.obs"), 2))
  }
  
  # Save CSVs for this season
  season_tag <- gsub("-", "_", season)
  
  write.csv(season_df,
            file.path(data_dir, paste0("season_data_", season_tag, ".csv")),
            row.names = FALSE)
  
  write.csv(top_ws,
            file.path(data_dir, paste0("top_ws_", season_tag, ".csv")),
            row.names = FALSE)
  
  write.csv(top_bpm,
            file.path(data_dir, paste0("top_bpm_", season_tag, ".csv")),
            row.names = FALSE)
  
  write.csv(top_vorp,
            file.path(data_dir, paste0("top_vorp_", season_tag, ".csv")),
            row.names = FALSE)
  
  write.csv(top_per,
            file.path(data_dir, paste0("top_per_", season_tag, ".csv")),
            row.names = FALSE)
  
  write.csv(top_ows,
            file.path(data_dir, paste0("top_ows_", season_tag, ".csv")),
            row.names = FALSE)
  
  write.csv(top_dws,
            file.path(data_dir, paste0("top_dws_", season_tag, ".csv")),
            row.names = FALSE)
  
  # Plots for this season
  print(plot_top_metric(season_df, "WS", season, 15))
  print(plot_top_metric(season_df, "BPM", season, 15))
  print(plot_top_metric(season_df, "VORP", season, 15))
  print(plot_top_metric(season_df, "PER", season, 15))
}

cat("\nFinished seasonal analysis.\n")

