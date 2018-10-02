# Load Data
df.stats <- read.csv("data/points.csv", header = TRUE, stringsAsFactors = FALSE)
df.sched <- read.csv("data/schedules.csv", header = TRUE, stringsAsFactors = FALSE)

# Build Manager Reference Table 
df.managers.short <- data.frame("manager_name" = c("AMackel", 
                                                   "CameronRouzer", 
                                                   "conorclarke", 
                                                   "dayello", 
                                                   "jimayello", 
                                                   "JoeDeGregorio", 
                                                   "M_Stojanovic", 
                                                   "SeanMcNally", 
                                                   "THaze", 
                                                   "TimMartens", 
                                                   "Truax", 
                                                   "WillPo", 
                                                   "zachzachzach"), 
                                
                                "manager_name_short" = c("Aaron", 
                                                         "Cam", 
                                                         "Conor", 
                                                         "Dan", 
                                                         "Jim", 
                                                         "Joe", 
                                                         "Mike", 
                                                         "Sean", 
                                                         "Tom", 
                                                         "Tim", 
                                                         "Truax", 
                                                         "Will", 
                                                         "Zach"),
                                stringsAsFactors = FALSE)

df.managers <- df.stats %>%
  select(manager_id, manager_name) %>%
  distinct() %>%
  arrange(manager_name) %>%
  left_join(df.managers.short, by = "manager_name")

# Build Team Reference Table (with current manager)
df.teams <- df.stats %>%
  group_by(team_id) %>%
  arrange(season, week) %>%
  summarise(manager_id_cur = last(manager_id),
            manager_name_cur = last(manager_name),
            team_name_cur = last(team_name)) %>%
  left_join(df.managers %>% select(manager_id, manager_name_short),
            by = c("manager_id_cur" = "manager_id"))


# Create list of managers for selection
opt.managers <- df.managers$manager_name_short

# Create filtered dataframe with just starters during regular season
df.stats.startreg <- df.stats %>%
  filter(as.integer(week) <= 13) %>%
  filter(! set_pos %in% c("BN", "IR", "TAXI"))














