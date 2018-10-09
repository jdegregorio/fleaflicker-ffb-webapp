function(input, output) {
  
  # ---- Dynamic Input Options ----
  output$ui <- renderUI({
    
    # Dynamically change inputs based on category type
    switch(input$category,
           "Power Rankings" = tagList(inp.slider.season),
           
           "H2H Stats" = tagList(inp.slider.season),

           "Point Distribution" = tagList(inp.slider.season,
                                          inp.chkgrp.managers,
                                          inp.action.update),

           "Positional Strength" = tagList(inp.slider.season,
                                           inp.grp.1,
                                           inp.action.update),
           
           "Shame" = tagList(inp.slider.season)
    )
    
  })
  
  # ---- Render Output ----
  
  # Selected Category
  output$selected_category <- renderText({input$category})
  
  # Jim Sucks Status
  output$jimsucks <- renderText({ifelse(input$js_checkbox == TRUE, "Jim Sucks", "")})
  
  # Power Rankings Plot
  output$plot_pr <- renderPlot({
    
    #Input Requirements
    req(input$season)
    
    #Gather Data
    tmp.plot <- df.stats %>%
      filter(! set_pos %in% c("BN", "TAXI"),
             season >= input$season[1],
             season <= input$season[2]) %>%
      group_by(team_id, season, week) %>%
      summarise(points_total = sum(points)) %>%
      ungroup() %>%
      left_join(df.teams %>% select(team_id, manager_name_short), by="team_id") %>%
      arrange(season, week) %>%
      mutate(week = paste0(season, "-", week)) %>%
      mutate(week = factor(week, ordered = TRUE))
    
    # Generate Plot
    ggplot(tmp.plot, aes(x = as.integer(week), y = points_total, col = manager_name_short)) +
      geom_smooth(method = 'loess', formula = 'y ~ x',level = 0.5, span = 1, alpha = 0.15) +
      scale_color_discrete(name = "Manager") +
      xlab("Weeks") +
      ylab("Mean Points")
    
  })
  
  # H2H Records
  output$h2hrecords <- reactive({
    
    # Input Requirements
    req(input$season)
    
    # Gather Wins
    tmp.plot.win <- df.sched %>%
      left_join(df.teams %>% select(team_id, manager_name_short), by = "team_id") %>%
      rename(manager_home = manager_name_short) %>%
      left_join(df.teams %>% select(team_id, manager_name_short), by = c("team_id_opp" = "team_id")) %>%
      rename(manager_away = manager_name_short) %>%
      select(-team_id, -team_id_opp) %>%
      filter(season >= input$season[1],
             season <= input$season[2]) %>%
      group_by(manager_home, manager_away) %>%
      summarize(Wins = length(result[result == "W"])) %>%
      ungroup() %>%
      spread(key = manager_away,
             value = Wins,
             fill = 0)
    
    # Rename rows
    rownames(tmp.plot.win) <- tmp.plot.win$manager_home
    tmp.plot.win$manager_home <- NULL
    
    # Gather Losses
    tmp.plot.loss <- df.sched %>%
      left_join(df.teams %>% select(team_id, manager_name_short), by = "team_id") %>%
      rename(manager_home = manager_name_short) %>%
      left_join(df.teams %>% select(team_id, manager_name_short), by = c("team_id_opp" = "team_id")) %>%
      rename(manager_away = manager_name_short) %>%
      filter(season >= input$season[1],
             season <= input$season[2]) %>%
      select(-team_id, -team_id_opp) %>%
      group_by(manager_home, manager_away) %>%
      summarize(Losses = length(result[result == "L"])) %>%
      ungroup() %>%
      spread(key = manager_away,
             value = Losses,
             fill = 0)
    
    # Rename rows
    rownames(tmp.plot.loss) <- tmp.plot.loss$manager_home
    tmp.plot.loss$manager_home <- NULL
    
    # Merge
    for (i in 1:nrow(tmp.plot.win)) {
      for (j in 1:ncol(tmp.plot.win)) {
        tmp.plot.win[i,j] <- paste(tmp.plot.win[i,j], tmp.plot.loss[i,j], sep = "-")
        tmp.plot.win[i,j] <- ifelse(j == i, "-", tmp.plot.win[i,j])
      }
    }
    
    # Generate HTML Table
    tmp.plot.win %>%
      kable() %>%
      kable_styling(bootstrap_options = c("hover", "condensed", "responsive"), full_width = F) %>%
      column_spec(1, bold = T) %>%
      row_spec(0, bold = T) %>%
      row_spec(1:12, align = "center") %>%
      #cell_spec(tmp.plot.win$Jim, popover = spec_popover(content = "Jim Sucks")) %>%
      add_footnote(c("\n Rows represent the home team, columns are the away team", 
                     "Records shown with notation:  home-away"), 
                   notation = "none")
    
  })
  
  # H2H Point Differential
  output$h2hpoints <- reactive({
    
    # Input Requirements
    req(input$season)
    
    # Gather Wins
    tmp.plot.win <- df.sched %>%
      filter(season >= input$season[1],
             season <= input$season[2]) %>%
      left_join(df.teams %>% select(team_id, manager_name_short), by = "team_id") %>%
      rename(manager_home = manager_name_short) %>%
      left_join(df.teams %>% select(team_id, manager_name_short), by = c("team_id_opp" = "team_id")) %>%
      rename(manager_away = manager_name_short) %>%
      select(-team_id, -team_id_opp) %>%
      mutate(point_dif = score_team - score_opp) %>%
      group_by(manager_home, manager_away) %>%
      summarize(point_dif = round(sum(point_dif),0)) %>%
      spread(key = manager_away,
             value = point_dif,
             fill = 0)
    
    # Rename rows
    rownames(tmp.plot.win) <- tmp.plot.win$manager_home
    tmp.plot.win$manager_home <- NULL
    
    
    # Merge
    for (i in 1:nrow(tmp.plot.win)) {
      for (j in 1:ncol(tmp.plot.win)) {
        tmp.plot.win[i,j] <- ifelse(j == i, "-", tmp.plot.win[i,j])
      }
    }
    
    tmp.plot.win %>%
      kable() %>%
      kable_styling(bootstrap_options = c("hover", "condensed", "responsive"), full_width = F) %>%
      column_spec(1, bold = T) %>%
      row_spec(0, bold = T) %>%
      row_spec(1:12, align = "center") %>%
      add_footnote(c("\n Rows represent the home team, columns are the away team"), 
                   notation = "none")
    
    
  })
  
  # Distribution Plot
  output$plot_dist <- renderPlot({
    
    #Input Requirements
    req(input$season, isolate(input$managers))
    
    # Add dependency to update buttom
    input$update
    
    #Gather Data
    tmp.plot <- df.stats %>%
      filter(! set_pos %in% c("BN", "TAXI"),
             season >= input$season[1],
             season <= input$season[2],
             manager_name_short %in% isolate(input$managers)) %>%
      group_by(season, week, manager_name_short) %>%
      summarise(point_total = sum(points))

    # Generate Plot
    ggplot(tmp.plot,
           aes(x = point_total,
               fill = manager_name_short)) +
      geom_density(alpha = 0.3) +
      labs(x = "Points", y = "Density", fill = "Manager")
    
  })
  
  # Positional Strength
  output$plot_pos_strength <- renderPlot({
    
    #Input Requirements
    #req(input$season, isolate(input$managers), isolate(input$positions), isolate(input$lutype))
    
    # Add dependency to update buttom
    input$update
    
    # Prep Data
    tmp.plot <- df.stats %>%
      filter(season >= input$season[1],
             season <= input$season[2],
             manager_name_short %in% isolate(input$managers),
             player_pos %in% isolate(input$positions),
             lineup_type %in% isolate(input$lutype)) %>%
      arrange(season, week) %>%
      mutate(week = paste0(season, "-", week)) %>%
      mutate(week = factor(week, ordered = TRUE))
    
    # Plot
    ggplot(tmp.plot, aes(x = as.integer(week), 
                         y = points, 
                         col = manager_name_short,
                         linetype = player_pos)) +
      geom_smooth(method = 'loess', formula = 'y ~ x', level = 0.5, span = 0.8, alpha = 0.2) +
      labs(x = "Weeks", y = "Points", col = "Manager", linetype = "Position")

  })
  
  # Goose Eggs
  output$plot_gegg <- renderPlot({
    
    # Input Requirements
    req(input$season)
    
    # Build Dataset
    tmp.plot.all <- df.stats %>%
      filter(lineup_type == "Starters",
             season >= input$season[1],
             season <= input$season[2]) %>%
      select(manager_name_short,
             season,
             week,
             set_pos,
             player_name,
             points) %>%
      group_by(manager_name_short) %>%
      summarise(count_all = n())
    
    tmp.plot.ltz <- df.stats %>%
      filter(lineup_type == "Starters",
             season >= input$season[1],
             season <= input$season[2]) %>%
      select(manager_name_short,
             season,
             week,
             set_pos,
             player_name,
             points) %>%
      filter(points <= 0) %>%
      group_by(manager_name_short) %>%
      summarise(count_ltz = n()) %>%
      left_join(tmp.plot.all, by = "manager_name_short") %>%
      mutate(rate = count_ltz/count_all) %>%
      select(Manager = manager_name_short,
             Rate = rate)
    
    #Plot team names
    ggplot(tmp.plot.ltz, aes(x = reorder(Manager, Rate), 
                             y = Rate,
                             fill = Rate)) +
      geom_bar(stat = "identity", alpha = 0.8) +
      scale_fill_gradient(low = "gray95", high = "red4") +
      labs(title = "Goose Eggs, or worse...",
           subtitle = "Rate of Starts with Zero or Fewer Points") +
      xlab("Manager") +
      ylab("Goose Egg Rate") +
      scale_y_continuous(labels = scales::percent) +
      theme(plot.title = element_text(hjust = 0.5),
            plot.subtitle = element_text(hjust = 0.5),
            legend.position = "none") +
      coord_flip()
    
  })
  
  # Dvorak Outcomes Plot
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
      scale_fill_manual(values=c("red4", "forestgreen")) +
      labs(title = "Championship Outcomes vs. Dvorak",
           x = "Manager",
           y = "Outcome") +
      ylim(c(-2,2)) +
      theme(legend.position = "none") +
      coord_flip()
    
  })
}