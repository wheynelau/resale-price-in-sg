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

address = st.text_input("Enter your address", placeholder="Enter your address or postal code")

if address:
    lat,lon = getcoordinates(address)
    find_nearest(st.session_state.data, lat, lon)
    results = st.session_state.data.query("distance <= 1").sort_index(ascending=False)

else:
    results = pd.DataFrame()

if not results.empty:
    flat_type = st.selectbox('Choose flat type value:', options=results['flat_type'].unique())
    with st.expander("Additional settings", expanded=False):
        lease_range = st.slider('Lease commencement date', min(results['lease_commence_date']), 
                                max(results['lease_commence_date']),
                                (min(results['lease_commence_date']), 
                                max(results['lease_commence_date'])),
                                help = "Select the range of lease commencement date")


        distance = st.slider('Radius in KM', 0.05,1.0,value = 1.0, step = 0.05,
                             help="This is just an estimate.")

    # Applying filters
    filtered_results = results[results['distance'] <= distance]
    filtered_results = filtered_results[(filtered_results['lease_commence_date'] >= lease_range[0]) &
                                         (filtered_results['lease_commence_date'] <= lease_range[1])]
    filtered_results = filtered_results[filtered_results['flat_type'] ==flat_type]
    filtered_results['month'] = filtered_results['year'].astype(str) + '-' + filtered_results['month'].astype(str)
    filtered_results['lease_commence_date'] = filtered_results['lease_commence_date'].astype(str)
    st.markdown("""### Results
                The columns can be sorted by clicking on the column name.
                """)
    st.dataframe(filtered_results[['month','lease_commence_date','remaining_lease_year',
                               'storey_range','floor_area_sqm','resale_price','address',
                               'distance'
                               ]]
                               .head(100), hide_index=True)