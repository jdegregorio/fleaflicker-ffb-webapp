fluidPage(
  
  # ---- Header Start----
  fluidRow(
    titlePanel(
      img(src = "wcb-xii-logo-small-2.png", align = "right")
    ),
    h1("Will Carter League Analytics", align = "center"),
    h3(textOutput("jimsucks"), align = "right")
  ),
  
  # ---- Page ----
  fluidRow(
    sidebarLayout(
      position = "left",
      
      # ---- Side Panel----
      sidebarPanel(
        h3("Options"),
        helpText("Select the type of analysis and preferred filters. Be sure to select the recommended formatting for an improved experience."),
        inp.chk.jimsucks,  # Optional Formatting ("Jim Sucks")
        inp.select.category,  # Plot Category
        uiOutput("ui")  # Plot-specific inputs
      ),
      
      # ---- Output Panel----
      mainPanel(
        
        # ---- Category Header----
        h3(textOutput("selected_category")),
        
        # ---- Power Rankings----
        conditionalPanel(
          condition = "input.category == 'Power Rankings'",
          plotOutput("plot_pr")
        ),
        
        # ---- Matchup Stats ----
        conditionalPanel(
          condition = "input.category == 'H2H Stats'",
          h4("Records"),
          htmlOutput("h2hrecords"),
          h4("Point Differential"),
          htmlOutput("h2hpoints")
        ),
        
        # ---- Distribution Plots----
        conditionalPanel(
          condition = "input.category == 'Point Distribution'",
          plotOutput("plot_dist")
        ),
        
        # ---- Positional Strength----
        conditionalPanel(
          condition = "input.category == 'Positional Strength'",
          plotOutput("plot_pos_strength")
        ),
        
        # ---- Shame ----
        conditionalPanel(
          condition = "input.category == 'Shame'",
          plotOutput("plot_dvorak"),
          plotOutput("plot_gegg")
        )
      )
    )
  )
)