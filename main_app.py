import streamlit as st
import requests
from bs4 import BeautifulSoup as bs
import re
import csv
import pandas as pd
import datetime
import plotly.graph_objects as go
import numpy as np
import os
from utils import *

# title of the site
st.title('CBS Fantasy Baseball Data Analysis')

# Example url for the user
st.write("Find a Player from CBS Website: https://www.cbssports.com/fantasy/baseball/stats/") 


with st.expander("See more explanation"):
     st.write("""
         When you go to the link given above, find the player
         whose data you would like to analyse. Click on the name of the player and 
         this will take you to the player's page. You need to copy it and paste it below.
     """)
     st.image("images/cbs_stats.png", use_column_width= True)
     st.write("""As you see below, if you click on the name of the Fernando Tatis
     you will end up in the player page. Copy the link and paste is below.
    """)
     st.image("images/tatis.png", use_column_width= True)
# take the user input
url = st.text_input('Enter the url')
url = url.strip()

if not url:
    url = 'https://www.cbssports.com/fantasy/baseball/players/2507363/fernando-tatis/'
# show user input url
st.write('you entered:', url)

with st.expander("Expand if it takes too long"):
     st.write("""
         If the player you choose has 10+ years of history in MLB 
         taking all of their data might take some time.
         Even in the worst case scenario this shouldn't take more than a couple of minutes though.
     """)
# get data and years for the player
dataframe, years = scraper(url = url)

# user select a metric
selected_metric = st.selectbox(
     'What are your stats you would like to focus. You can select one and change it later.',
     ('AVG', 'SLG', 'OBP'))

# user select years
selected_years = st.multiselect(
     'What are the years you would like to focus. You can select multiple and change later again.',
     years,
     ['2019'])

# user select some day of the week
selected_days = st.multiselect(
     'What are the years you would like to focus. You can select multiple and change later again.',
     ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
     ['Friday', 'Saturday', 'Sunday'])

day_dict = {'Monday': 0,
            'Tuesday': 1,
            'Wednesday':2,
            'Thursday': 3,
            'Friday':4,
            'Saturday':5,
            'Sunday':6}

days = [day_dict.get(key) for key in selected_days]
dataframe = dataframe[dataframe.dayofweek.isin(days)]
# Create visualization
fig = go.Figure()
for year in selected_years:
    year_data_length = dataframe.loc[year].shape[0]
    x = np.arange(year_data_length)
    year_data = dataframe.loc[year, selected_metric]
    fig.add_trace(go.Scatter(x=x, y=year_data,
                    mode='lines',
                    name= year + " " + selected_metric))

with st.container():
    player_name = dataframe.player_name.unique()[0]
    st.write(f'Player: {player_name}')
    st.plotly_chart(fig)
