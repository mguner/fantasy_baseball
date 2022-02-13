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
        'SB','CS','SH','SF','HBP','AVG','SLG%','YTDOBP%',
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
    df['dayofweek'] = df.date.dt.dayofweek
    df['Year'] = df.date.dt.year
    return df, years