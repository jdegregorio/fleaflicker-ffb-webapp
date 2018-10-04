# -*- coding: utf-8 -*-
"""
Matchup Scraper
Author: Joseph DeGregorio
Created: 9/19/2018

Description:  This python script gathers all of the matchup information from
the Fleaflicker fantasy football website.  The data includes each weekly head-
to-head matchup, as well as all of the player stats from each team every week.

"""
#--------------------------------------------#
#                  Setup
#--------------------------------------------#

# Import Packages/Functions
import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from time import sleep

# --------DEFINE FUNCTIONS---------

def reqPage( url ):

    # Define local variables
    headers = {'user-agent':('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleW'
                             'ebKit/537.36 (KHTML, like Gecko) Chrome/62.0.320'
                             '2.94 Safari/537.36')}
    req = ''
    attempt = 1
    attempt_max = 10  # Max attempts
    attempt_delay = 5

    # Try multiple attemps until succesful, with increasing delay
    while (req == '') and (attempt <= attempt_max):
        try:
            req = requests.get(url, headers = headers)
            break
        except:
            print("\n")
            print("Connection Error. Trying again in 15 seconds...")
            print("\n")
            attempt = attempt + 1
            sleep(attempt*attempt_delay)
            continue

    return req

def getCurrent( league_id ):

    # Concatenate league id to form league url
    league_url = ('https://www.fleaflicker.com/nfl/leagues/' + str(league_id) +
                  '/scores')

    # Request page and create soup
    req = reqPage(league_url)

    # Create Soup
    soup  = BeautifulSoup(req.text, 'html.parser')
    if type(soup) is type(None):
        return ''

    # Find Season Menu
    try:
        seasons = soup.find('ul', attrs={'class': 'dropdown-menu pull-right'}).find_all('li')
        end_season = int(seasons[0].text.strip())
        start_season = int(seasons[-1].text.strip())
    except:
        print('Could not extract seasons')


    # Look for drop-down menu to select week
    weeks = soup.find('ul', attrs={'class': 'dropdown-menu pull-left'})
    current_week = weeks.find('li', attrs={'class': 'active'})
    menu_items = weeks.find_all('li')
    for i in list(range(0, len(menu_items))):
        item = menu_items[i]
        if item == current_week:
            start_week = i

    return  start_week, start_season, end_season


def getTeams( league_id , season ):

    # Create list to store team data
    team_data = []

    # Concatenate league id to form league url
    league_url = ('https://www.fleaflicker.com/nfl/leagues/' + str(league_id) +
                  '?season='+ str(season))

    # Request page and create soup
    req = reqPage(league_url)

    # Create Soup
    soup  = BeautifulSoup(req.text, 'html.parser')
    if type(soup) is type(None):
        return ''

    # Loop through rows to find teams
    rows = soup.find_all('tr')
    for row in rows:

        # Team ID
        try:
                target = row.find('div' , attrs={'class': 'league-name'}).a.get('href')
                team_id = re.findall('(?<=teams/)[0-9]{1,}', target)[0]
        except:
            continue

        # Team Name
        key = 'team_name'
        try:
                val = row.find('div', attrs={'class': 'league-name'}).text.strip()
                team_data.append([team_id, key, val])
        except:
            print('    -Could not find attribute: %s' % (key))

        # Manager Name
        key = 'manager_name'
        try:
                val = row.find('a', attrs={'class': 'user-name'}).text.strip()
                team_data.append([team_id, key, val])
        except:
            print('    -Could not find attribute: %s' % (key))

        # Manager User ID
        key = 'manager_id'
        try:
                target = row.find('a', attrs={'class': 'user-name'}).get('href')
                val = target.rpartition('/')[-1]
                team_data.append([team_id, key, val])
        except:
            print('    -Could not find attribute: %s' % (key))


    #Save as pandas dataframe
    df = pd.DataFrame.from_records(team_data, columns = ['team_id', 'Key', 'Value'])
    df = df.pivot(index = 'team_id', columns = 'Key', values = 'Value')
    df.reset_index(inplace = True)

    return df

