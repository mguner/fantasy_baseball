import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
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

def cell_reader(cells):
    row_data = []
    for c in cells:
        if c.text:
            row_data.append(c.text)
        else:
            row_data.append(c.find('a')['href'])
    return  row_data

header = ['DATE','TEAM','home/away', 'OPPONENT','RESULT',
        'AB','R' ,'H','2B','3B','HR','RBI','BB','K',
        'SB','CS','SH','SF','HBP','AVG','SLG','YTDOBP',
        'FPTS']
new_header = header + ['date']

def scraper(url):
    # to keep the list of years a player played in MLB
    years = []
    player_name, player_id = player_info_from_url(url)
    # create an url for one of the player's pages.
    player_url = create_url('2021', player_name, player_id)
        # create soup
    soup = make_soup(player_url)
        # create links for each year
    links = yearLinks(soup)
    body = []
    for url in links:
        # get the year
        year = url.split('/')[-4]
        # soup for a particular year data
        soup = make_soup(url)
        try:
            years.append(year)
            table = soup.find('table', 'data compact')
            for month in table.findAll('tbody'):
                for row in month.findAll('tr'):
                    cells = row.findAll('td')
                    row_data = cell_reader(cells)
                    day = row_data[0]
                    date = datetime.strptime(day+ '/' + year, '%m/%d/%Y' )
                    row_data.append(date)
                    body.append(row_data)
        except:
            print('No content for:', url)
    df = pd.DataFrame(body, columns= new_header)
    df.loc[:, 'AB': 'HBP'] = df.loc[:,'AB': 'HBP'].astype(int)
    df.loc[:, 'AVG': 'FPTS'] = df.loc[:, 'AVG': 'FPTS'].astype(float)
    df['dayofweek'] = df.date.dt.dayofweek
    df['Year'] = df.date.dt.year
    return df, years

# Hits divided by At Bats
def daily_avg(df):
    avg = df.H/df.AB
    return avg.fillna(0)
# Calculates avg cumulatively
def cum_avg(df):
    avg = df.H.cumsum()/df.AB.cumsum()
    return avg.fillna(0)

# Hits + Walks + Hit By Pitch) divided by (At-bats + Walks + Hit By Pitch + Sacrifices)
def daily_obp(df):
    numerator = df.H + df.BB + df.HBP
    denom = df.AB + df.BB + df.HBP + df.SF
    return (numerator/denom).fillna(0)
def cum_obp(df):
    num = (df.H + df.BB + df.HBP).cumsum()
    denom = (df.AB + df.BB + df.HBP + df.SF).cumsum()
    return (num/denom).fillna(0)

# Total number of bases divided by At-bats
def daily_slg(df):
    first_base = df.H - (df['2B'] + df['3B'] + df['HR'])
    num = first_base + 2 * df['2B'] + 3*df['3B'] + 4*df['HR']
    return (num/df.AB).fillna(0)
def cum_slg(df):
    first_base = df.H - (df['2B'] + df['3B'] + df['HR'])
    num = first_base.cumsum() + 2 * df['2B'].cumsum() + 3*df['3B'].cumsum() + 4*df['HR'].cumsum()
    return (num/df.AB.cumsum()).fillna(0)


# returns the final version of the data
def cbs_data(url):
    df, years = scraper(url)
    df['daily_avg'] = daily_avg(df)
    df['daily_slg'] = daily_slg(df)
    df['daily_obp'] = daily_obp(df)
    return df, years

def select_metric_data(df, selected_metric):
    if selected_metric == 'AVG':
        return cum_avg(df)
    elif selected_metric == 'SLG':
        return cum_slg(df)
    else:
        return cum_obp(df)

    