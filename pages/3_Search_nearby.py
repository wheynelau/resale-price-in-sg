import streamlit as st
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.utils.common_func import getcoordinates, find_nearest


st.title("Search nearby houses that were sold")

@st.cache_data
def load_csv():
    return pd.read_csv("assets/data/geo_coords_2017.csv", index_col=0)
if "data" not in st.session_state:
    st.session_state.data = load_csv()

address = st.text_input("Enter your address", placeholder="Enter your address or postal code")

if address:
    lat,lon = getcoordinates(address)
    find_nearest(st.session_state.data, lat, lon)
    results = st.session_state.data.query("distance <= 1").sort_index(ascending=False)

else:
    results = pd.DataFrame()

if not results.empty:
    flat_type = st.selectbox('Choose flat type:', 
                             options=np.insert(results['flat_type'].unique(),0,'All',)
                             )
    with st.expander("Additional settings (Distance, lease range and flat types)", expanded=False):
        lease_range = st.slider('Lease commencement date', min(results['lease_commence_date']), 
                                max(results['lease_commence_date']),
                                (min(results['lease_commence_date']), 
                                max(results['lease_commence_date'])),
                                help = "Select the range of lease commencement date")


        distance = st.slider('Radius in KM', 0.0,1.0,value = 0.0, step = 0.05,
                             help="This is just an estimate. 0 distance should return your exact block")

    # Applying filters
    filtered_results = results[results['distance'] <= distance]
    filtered_results = filtered_results[(filtered_results['lease_commence_date'] >= lease_range[0]) &
                                         (filtered_results['lease_commence_date'] <= lease_range[1])]
    if flat_type != 'All':
        filtered_results = filtered_results[filtered_results['flat_type'] ==flat_type]
    filtered_results['month'] = filtered_results['year'].astype(str) + '-' + filtered_results['month'].astype(str)
    filtered_results['lease_commence_date'] = filtered_results['lease_commence_date'].astype(str)
    filtered_results['price_per_sqm'] = filtered_results['resale_price'] / filtered_results['floor_area_sqm']

    st.markdown("### Results\n"
                "The columns can be sorted by clicking on the column name. "
                "Note that only the first 100 results are shown."
                )
    st.dataframe(filtered_results[['month','lease_commence_date','remaining_lease_year', 'flat_type',
                               'storey_range','floor_area_sqm','price_per_sqm','resale_price','address',
                               'distance'
                               ]]
                               .head(100), hide_index=True,
                               column_config={
                                   'price_per_sqm': st.column_config.NumberColumn(
                                       "Price per SQM ($)", width= 'small',format="$ %.2f"),
                                    'resale_price': st.column_config.NumberColumn(
                                        "Resale Price ($)", format="$ %d"),
                                    'distance': st.column_config.NumberColumn(
                                        "Distance (KM)", format="%.2f"),
                                    'remaining_lease_year': st.column_config.NumberColumn(
                                        "Remaining Lease (Years)", format="%d"),
                                    'floor_area_sqm': st.column_config.NumberColumn(
                                        "Floor Area (SQM)", format="%d"),
                                    'month': st.column_config.DatetimeColumn(
                                        "Month", format="MMM-YYYY"),
                                       },
                                       )