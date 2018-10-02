# Load Packages----
library(shiny)
library(tidyverse)

# ----Set Plot Themes/Palettes----
theme_set(theme_light())
scale_colour_discrete <- function(...) scale_colour_brewer(..., palette="Paired")
scale_fill_discrete <- function(...) scale_fill_brewer(... , palette="Paired")

# ----Load Data----
df.stats <- read.csv("data/points.csv", header = TRUE, stringsAsFactors = FALSE)
df.sched <- read.csv("data/schedules.csv", header = TRUE, stringsAsFactors = FALSE)
df.managers.short <- read.csv("data/managers_short.csv", header = TRUE, stringsAsFactors = FALSE)
df.pos.lim <- read.csv("data/position_limits.csv", header = TRUE, stringsAsFactors = FALSE)
# ----Data Prep----

# Add Positional Rank Column
df.stats <- df.stats %>%
  filter(set_pos != "IR") %>%
  left_join(df.managers.short %>% select(manager_name, manager_name_short), 
            by="manager_name") %>%
  left_join(df.pos.lim, by = "player_pos") %>%
  group_by(season, week, team_id, player_pos) %>%
  arrange(desc(points)) %>%
  mutate(rank_tot = row_number()) %>%
  ungroup() %>%
  mutate(posrank_tot = paste0(as.character(player_pos), rank_tot),
         lineup_type = ifelse(! set_pos %in% c("BN", "TAXI"),
                              "Starters",
                              ifelse(set_pos == "BN",
                                     "Bench",
                                     ifelse(set_pos == "TAXI",
                                            "Taxi Squad",
                                            "Unknown"))),
         match_type = ifelse(week <= 13,
                             "Regular Season",
                             "Playoffs")) %>%
  group_by(season, week, team_id, player_pos, lineup_type) %>%
  arrange(desc(points)) %>%
  mutate(rank_start = row_number(),
         posrank_start = ifelse(lineup_type == "Starters",
                                ifelse(pos_lim > 1,
                                       paste0(as.character(player_pos), rank_start),
                                       player_pos),
                                NA)) %>%
  ungroup()

# Create Dataset - Starters, Regular Season
df.stats.startreg <- df.stats %>%
  filter(as.integer(week) <= 13) %>%
  filter(! set_pos %in% c("BN", "TAXI"))

# ----Build Reference Tables----

# Build Current Manager Table
df.managers <- df.stats %>%
  select(manager_id, manager_name) %>%
  distinct() %>%
  arrange(manager_name) %>%
  left_join(df.managers.short, by = "manager_name")

# Build Team Reference Table
df.teams <- df.stats %>%
  group_by(team_id) %>%
  arrange(season, week) %>%
  summarise(manager_id_cur = last(manager_id),
            manager_name_cur = last(manager_name),
            team_name_cur = last(team_name)) %>%
  left_join(df.managers %>% select(manager_id, manager_name_short),
            by = c("manager_id_cur" = "manager_id"))


# ---- UI Functions ----
opt.managers <- df.managers$manager_name_short  # list of managers
opt.posranks <- c("QB1", "QB2", "QB3", "RB1", "RB2", "RB3", "RB4", "WR1", "WR2", "WR3", "WR4", "WR5", "TE1", "TE2", "D/ST1", "D/ST2")

















