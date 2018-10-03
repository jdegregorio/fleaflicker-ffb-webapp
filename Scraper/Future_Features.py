# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 19:49:53 2018

@author: Joe
"""

def getMatchIds( league_id , start_week, start_season, end_season ):

    # Gather matchup ids, loop through season/weeks
    match_ids = []
    for season in list(reversed(range(end_season, start_season+1))):
        for week in list(reversed(range(1, 17))):

            # Skip future weeks if current season
            if (season == start_season) and (week >= start_week):
                continue

            # Concatenate league id to form league url
            url = ('https://www.fleaflicker.com/nfl/leagues/' + str(league_id) +
                   '/scores?season=' + str(season) + '&week=' + str(week))

            # Sleep 2 sec before loading page
            sleep(2)

            # Print Status
            print(url)

            # Request page and create soup
            req = reqPage(url)

            # Create Soup
            soup  = BeautifulSoup(req.text, 'html.parser')
            if type(soup) is type(None):
                print('No soup for you...  ', url)
                continue

            # Extract matchup ids
            target = soup.find_all('a', href=True)
            for a in target:
                val = re.findall('(?<=/scores/)[0-9]{1,}', a['href'])
                if len(val) > 0:
                    val = int(val[0])
                    match_ids.append([season, week, val])

    # Convert to Dataframe
    df = pd.DataFrame.from_records(match_ids,
                                   columns = ['season', 'week', 'match_id'])

    # Remove Duplicates
    df.drop_duplicates(keep='first', inplace=True)
    df.reset_index(inplace=True)

    return df

def getMatchups( league_id , start_week, start_season, end_season ):

    # Create list to store matchup data
    matchup_data = []

    # Get match ids
    df_matchups = getMatchIds(league_id , start_week, start_season, end_season)

    for i in list(range(0, df_matchups.shape[0])):

        # Set matchup information
        season = df_matchups['season'][i]
        week = df_matchups['week'][i]
        match_id = df_matchups['match_id'][i]

        # Concatenate league id to form league url
        url = ('https://www.fleaflicker.com/nfl/leagues/' + str(league_id) +
               '/scores/' + str(match_id))

        # Sleep 2 sec before loading page
        sleep(2)

        # Print Status
        print(url)

        # Request page and create soup
        req = reqPage(url)

        # Create Soup
        soup  = BeautifulSoup(req.text, 'html.parser')
        if type(soup) is type(None):
            print('No soup for you...  ', url)
            continue


        # Find Primary Table
        table = soup.find_all('table',
                              attrs={'class': ('table-group table table-st'
                                     'riped table-bordered table-hover')})[1]

        # Find teams
        teams = table.thead.find_all('a', href = True)

        # ---------------Extract Left Side--------------------
        team_id = re.findall('(?<=teams/)[0-9]{1,}', teams[0]['href'])[0]

        # Gather all rows in table for left side
        rows = table.find_all('tr')

        # Loop through rows for left side
        for row in rows:

            # Find all columns within row
            try:
                cols = row.find_all('td')
            except:
                continue

            # Player ID
            try:
                target = cols[0].find_all('a', href=True)[0]
                player_id = re.findall('(?<=-)[0-9]{1,}', target['href'])[0]
            except:
                continue

            # Player Name
            key = 'player_name'
            try:
                target = cols[0].find('div', attrs={'class': 'player'})
                val = target.find('a', attrs={'class': 'player-text'}).text.strip()
                matchup_data.append([season, week, match_id, team_id,
                     player_id, key, val])

            except:
                print('    -Could not find attribute: %s' % (key))

            # Player Position
            key = 'player_pos'
            try:
                target = cols[0].find('div', attrs={'class': 'player'})
                val = target.find('span', attrs={'class': 'position'}).text.strip()
                matchup_data.append([season, week, match_id, team_id,
                                     player_id, key, val])
            except:
                print('    -Could not find attribute: %s' % (key))

            # Player Team
            key = 'player_team'
            try:
                target = cols[0].find('div', attrs={'class': 'player'})
                val = target.find('span', attrs={'class': 'player-team'}).text.strip()
                matchup_data.append([season, week, match_id, team_id,
                                     player_id, key, val])

            except:
                print('    -Could not find attribute: %s' % (key))

            # Set Position
            key = 'set_pos'
            try:
                val = cols[5].text.strip()
                matchup_data.append([season, week, match_id, team_id,
                                     player_id, key, val])
            except:
                print('    -Could not find attribute: %s' % (key))

            # Fantasy Points
            key = 'points'
            try:
                val = cols[3].text.strip()
                matchup_data.append([season, week, match_id, team_id,
                                     player_id, key, val])
            except:
                print('    -Could not find attribute: %s' % (key))


        # ---------------Extract Right Side--------------------
        team_id = re.findall('(?<=teams/)[0-9]{1,}', teams[1]['href'])[0]

        # Gather all rows in table for right side
        rows = table.find_all('tr')

        # Loop through rows for right side
        for row in rows:

            # Find all columns within row
            try:
                cols = row.find_all('td')
            except:
                continue

            # Player ID
            try:
                target = cols[-1].find_all('a', href=True)[0]
                player_id = re.findall('(?<=-)[0-9]{1,}', target['href'])[0]
            except:
                continue

            # Player Name
            key = 'player_name'
            try:
                target = cols[-1].find('div', attrs={'class': 'player'})
                val = target.find('a', attrs={'class': 'player-text'}).text.strip()
                matchup_data.append([season, week, match_id, team_id,
                     player_id, key, val])

            except:
                print('    -Could not find attribute: %s' % (key))

            # Player Position
            key = 'player_pos'
            try:
                target = cols[-1].find('div', attrs={'class': 'player'})
                val = target.find('span', attrs={'class': 'position'}).text.strip()
                matchup_data.append([season, week, match_id, team_id,
                                     player_id, key, val])
            except:
                print('    -Could not find attribute: %s' % (key))

            # Player Team
            key = 'player_team'
            try:
                target = cols[-1].find('div', attrs={'class': 'player'})
                val = target.find('span', attrs={'class': 'player-team'}).text.strip()
                matchup_data.append([season, week, match_id, team_id,
                                     player_id, key, val])

            except:
                print('    -Could not find attribute: %s' % (key))

            # Set Position
            key = 'set_pos'
            try:
                val = cols[5].text.strip()
                matchup_data.append([season, week, match_id, team_id,
                                     player_id, key, val])
            except:
                print('    -Could not find attribute: %s' % (key))

            # Fantasy Points
            key = 'points'
            try:
                val = cols[7].text.strip()
                matchup_data.append([season, week, match_id, team_id,
                                     player_id, key, val])
            except:
                print('    -Could not find attribute: %s' % (key))


    # Save as pandas dataframe
    df = pd.DataFrame.from_records(matchup_data,
                                   columns = ['season', 'week', 'match_id',
                                              'team_id', 'player_id', 'key',
                                              'val'])

    # Find Duplicates (troubleshooting only)
    #df[df.duplicated()]

    # Create ID column for pivoting
    df['ID'] = (df['season'].astype(str) + ',' +
                df['week'].astype(str) + ',' +
                df['match_id'].astype(str) + ',' +
                df['team_id'].astype(str) + ',' +
                df['player_id'].astype(str))


    df.drop(columns = ['season', 'week', 'match_id', 'team_id', 'player_id'],
            inplace=True)

    # Pivot Key/Value Columns
    df = df.pivot(index = 'ID', columns = 'key', values = 'val')
    df.reset_index(inplace = True)

    # Split ID back into individual columns
    df[['season', 'week', 'match_id', 'team_id', 'player_id']] = df.ID.str.split(',', expand=True)
    df.drop(columns = ['ID'], inplace=True)

    # Organize Columns
    df = df[['season', 'week', 'match_id', 'team_id', 'player_id',
             'player_name', 'player_pos', 'player_team', 'set_pos', 'points']]

    # Fill blank scores with zero
    df.points.replace('—', '0', inplace=True)

    return df
