# Load Packages----
library(shiny)
library(tidyverse)
library(kableExtra)

rownames <- base::rownames

# ----Set Plot Themes/Palettes----
theme.global <- theme_light() +
  theme(plot.title = element_text(hjust = 0.5, size = 18, face = "bold"),
        plot.subtitle = element_text(hjust = 0.5))

theme_set(theme.global)

# # Define Palettes
# cbPalette <- c("#A63446","#0072B2", "#009E73",  "#E69F00", "#F0E442", "#56B4E9",
#                "#D55E00", "#CC79A7", "#937666", "#7E1946", "#999999", "#000000")
# scale_colour_discrete <- function(...) scale_colour_manual(values=cbPalette)
# scale_fill_discrete <- function(...) scale_fill_manual(values=cbPalette)

# scale_colour_discrete <- function(...) scale_colour_brewer(..., 
#                                                            palette="Paired")
# scale_fill_discrete <- function(...) scale_fill_brewer(..., 
#                                                        palette="Paired")

# ----Load Data----
df.stats <- read.csv("data/points.csv", 
                     header = TRUE, 
                     stringsAsFactors = FALSE)
df.sched <- read.csv("data/schedules.csv", 
                     header = TRUE, 
                     stringsAsFactors = FALSE)
df.managers.short <- read.csv("data/managers_short.csv", 
                              header = TRUE, 
                              stringsAsFactors = FALSE)
df.pos.lim <- read.csv("data/position_limits.csv", 
                       header = TRUE, 
                       stringsAsFactors = FALSE)

# ----Data Prep----

# Apply Basic Filters
df.stats <- df.stats %>%
  filter(as.integer(week) <= 13,  # Regular Season Only
         set_pos != "IR") 

# Join Data
df.stats <- df.stats %>%
  left_join(df.managers.short %>% 
              select(manager_name, 
                     manager_name_short), 
            by="manager_name") %>%
  left_join(df.pos.lim, by = "player_pos")

# Add Positional Rank
df.stats <- df.stats %>%
  group_by(season, week, team_id, player_pos) %>%
  arrange(desc(points)) %>%
  mutate(pos_rank = row_number()) %>%
  ungroup()

# Add Lineup Type Designation
df.stats <- df.stats %>%
  mutate(lineup_type = ifelse(! set_pos %in% c("BN", "TAXI"),
                              "Starters",
                              ifelse(set_pos == "BN",
                                     "Bench",
                                     ifelse(set_pos == "TAXI",
                                            "Taxi",
                                            "Unknown"))))

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

# ---- Define UI Input Elements----

# Recommended Formatting Checkbox ("Jim Sucks")
inp.chk.jimsucks <- 
  checkboxInput("js_checkbox", "Recommended Formatting", value = FALSE)

# Chart Category Dropdown Selection
inp.select.category <- 
  selectInput("category",
              label = "Choose a Category",
              choices = list("Power Rankings",
                             "H2H Stats",
                             "Point Distribution",
                             "Positional Strength",
                             "Shame"
              ),
              selected = "Power Rankings")

# Season Filter Slider
inp.slider.season <- 
  sliderInput("season", 
              strong("Season"),
              min = min(df.stats$season), 
              max = max(df.stats$season),
              value = c(min(df.stats$season), 
                        max(df.stats$season)),
              step = 1,
              round = TRUE,
              sep = "",
              width = "100%")

# Manager Grouped Checkboxes
inp.chkgrp.managers <- 
  checkboxGroupInput("managers", 
                     strong("Team"), 
                     choices = df.managers$manager_name_short,
                     selected = df.managers$manager_name_short[1],
                     width = "100%")

# Positions Grouped Checkboxes
inp.chkgrp.positions <- 
  checkboxGroupInput("positions", 
                     strong("Positions"), 
                     choices = unique(df.stats$player_pos),
                     selected = unique(df.stats$player_pos)[1],
                     width = "100%")

# Lineup Type Radio Buttons
inp.radbut.lutype <- 
  radioButtons("lutype", 
               strong("Lineup Type"), 
               choices = c("Starters", "Bench", "Taxi"),
               selected = "Starters",
               width = "100%")

# Update Button
inp.action.update <- actionButton("update", "Update View")

# Combined formatted input groups (managers, positions)
inp.grp.1 <- 
  fluidRow(column(4, inp.chkgrp.managers),
           column(8, tagList(inp.chkgrp.positions, inp.radbut.lutype)))
  
