# -*- coding: utf-8 -*-
"""
WTA Scraper
Author:  Joseph DeGregorio

Description:  This python script gathers all of the hike page URLs 
from the Washington Trails Association (WTA) webpage (www.wta.org/).

"""
#--------------------------------------------#
#                  Setup
#--------------------------------------------#

#Import Packages/Functions
import requests
import pandas as pd
from bs4 import BeautifulSoup
from numpy import arange
from time import sleep


#Create list to store extracted hike URLs
hike_urls = []

#--------------------------------------------#
#               Generate Page URLS
#--------------------------------------------#

#Define WTA start URL
url_base = 'https://www.wta.org/go-outside/hikes?b_start:int='

#Define page increments
url_pages = arange(0, 5000, 30)

#Print Start
print("\n")
print("Scraping Starting...  now!!!")
print("\n")

for p in list(range(len(url_pages))):
    
    url = url_base + str(url_pages[p])
    
    #--------------------------------------------#
    #               Gather HIKE URLS
    #--------------------------------------------#
    
    #Request HTLM from webpage
    req = requests.get(url)
    
    #Create Soup
    soup  = BeautifulSoup(req.text, 'html.parser')
    
    #Search for all tags containing the hike objects
    hikes = soup.find_all('a' , attrs={'class': 'listitem-title'}, href=True)
    
    #Check if page is empty
    if len(hikes) == 0:
        break
    
    #Extract hike URLs
    for i in list(arange(0, len(hikes), 1)):
        hike_urls.append(hikes[i]['href'])
        #print(hike_urls[i])
    
    #Print progress
    print("Scraped URLs:  :", len(hike_urls))
 
    #Wait 2 seconds before requesting next page
    sleep(2)

#Print Complete
print("\n")
print("Scraping Complete!!!")
print("\n")

#Save hike URLs to a csv file for the next phase of scraping
df = pd.DataFrame(hike_urls, columns=['URL'])
df.to_csv("hike_urls.csv", index = False, encoding = "utf-8")