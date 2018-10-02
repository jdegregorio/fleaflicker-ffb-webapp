function(input, output) {
  
  # ----Selected Category----
  output$selected_category <- renderText({input$category})
  
  # ----Jim Sucks Status----
  output$jimsucks <- renderText({ifelse(input$js_checkbox == TRUE, "Jim Sucks", "")})
  
  # ----Power Rankings Plot----
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
  
  # ----Distribution Plot----
  output$plot_dist <- renderPlot({
    
    #Gather Data
    tmp.plot <- df.stats.startreg %>%
      left_join(df.managers %>% select(manager_id, manager_name_short), by="manager_id") %>%
      filter(season >= input$season[1] & season <= input$season[2]) %>%
      filter(manager_name_short %in% input$managers) %>%
      group_by(season, week, manager_name_short) %>%
      summarise(point_total = sum(points))
    
    # Generate Plot
    ggplot(tmp.plot, 
           aes(x = point_total, 
               fill = manager_name_short)) +
      geom_density(alpha = 0.3) +
      labs(x = "Points", y = "Density", fill = "Manager")
    
  })
  
  # ----Positional Strength----
  output$plot_pos_strength <- renderPlot({
    
    tmp.plot <- df.stats %>%
      filter(season >= input$season[1] & season <= input$season[2]) %>%
      filter(manager_name_short %in% input$managers) %>%
      filter(posrank_tot %in% input$positions) %>%
      arrange(season, week) %>%
      mutate(week = paste0(season, "-", week)) %>%
      mutate(week = factor(week, ordered = TRUE))
    
    ggplot(tmp.plot, aes(x = as.integer(week), 
                         y = points, 
                         col = manager_name_short,
                         linetype = posrank_tot)) +
      geom_smooth(level = 0.5, alpha = 0.2) +
      geom_vline(xintercept = seq(13, as.integer(max(tmp.plot$week)), 13), alpha = 0.2) +
      labs(x = "Weeks", y = "Points", col = "Manager", linetype = "Position")

  })
  
  # ----Dvorak Outcomes Plot----
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