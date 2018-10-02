# Load Packages
library(shiny)
library(tidyverse)

# Set Plot Themes/Palettes
theme_set(theme_light())
scale_colour_discrete <- function(...) scale_colour_brewer(..., palette="Paired")
scale_fill_discrete <- function(...) scale_fill_brewer(... , palette="Paired")

# Load Data
#df.stats <- read.csv("data/points.csv", header = TRUE, stringsAsFactors = FALSE)

# Prepare Data
source("code/prepare_data.R")

# Define UI ----
ui <- fluidPage(
  
  # MAIN HEADINGS
  fluidRow(
    titlePanel(
      img(src = "wcb-xii-logo-small-2.png", align = "right")
    ),
    h1("Will Carter League Overview", align = "center"),
    h3(textOutput("jimsucks"), align = "right")
  ),
  
  # BODY OF APP
  fluidRow(
    sidebarLayout(
      position = "left",
      
      # SIDE PANEL
      sidebarPanel(
        h3("Options"),
        helpText("This app allows you to explore the stats of the Will Carter Fantasy Football League"),
        
        # Optional Formatting
        checkboxInput("js_checkbox", "Recommended Formatting", value = FALSE),
        
        # Input - Plot Category
        selectInput("category", 
                    label = "Choose a Category",
                    choices = list("Power Rankings",
                                   "Point Distribution",
                                   "Championships vs Dvorak"
                    ),
                    selected = "Power Rankings"),
        
        # Input - Season Slider (if Power Rankings selected)
        conditionalPanel(
          condition = "input.category == 'Power Rankings' || input.category == 'Point Distribution'",
          sliderInput("season", 
                      strong("Season"),
                      min = min(df.stats$season), 
                      max = max(df.stats$season),
                      value = c(min(df.stats$season), max(df.stats$season)),
                      step = 1,
                      round = TRUE,
                      sep = ""
          )
        ),
        
        # Input - Manager Selection (If Point Dist Selected)
        conditionalPanel(
          condition = "input.category == 'Point Distribution'",
          checkboxGroupInput("managers", 
                             strong("Team"), 
                             choices = df.managers$manager_name_short,
                             selected = df.managers$manager_name_short[1],
                             width = "100%")
        )
      ),
      
      # MAIN PANEL
      mainPanel(
        #Display Primary Category
        h3(textOutput("selected_category")),
        
        # Display Power Rankings (if selected)
        conditionalPanel(
          condition = "input.category == 'Power Rankings'",
          plotOutput("plot_pr")
        ),
        
        # Display Distribution Plot (if selected)
        conditionalPanel(
          condition = "input.category == 'Point Distribution'",
          plotOutput("plot_dist")
        ),
        
        # Display Distribution Plot (if selected)
        conditionalPanel(
          condition = "input.category == 'Championships vs Dvorak'",
          plotOutput("plot_dvorak")
        )
      )
    )
  )
)



# Define server logic ----
server <- function(input, output) {
  
  # Store Selected Category
  output$selected_category <- renderText({input$category})
  
  # Store Jim Sucks Status
  output$jimsucks <- renderText({ifelse(input$js_checkbox == TRUE, "Jim Sucks", "")})
  
  # Store Power Rankings Plot
  output$plot_pr <- renderPlot({
    
    #Gather Data
    tmp.plot <- df.stats.startreg %>%
      filter(season >= input$season[1] & season <= input$season[2]) %>%
      group_by(team_id, season, week) %>%
      summarise(points_total = sum(points)) %>%
      ungroup() %>%
      left_join(df.teams %>% select(team_id, manager_name_short), by="team_id") %>%
      arrange(season, week) %>%
      mutate(week = paste0(season, "-", week)) %>%
      mutate(week = factor(week, ordered = TRUE))
    
    # Generage Plot
    ggplot(tmp.plot, aes(x = as.integer(week), y = points_total, col = manager_name_short)) +
      geom_smooth(method = 'loess', formula = 'y ~ x',level = 0.5, span = .8, alpha = 0.2) +
      scale_color_discrete(name = "Manager") +
      xlab("Weeks") +
      ylab("Mean Points")
    
  })
  
  # Store Distribution Plot
  output$plot_dist <- renderPlot({
    
    #Gather Data
    tmp.plot <- df.stats.startreg %>%
      left_join(df.managers %>% select(manager_id, manager_name_short), by="manager_id") %>%
      filter(season >= input$season[1] & season <= input$season[2]) %>%
      filter(manager_name_short %in% input$managers) %>%
      group_by(season, week, manager_name_short) %>%
      summarise(point_total = sum(points))
    
    # Generage Plot
    ggplot(tmp.plot, 
           aes(x = point_total, 
               fill = manager_name_short)) +
      geom_density(alpha = 0.3) +
      scale_fill_discrete(name = "Manager") +
      xlab("Points") +
      ylab("Density")
    
  })
  
  # Store Distribution Plot
  output$plot_dvorak <- renderPlot({
    
    tmp.plot <- 
      data.frame("manager" = c("Aaron", "Jim", "Tim", "Cam", "Sean", "Dan", "Will", "Truax", "Joe", "Tom", "Conor", "Zach"), 
                 "outcome" = c(2,-1,0,0,0,0,0,0,0,0,0,0), 
                 "type" = c("W", "L", "L", "L", "L", "L", "L", "L", "L", "L", "L", "L"))
    
    ggplot(tmp.plot, aes(x = reorder(manager, abs(outcome)), y = outcome)) +
      geom_bar(stat = "identity", aes(fill = type), col = "black", alpha = 0.8) +
      geom_text(aes(x = "Jim", y = -0.5, label = "Jim is a failure."), col = "white") +
      geom_text(aes(x = "Aaron", y = 1, label = "Aaron did his job.  Twice..."), col = "white") +
      geom_text(aes(x = "Cam", y = 0.5, label = "Wins"), col = "black") +
      geom_text(aes(x = "Cam", y = -0.5, label = "Losses"), col = "black") +
      geom_vline(xintercept = 0) +
      scale_fill_manual(values=c("firebrick3", "forestgreen")) +
      xlab("Manager") +
      ylab("Outcome") +
      ylim(c(-2,2)) +
      theme(legend.position = "none") +
      coord_flip()
    
  })

  
  
}

# Run the app ----
shinyApp(ui = ui, server = server)