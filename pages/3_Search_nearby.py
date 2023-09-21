import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.utils.common_func import getcoordinates, find_nearest

st.title("Search nearby houses that were sold")
@st.cache_data
def load_csv():
    return pd.read_csv("assets/data/geo_coords_2017.csv", index_col=0)
if "data" not in st.session_state:
    st.session_state.data = load_csv()

address = st.text_input("Enter your address", "Blk 1 Jalan Bukit Merah")

if address:
    lat,lon = getcoordinates(address)
    find_nearest(st.session_state.data, lat, lon)
    results = st.session_state.data.query("distance <= 1").sort_index(ascending=False)

else:
    results = pd.DataFrame()

if not results.empty:
    lease_range = st.slider('Lease commencement date', min(results['lease_commence_date']), 
                            max(results['lease_commence_date']),
                             (min(results['lease_commence_date']), 
                              max(results['lease_commence_date'])))
    column2_value = st.selectbox('Choose flat type value:', options=results['flat_type'].unique())
    distance = st.slider('Radius in KM', 0.05,1.0, step = 0.05)

    # Applying filters
    filtered_results = results[results['distance'] <= distance]
    filtered_results = filtered_results[(filtered_results['lease_commence_date'] >= lease_range[0]) &
                                         (filtered_results['lease_commence_date'] <= lease_range[1])]
    filtered_results = filtered_results[filtered_results['flat_type'] == column2_value]
    filtered_results['month'] = filtered_results['year'].astype(str) + '-' + filtered_results['month'].astype(str)
    filtered_results['lease_commence_date'] = filtered_results['lease_commence_date'].astype(str)

    st.write(filtered_results[['month','lease_commence_date','remaining_lease_year','storey_range','floor_area_sqm','resale_price','address']].reset_index(drop=True))