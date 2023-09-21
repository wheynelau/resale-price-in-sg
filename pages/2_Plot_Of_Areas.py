import streamlit as st
import pandas as pd
import pydeck as pdk


st.title("Resale prices on a map")
@st.cache_data
def load_csv():
    return pd.read_csv("assets/data/geo_coords_2017.csv", index_col=0)
if "data" not in st.session_state:
    st.session_state.data = load_csv()

@st.cache_resource(ttl=60*60*24)
def load_pdk():
    view_state = pdk.ViewState(latitude=st.session_state.data['latitude'].mean(), 
                           longitude=st.session_state.data['longitude'].mean(), 
                           zoom=10,
                           pitch=50,
                           bearing=-27.36)

    # Create a hexagon layer
    min_price = st.session_state.data['resale_price'].min()
    max_price = st.session_state.data['resale_price'].max()
    resale_price = st.session_state.data['resale_price']
    st.session_state['normalized_price'] = (resale_price - min_price) / (max_price - min_price)

    layer = pdk.Layer(
        "HexagonLayer",
        st.session_state.data,
        get_position=["longitude", "latitude"],
        auto_highlight=True,
        elevation_scale=10,
        pickable=True,
        elevation_range=[0, 3000],
        extruded=True,
        coverage=1,
        radius=500,
        get_fill_color=f"[255 * (resale_price - {min_price}) / ({max_price} - {min_price}), 0, 255 - 255 * (resale_price - {min_price}) / ({max_price} - {min_price})]"
    )
    return  pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    layers=[layer],
    initial_view_state=view_state,
    )

st.pydeck_chart(load_pdk())
