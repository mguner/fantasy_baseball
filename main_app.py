import streamlit as st
import requests
from bs4 import BeautifulSoup as bs
import re
import csv
import pandas as pd
import datetime
import plotly.graph_objects as go
import numpy as np
st.title('CBS Fantasy Baseball Data Analysis')

st.write('Example URL: https://www.cbssports.com/fantasy/baseball/players/2507363/fernando-tatis/')

url = st.text_input('Enter the url')

st.write('you entered:', url)

def yearLinks(soup):
    links = []
    base_url = 'https://www.cbssports.com'
    drop_down = soup.find_all('ul', 'Dropdown-list')[0]
    for url in drop_down.find_all('a'):
        links.append(base_url + url['href'] )
    return links



@st.cache
def stats(url):
    years = []
    header_dictionary = {'AVG':-4, 'SLG':-3, 'OBP':-2 } 
    field_names = ['player_name', 'date'] + ['AVG', 'SLG', 'OBP']
    metrics = ['AVG', 'SLG', 'OBP']
    player_name = url.split('/')[-2]
    player_id = url.split('/')[-3]
    player_url = f'https://www.cbssports.com/fantasy/baseball/players/game-log/2021/{player_id}/{player_name}/'
    with open(f'{player_name}.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        response = requests.get(player_url)
        soup = bs(response.content, features="html.parser")
        links = yearLinks(soup)
        for url in links:
            year = url.split('/')[-4]
            response = requests.get(url)
            soup = bs(response.content, features="html.parser")
            try:
                table = soup.find_all('table', 'data compact')[0]
                years.append(year)
                for month in table.findAll('tbody'):
                    for row in month.findAll('tr'):
                        row_data = {}
                        row_data['player_name'] = player_name 
                        day = row.findAll('td')[0].text
                        date = datetime.datetime.strptime(day + '/'+ year, '%m/%d/%Y' )
                        row_data['date'] = date
                        for s in metrics:
                            s_index = header_dictionary[s]
                            row_data[s] = float(row.findAll('td')[s_index].text)
                        writer.writerow(row_data)
            except:
                print('No content for:', url)
    df = pd.read_csv(f'{player_name}.csv',
                         index_col = 'date', 
                         parse_dates= True, 
                         infer_datetime_format= True)
    return df, years

dataframe, years = stats(url = url)

selected_metrics = st.multiselect(
     'What are your stats you would like to focus',
     ['AVG', 'SLG', 'OBP'],
     ['AVG'])

selected_years = st.multiselect(
     'What are the years you would like to focus',
     years,
     ['2019'])

# Create traces
fig = go.Figure()
for year in selected_years:
    year_data_length = dataframe.loc[year].shape[0]
    x = np.arange(year_data_length)
    year_data = dataframe.loc[year, 'AVG']
    fig.add_trace(go.Scatter(x=x, y=year_data,
                    mode='lines',
                    name= year + 'AVG'))

st.plotly_chart(fig)