def getPoints( league_id , weeks_new ):

    # Create list to store team data
    point_data = []

    for week in weeks_new:
        season = week[0]
        week = week[1]

        # Gather team information
        df_teams = getTeams(league_id, season)

        for i in list(range(0, df_teams.shape[0])):

            # Set team information
            team_id = df_teams.team_id[i]
            manager_id = df_teams.manager_id[i]
            manager_name = df_teams.manager_name[i]
            team_name = df_teams.team_name[i]

            # Concatenate league id to form league url
            url = ('https://www.fleaflicker.com/nfl/leagues/' +
                          league_id + '/teams/' + str(team_id) + '?season='
                          + str(season) + '&week=' + str(week))

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
            table = soup.find('table',
                              attrs={'class': ('table-group table table-st'
                                      'riped table-bordered table-hover')})

            # Find rows in table
            rows = table.find_all('tr')

            for row in rows:

                # Player Name
                key = 'player_name'
                try:
                    target = row.find('div', attrs={'class': 'player'})
                    player_name = target.find('a', attrs={'class': 'player-text'}).text.strip()
                except:
                    continue

                # Player ID
                key = 'player_id'
                try:
                    target = row.find('div', attrs={'class': 'player'})
                    target = target.find('a', attrs={'class': 'player-text'})
                    target = target.get('href')
                    val = re.findall('(?<=-)[0-9]{1,}', target)[0]
                    point_data.append([team_id,  manager_id,  manager_name,
                                       team_name, season, week, player_name,
                                       key, val])
                except:
                    print('    -Could not find attribute: %s' % (key))

                # Player Position
                key = 'player_pos'
                try:
                    target = row.find('div', attrs={'class': 'player'})
                    val = target.find('span', attrs={'class': 'position'}).text.strip()
                    point_data.append([team_id,  manager_id,  manager_name,
                                       team_name, season, week, player_name,
                                       key, val])
                except:
                    print('    -Could not find attribute: %s' % (key))

                # Player Team
                key = 'player_team'
                try:
                    target = row.find('div', attrs={'class': 'player'})
                    val = target.find('span', attrs={'class': 'player-team'}).text.strip()
                    point_data.append([team_id,  manager_id,  manager_name,
                                       team_name, season, week, player_name,
                                       key, val])
                except:
                    print('    -Could not find attribute: %s' % (key))

                # Set Position
                key = 'set_pos'
                try:
                    target = row.find_all('td')[-1]
                    val = target.text.strip()
                    point_data.append([team_id,  manager_id,  manager_name,
                                       team_name, season, week, player_name,
                                       key, val])
                except:
                    print('    -Could not find attribute: %s' % (key))

                # Fantasy Points
                key = 'points'
                try:
                    target = row.find('a', attrs={'class': 'points-final'})
                    val = target.text.strip()
                    point_data.append([team_id,  manager_id,  manager_name,
                                       team_name, season, week, player_name,
                                       key, val])
                except:
                    print('    -Could not find attribute: %s' % (key))



    # Save as pandas dataframe
    df = pd.DataFrame.from_records(point_data,
                                   columns = ['team_id',  'manager_id',
                                              'manager_name', 'team_name',
                                              'season', 'week', 'player_name',
                                              'key', 'val'])

    # Find Duplicates (troubleshooting only)
    #df[df.duplicated()]

    # Create ID column for pivoting
    df['ID'] = (df['team_id'] + ',' + df['manager_id'].astype(str) + ',' +
                df['manager_name'].astype(str) + ',' +
                df['team_name'].astype(str) + ',' + df['season'].astype(str) +
                ',' + df['week'].astype(str) + ',' + df['player_name'])

    df.drop(columns = ['team_id', 'manager_id', 'manager_name', 'team_name',
                       'season', 'week', 'player_name'], inplace=True)

    # Pivot Key/Value Columns
    df = df.pivot(index = 'ID', columns = 'key', values = 'val')
    df.reset_index(inplace = True)

    # Split ID back into individual columns
    df[['team_id', 'manager_id', 'manager_name', 'team_name', 'season', 'week', 'player_name']] = df.ID.str.split(',', expand=True)
    df = df[['team_id', 'manager_id', 'manager_name', 'team_name', 'season', 'week', 'player_name', 'player_id', 'player_team', 'player_pos', 'set_pos', 'points']]

    # Replace NA points with 0
    df['points'] = df['points'].fillna(value='0')

    return df

