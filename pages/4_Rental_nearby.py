import streamlit as st
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.utils.common_func import getcoordinates, find_nearest

st.title("Search nearby houses that were rented")


@st.cache_data
def load_resale():
    return pd.read_csv("assets/data/rental_flats.csv", index_col=0)


if "resale" not in st.session_state:
    st.session_state.resale = load_resale()


address = st.text_input(
    "Enter your address", placeholder="Enter your address or postal code"
)

if address:
    lat, lon = getcoordinates(address)
    find_nearest(st.session_state.resale, lat, lon)
    results = st.session_state.resale.query("distance <= 1")

else:
    results = st.session_state.resale

if not results.empty:
    flat_type = st.selectbox(
        "Choose flat type:",
        options=np.insert(
            results["flat_type"].unique(),
            0,
            "All",
        ),
    )
    with st.expander("Additional settings (Distance and price)", expanded=False):
        lease_range = st.slider(
            "Rental price",
            min(results["monthly_rent"]),
            max(results["monthly_rent"]),
            (min(results["monthly_rent"]), max(results["monthly_rent"])),
            help="Select the range of pricing, good if you search without an address.",
        )
        distance = st.slider(
            "Radius in KM",
            0.0,
            1.0,
            value=0.5,
            step=0.05,
            help=(
                "This is just an estimate. 0 distance should return your exact block. "
                "Doesn't work if address is not entered"
            ),
            disabled=not address,
        )
    if address:
        filtered_results = results[results["distance"] <= distance]
    else:
        filtered_results = results

    filtered_results = filtered_results[
        (filtered_results["monthly_rent"] >= lease_range[0])
        & (filtered_results["monthly_rent"] <= lease_range[1])
    ]

    if flat_type != "All":
        filtered_results = filtered_results[filtered_results["flat_type"] == flat_type]

    filtered_results["month"] = filtered_results.index
    st.markdown(
        "### Results\n"
        "The columns can be sorted by clicking on the column name. "
        "Note that only the first 100 results are shown."
    )
    filtered_results = filtered_results.sort_values("month", ascending=False)
    col_config = {
        "monthly_rent": st.column_config.NumberColumn(
            "Rental Price ($)", format="$ %d"
        ),
        "distance": st.column_config.NumberColumn("Distance (KM)", format="%.2f"),
        "month": st.column_config.DatetimeColumn("Month", format="MMM-YYYY"),
    }
    if address:
        st.dataframe(
            filtered_results[
                [
                    "month",
                    "flat_type",
                    "monthly_rent",
                    "address",
                    "distance",
                ]
            ].head(100),
            hide_index=True,
        )
    else:
        st.dataframe(
            filtered_results[
                [
                    "month",
                    "flat_type",
                    "monthly_rent",
                    "address",
                ]
            ].head(100),
            hide_index=True,
            column_config=col_config,
        )
