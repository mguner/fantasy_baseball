import streamlit as st
import requests
from bs4 import BeautifulSoup as bs
import re
import csv
import pandas as pd
import datetime
import plotly.graph_objects as go
import numpy as np
from utils import *

# title of the site
st.title('CBS Fantasy Baseball Data Analysis')

# Example url for the user
st.write('Example URL: https://www.cbssports.com/fantasy/baseball/players/2507363/fernando-tatis/')

# take the user input
url = st.text_input('Enter the url')

# show user input url
st.write('you entered:', url)

# get data and years for the player
dataframe, years = stats(url = url)

# user select a metric
selected_metric = st.selectbox(
     'What are your stats you would like to focus',
     ('AVG', 'SLG', 'OBP'))

# user select years
selected_years = st.multiselect(
     'What are the years you would like to focus',
     years,
     ['2019'])

# Create visualization
fig = go.Figure()
for year in selected_years:
    year_data_length = dataframe.loc[year].shape[0]
    x = np.arange(year_data_length)
    year_data = dataframe.loc[year, selected_metric]
    fig.add_trace(go.Scatter(x=x, y=year_data,
                    mode='lines',
                    name= year + " " + selected_metric))

st.plotly_chart(fig)
