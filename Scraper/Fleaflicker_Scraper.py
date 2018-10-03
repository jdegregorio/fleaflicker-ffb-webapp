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

    return  start_week, end_season, start_season


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

def getPoints( league_id , start_week, start_season, end_season ):

    # Create list to store team data
    point_data = []


    for season in list(reversed(range(end_season, start_season+1))):

        # Gather team information
        df_teams = getTeams(league_id, season)

        for i in list(range(0, df_teams.shape[0])):

            # Set team information
            team_id = df_teams.team_id[i]
            manager_id = df_teams.manager_id[i]
            manager_name = df_teams.manager_name[i]
            team_name = df_teams.team_name[i]

            for week in list(reversed(range(1, 17))):

                # Skip future weeks if current season
                if (season == start_season) and (week >= start_week):
                    continue

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

def getSchedules( league_id , start_season, end_season ):

    # Create list to store matchup data
    schedule_data = []

    for season in list(reversed(range(end_season, start_season+1))):

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

def findNew( df_points, df_schedules):
    x=1
    return x


# --------SCRIPT---------
import os
os.__file__
os.path.dirname("Fleaflicker_Scraper.py")

# Define Variables
league_id = '154290'

# Get Current Week/Season
start_week, start_season, end_season = getCurrent(league_id)

# Check for existing data
#df_points_old = pd.read_csv('../Data/points.csv', encoding = "utf-8")
#df_schedules_old = pd.read_csv("/Data/schedules.csv", encoding = "utf-8")

# Gather data using previously defined functions
df_points = getPoints(league_id , start_week, start_season, end_season)
df_schedules = getSchedules(league_id, start_season, end_season)

# Save Data
df_points.to_csv("../Data/points.csv", index = False, encoding = "utf-8")
df_schedules.to_csv("../Data/schedules.csv", index = False, encoding = "utf-8")