def getSchedules( league_id , weeks_new ):

    # Create list to store matchup data
    schedule_data = []

    for week in weeks_new:
        season = week[0]

        # Gather team information
        df_teams = getTeams(league_id, season)

        for i in list(range(0, df_teams.shape[0])):

            # Set team information
            team_id = df_teams.team_id[i]

            # Concatenate league id to form league url
            url = ('https://www.fleaflicker.com/nfl/leagues/' +
                    league_id + '/teams/' + str(team_id) + '/schedule?season='
                    + str(season))

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
            try:
                table = soup.find('table',
                                  attrs={'class': ('table-group table table-st'
                                          'riped table-bordered table-hover')})
            except:
                continue

            # Find rows in table
            try:
                rows = table.find_all('tr')
            except:
                continue

            for row in rows:

                # Find all columns within row
                try:
                    cols = row.find_all('td')
                except:
                    continue

                # Week
                try:
                    target = cols[0].text
                    week = re.findall('^[0-9]{1,}', target)[0]
                except:
                    continue

                # Opponent ID
                key = 'team_id_opp'
                try:
                    target = cols[1].a.get('href')
                    val = re.findall('(?<=teams/)[0-9]{1,}', target)[0]
                    schedule_data.append([team_id, season, week, key, val])
                except:
                    print('    -Could not find attribute: %s' % (key))
                    continue

                # Type
                key = 'matchup_type'
                try:
                    val = cols[2].text
                    schedule_data.append([team_id, season, week, key, val])
                except:
                    print('    -Could not find attribute: %s' % (key))
                    continue

                # Result
                key = 'result'
                try:
                    val = cols[3].text[0]
                    schedule_data.append([team_id, season, week, key, val])
                except:
                    print('    -Could not find attribute: %s' % (key))
                    continue

                # Scores
                key = 'score'
                try:
                    val = cols[3].text[2:]
                    schedule_data.append([team_id, season, week, key, val])
                except:
                    print('    -Could not find attribute: %s' % (key))
                    continue

    # Save as pandas dataframe
    df = pd.DataFrame.from_records(schedule_data,
                                   columns = ['team_id', 'season', 'week',
                                              'key', 'val'])

    # Find Duplicates (troubleshooting only)
    #df[df.duplicated()]

    # Create ID column for pivoting
    df['ID'] = (df['team_id'] + ',' + df['season'].astype(str) + ',' +
                df['week'].astype(str))

    df.drop(columns = ['team_id', 'season', 'week'], inplace=True)

    # Pivot Key/Value Columns
    df = df.pivot(index = 'ID', columns = 'key', values = 'val')
    df.reset_index(inplace = True)

    # Remove missing values (not played yet)
    df = df[df.result.notnull()]

    # Split ID back into individual columns
    df[['team_id', 'season', 'week']] = df.ID.str.split(',', expand=True)
    df = df[['team_id', 'season', 'week', 'team_id_opp', 'matchup_type', 'result', 'score']]

    # Split Scores
    df[['score_team', 'score_opp']] = df.score.str.split('-', expand=True)
    df.drop(columns = ['score'], inplace=True)

    return df

def checkNew( league_id , filepath ):

    # Load file, flag if missing
    file_missing = False
    try:
        df_old = pd.read_csv(filepath, encoding = "utf-8")
    except:
        print('File not found, defaulting to all available weeks')
        file_missing = True

    # List out available weeks
    weeks_avl = []
    start_week, start_season, end_season = getCurrent(league_id)
    for season in list(reversed(range(end_season, start_season+1))):
        for week in list(reversed(range(1, 17))):
            # Skip future weeks if current season
            if (season == start_season) and (week > start_week):
                continue
            weeks_avl.append([season, week])

    # Return available weeks if there is no existing file
    if file_missing:
        return weeks_avl

    # If file does exist, extract week values
    weeks_old = df_old[['season', 'week']].drop_duplicates().values.tolist()

    # Find new available weeks not already stored in file
    weeks_new = [x for x in weeks_avl if x not in weeks_old]

    return weeks_new

def saveNew( df_new , filepath ):

    # Load file, flag if missing
    try:
        df_old = pd.read_csv(filepath, encoding = "utf-8")
    except:
        print('File not found, saving only new data')
        df_new.to_csv(filepath, index = False, encoding = "utf-8")
        return

    # Combine new/old and remove duplicates
    df_comb = df_old.append(df_new, ignore_index = True)
    df_comb.drop_duplicates(inplace=True)

    # Save Data
    df_comb.to_csv(filepath, index = False, encoding = "utf-8")

# --------SCRIPT---------

# Define Variables
league_id = '154290'
filepath_points = 'C:/scripts/data/points.csv'
filepath_schedules = 'C:/scripts/data/schedules.csv'

# Check for new data
weeks_new_points = checkNew(league_id, filepath_points)
weeks_new_schedule = checkNew(league_id, filepath_schedules)

# Gather new data
df_points = getPoints(league_id , weeks_new_points)
df_schedules = getSchedules(league_id, weeks_new_schedule)

# Save Data
saveNew(df_points, filepath_points)
saveNew(df_schedules, filepath_schedules)
