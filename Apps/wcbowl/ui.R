
fluidPage(
  
  # Header Start----
  fluidRow(
    titlePanel(
      img(src = "wcb-xii-logo-small-2.png", align = "right")
    ),
    h1("Will Carter League Overview", align = "center"),
    h3(textOutput("jimsucks"), align = "right")
  ),
  
  # Page ----
  fluidRow(
    sidebarLayout(
      position = "left",
      
      # Side Panel----
      sidebarPanel(
        fluidRow(
          h3("Options"),
          helpText("This app allows you to explore the stats of the Will Carter Fantasy Football League"),
          
          # Optional Formatting----
          checkboxInput("js_checkbox", "Recommended Formatting", value = FALSE),
          
          # Input - Plot Category----
          selectInput("category", 
                      label = "Choose a Category",
                      choices = list("Power Rankings",
                                     "Point Distribution",
                                     "Positional Strength",
                                     "Championships vs Dvorak"
                      ),
                      selected = "Power Rankings"),
          
          # Input - Season Slider----
          conditionalPanel(
            condition = "input.category == 'Power Rankings' || input.category == 'Point Distribution' || input.category == 'Positional Strength'",
            sliderInput("season", 
                        strong("Season"),
                        min = min(df.stats$season), 
                        max = max(df.stats$season),
                        value = c(min(df.stats$season), max(df.stats$season)),
                        step = 1,
                        round = TRUE,
                        sep = "",
                        width = "100%")
          )
        ),
        fluidRow(
          column(
            6,
            # Input - Manager Selection----
            conditionalPanel(
              condition = "input.category == 'Point Distribution' || input.category == 'Positional Strength'",
              checkboxGroupInput("managers", 
                                 strong("Team"), 
                                 choices = df.managers$manager_name_short,
                                 selected = df.managers$manager_name_short[1],
                                 width = "100%")
            )
          ),
          column(
            6,
            # Input - Position Selection----
            conditionalPanel(
              condition = "input.category == 'Positional Strength'",
              checkboxGroupInput("positions", 
                                 strong("Positions"), 
                                 choices = opt.posranks,
                                 selected = opt.posranks[1],
                                 width = "100%")
            )
          )
        )
      ),
      
      # Output Panel----
      mainPanel(
        
        # Category Header----
        h3(textOutput("selected_category")),
        
        # Power Rankings----
        conditionalPanel(
          condition = "input.category == 'Power Rankings'",
          plotOutput("plot_pr")
        ),
        
        # Distribution Plots----
        conditionalPanel(
          condition = "input.category == 'Point Distribution'",
          plotOutput("plot_dist")
        ),
        
        # Positional Strength----
        conditionalPanel(
          condition = "input.category == 'Positional Strength'",
          plotOutput("plot_pos_strength")
        ),
        
        # Dvorak Outcomes----
        conditionalPanel(
          condition = "input.category == 'Championships vs Dvorak'",
          plotOutput("plot_dvorak")
        )
      )
    )
  )
)