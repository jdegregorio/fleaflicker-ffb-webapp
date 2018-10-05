fluidPage(
  
  # ---- Header Start----
  fluidRow(
    titlePanel(
      img(src = "wcb-xii-logo-small-2.png", align = "right")
    ),
    h1("Will Carter League Overview", align = "center"),
    h3(textOutput("jimsucks"), align = "right")
  ),
  
  # ---- Page ----
  fluidRow(
    sidebarLayout(
      position = "left",
      
      # ---- Side Panel----
      sidebarPanel(
        h3("Options"),
        helpText("This app allows you to explore the stats of the Will Carter Fantasy Football League"),
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
        
        # ---- Dvorak Outcomes----
        conditionalPanel(
          condition = "input.category == 'Championships vs Dvorak'",
          plotOutput("plot_dvorak")
        )
      )
    )
  )
)