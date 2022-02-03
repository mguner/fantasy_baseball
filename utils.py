import streamlit as st
import requests
from bs4 import BeautifulSoup as bs
import csv
import pandas as pd
from datetime import datetime
import os

# gather urls for each year
def yearLinks(soup):
    """
    Each year data for a player shown in a different page. 
    This function creates a list of urls from a given soup object of the player's page.
    Parameters
    --------
    soup: bs4.BeautifulSoup object. Created from player's page html.
    Returns
    ---------
    links: list. List of strings. Each string links to the player's page for different year's data.
    """
    links = []
    base_url = 'https://www.cbssports.com'
    drop_down = soup.find_all('ul', 'Dropdown-list')[0]
    for url in drop_down.find_all('a'):
        links.append(base_url + url['href'] )
    return links

# get name and id from url
def player_info_from_url(url):
    player_name = url.split('/')[-2]
    player_id = url.split('/')[-3]
    return player_name, player_id

# given year, player_name and id create the url.
def create_url(year, player_name, player_id):
    base = 'https://www.cbssports.com/'
    extension = f'fantasy/baseball/players/game-log/{year}/{player_id}/{player_name}/'
    return base+extension

# from a url create soup object
def make_soup(url):
    response = requests.get(url)
    soup = bs(response.content, features="html.parser")
    return soup

# cache so that page would not refresh each time.
@st.cache
def stats(url):
    # to keep the list of years a player played in MLB
    years = []
    # in the tables(html) the indexes of metrics
    header_dictionary = {'AVG':-4, 'SLG':-3, 'OBP':-2 } 
    field_names = ['player_name', 'date'] + ['AVG', 'SLG', 'OBP']
    # we can add additional metrics later on
    metrics = ['AVG', 'SLG', 'OBP']
    # get player name and id
    player_name, player_id = player_info_from_url(url)
    # create an url for one of the player's pages.
    player_url = create_url('2021', player_name, player_id)
    # create a temporary csv file. Not sure this is needed.
    with open(f'{player_name}.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        # create soup
        soup = make_soup(player_url)
        # create links for each year
        links = yearLinks(soup)
        for url in links:
            # get the year
            year = url.split('/')[-4]
            # soup for a particular year data
            soup = make_soup(url)
            try:
                # main table in the page
                table = soup.find('table', 'data compact')
                # append year in try so that if table is empty user don't see it
                years.append(year)
                # data kept in monthly - each month data is a table.
                for month in table.findAll('tbody'):
                    # we run through each row 
                    for row in month.findAll('tr'):
                        row_data = {}
                        # get player data - for consistency
                        row_data['player_name'] = player_name 
                        # day of the game that data is coming from
                        day = row.findAll('td')[0].text
                        # add the year to date format
                        date = datetime.strptime(day+ '/' + year, '%m/%d/%Y' )
                        row_data['date'] = date
                        # focus only on the metrics listed at the begining
                        for s in metrics:
                            s_index = header_dictionary[s]
                            row_data[s] = float(row.findAll('td')[s_index].text)
                        writer.writerow(row_data)
            except:
                print('No content for:', url)
    # read the csv to a dataframe
    df = pd.read_csv(f'{player_name}.csv',
                         index_col = 'date', 
                         parse_dates= True, 
                         infer_datetime_format= True)
    # delete the csv 
    os.remove(f'{player_name}.csv')
    return df, years