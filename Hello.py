import streamlit as st

st.set_page_config(
    page_title="Resale Price",
    page_icon="🏠",
    layout="wide",
)

st.write("# Welcome to HDB Resale app! 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    ## This is an application for HDB resale price prediction.

    ### The application is divided into 3 parts:
    - Basic plots
    - Map plot of areas
    - Search
    - Prediction
""" 
)