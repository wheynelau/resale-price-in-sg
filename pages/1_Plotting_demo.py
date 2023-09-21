import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Streamlit CSV Visualization App")
@st.cache_data
def load_csv():
    return pd.read_csv("assets/data/geo_coords_2017.csv", index_col=0)
data = load_csv()
# st.write(data.head())

# if st.checkbox("Show column types and missing values"):
#     st.write(data.info())
fig, ax = plt.subplots()
avg = data.groupby('month').agg({'resale_price':np.median})
st.line_chart(avg, x= 'month', y='resale_price')
