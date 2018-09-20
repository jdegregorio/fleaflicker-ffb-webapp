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
from bs4 import BeautifulSoup
from numpy import arange
from time import sleep

# Parameters
delay = 3  # Time delay for loading pages

def reqPage( url ):

    #Define local variables
    headers = {'user-agent':('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleW'
                             'ebKit/537.36 (KHTML, like Gecko) Chrome/62.0.320'
                             '2.94 Safari/537.36')}
    req = ''
    attempt = 1
    attempt_max = 10  # Max attempts
    attempt_delay = 5

    #Try multiple attemps until succesful, with increasing delay
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

def getTeams( league_id ):

    # Create list to store team data
    team_data = []

    # Concatenate league id to form league url
    url_league = 'https://www.fleaflicker.com/nfl/leagues/' + league_id

    # Request page and create soup
    req = reqPage(url_league)

    # Create Soup
    soup  = BeautifulSoup(req.text, 'html.parser')
    if type(soup) is type(None):
        return ''

    # Loop through teams
    rows = soup.find_all('tr')
    for row in rows:

        # Team ID
        try:
                target = row.find('div' , attrs={'class': 'league-name'}).a.get('href')
                team_id = target.rpartition('/')[-1]
        except:
            print('    -Could not find TeamID')

        # Team Name
        key = 'TeamName'
        try:
                val = row.find('div', attrs={'class': 'league-name'}).text.strip()
                team_data.append([team_id, key, val])
        except:
            print('    -Could not find attribute: %s' % (key))

        # Manager Name
        key = 'ManagerName'
        try:
                val = row.find('a', attrs={'class': 'user-name'}).text.strip()
                team_data.append([team_id, key, val])
        except:
            print('    -Could not find attribute: %s' % (key))

        # Manager User ID
        key = 'ManagerID'
        try:
                target = row.find('a', attrs={'class': 'user-name'}).get('href')
                val = target.rpartition('/')[-1]
                team_data.append([team_id, key, val])
        except:
            print('    -Could not find attribute: %s' % (key))


    #Save as pandas dataframe
    df = pd.DataFrame.from_records(team_data, columns = ['TeamID', 'Key', 'Value'])
    df = df.pivot(index = 'TeamID', columns = 'Key', values = 'Value')
    df.reset_index(inplace = True)

    return df


league_id = '154290'
df_teams = getTeams(league_id)

