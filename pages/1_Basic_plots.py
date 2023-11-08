import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


st.title("Resale prices at a glance")


@st.cache_data
def load_csv():
    return pd.read_csv("assets/data/geo_coords_2017.csv", index_col=0)


if "data" not in st.session_state:
    st.session_state.data = load_csv()

with st.expander("About this page"):
    st.markdown(
        "This page shows some basic plots of the resale prices in Singapore.\n "
        "The plot will automatically update with there is new data from data.gov.sg"
    )


fig, axarr = plt.subplots(2, 2, figsize=(10, 10))

# Example plots - adjust as needed based on your CSV data
avg = st.session_state.data.groupby("year").agg({"resale_price": "median"})
sns.lineplot(data=avg, x="year", y="resale_price", ax=axarr[0][0])
axarr[0][0].set_title("Resale Price by Year")

year_subset = st.session_state.data[
    st.session_state.data["year"] == st.session_state.data["year"].max()
]
ytd_avg = year_subset.groupby("month").agg({"resale_price": "median"})
sns.lineplot(data=ytd_avg, x="month", y="resale_price", ax=axarr[0][1])
axarr[0][1].set_title(
    "YTD Median Resale Price by Month in {}".format(st.session_state.data["year"].max())
)
# PLOT 3
avg_town_price = st.session_state.data.groupby("town")["resale_price"].median()
avg_town_price = avg_town_price.to_frame()
sns.barplot(
    data=avg_town_price,
    x=avg_town_price.index,
    y="resale_price",
    order=avg_town_price.sort_values(by="resale_price", ascending=True).index,
    ax=axarr[1][0],
)
axarr[1][0].xaxis.set_tick_params(rotation=90)
axarr[1][0].set_title("Median Resale Price by Town")
## PLOT 4
mop_resale = st.session_state.data[st.session_state.data["remaining_lease_year"] > 93]
mop_resale = mop_resale.groupby("year").agg({"town": "count"})
sns.lineplot(data=mop_resale, x="year", y="town", ax=axarr[1][1])
axarr[1][1].set_title("Number of Resale Flats sold < 2 years of MOP")
axarr[1][1].set_ylabel("Number of Resale Flats")
plt.tight_layout()
st.pyplot(fig)
