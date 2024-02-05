import requests
import pandas as pd
import numpy as np
import difflib as dl
from datetime import datetime
from ast import literal_eval

# function gets the lat and lon details from the given address
# it's a free API with a rate limit of 250 per min


def getcoordinates(address):
    req = requests.get(
            "https://www.onemap.gov.sg/api/common/elastic/search?searchVal="
            + address
            + "&returnGeom=Y&getAddrDetails=Y&pageNum=1",
            timeout=30,
        )
    resultsdict = literal_eval(req.text)
    if len(resultsdict["results"]) > 0:
        return [
            resultsdict["results"][0]["LATITUDE"],
            resultsdict["results"][0]["LONGITUDE"],
        ]
    else:
        pass


def find_nearest(df, lat, long, col_name="distance", conversion=111):
    lat = float(lat)
    long = float(long)
    df[col_name] = (
        np.linalg.norm(df[["latitude", "longitude"]] - (lat, long), axis=1) * conversion
    )


def create_lat_lon(new_df):
    new_df = new_df.join(
        pd.DataFrame(new_df["Coords"].values.tolist(), columns=["LAT", "LONG"]),
        on=new_df.index,
    )
    new_df.set_index(new_df.columns[0], inplace=True)
    new_df.drop(columns=["Coords"], inplace=True)
    return new_df


def load_mrt_malls():
    mrt = pd.read_csv("assets/amenities/mrt.csv")
    malls = pd.read_csv("assets/amenities/malls.csv")
    convert_mrt_array = mrt[["latitude", "longitude"]].to_numpy()
    convert_malls_array = malls[["LAT", "LONG"]].to_numpy()
    return convert_mrt_array, convert_malls_array


def info_parser(features: dict, mrt, malls, hdb_details_df: pd.DataFrame):
    postal = features["Postal"]
    req = requests.get(
        "https://developers.onemap.sg/commonapi/search?searchVal="
        + str(postal)
        + "&returnGeom=Y&getAddrDetails=Y&pageNum=1"
    )
    resultsdict = eval(req.text)
    if len(resultsdict["results"]) > 0:
        blk, street = (
            resultsdict["results"][0]["BLK_NO"],
            resultsdict["results"][0]["ROAD_NAME"],
        )

        ignore_short_forms = dl.get_close_matches(
            street, hdb_details_df["street"].values
        )[0]

        row = hdb_details_df[
            (hdb_details_df["blk_no"] == blk)
            & (hdb_details_df["street"] == ignore_short_forms)
        ]

        # build dict of features
        features["year"] = datetime.now().year
        if features["Lease"] == "":
            features["remaining_lease_year"] = features["year"] - row.iloc[0, -1]
        else:
            features["remaining_lease_year"] = features["year"] - int(features["Lease"])

        if features["floor_area_sqm"] == "":
            features["floor_area_sqm"] = avg_area[int(features["flat_cat"])]

        coords = np.array(
            [
                float(resultsdict["results"][0]["LATITUDE"]),
                float(resultsdict["results"][0]["LONGITUDE"]),
            ]
        )
        features["distance_to_town"] = (
            np.linalg.norm(coords - np.array([1.300556, 103.821667])) * conversion
        )
        features["distance_to_mrt"] = (
            min(np.linalg.norm(coords - mrt_array, axis=1)) * conversion
        )
        features["distance_to_mall"] = (
            min(np.linalg.norm(coords - malls_array, axis=1)) * conversion
        )
        features["number_of_malls"] = (
            np.linalg.norm(coords - malls_array, axis=1) < radius / conversion
        ).sum()

        final_features = np.array(
            [features[i] for i in reorder_list], dtype=object
        ).reshape(1, len(reorder_list))
        return final_features


# helper variables for calculations

mrt_array, malls_array = load_mrt_malls()

reorder_list = [
    "storey_range",
    "floor_area_sqm",
    "remaining_lease_year",
    "distance_to_town",
    "distance_to_mrt",
    "distance_to_mall",
    "number_of_malls",
    "year",
    "flat_cat",
]

avg_area = {
    1: 31.0,
    2: 45.82892057026476,
    3: 68.18060710335504,
    4: 95.47028447439294,
    5: 118.0717443108435,
    6: 144.3410299943407,
    7: 160.15217391304347,
}

conversion = 111
central = np.array([1.300556, 103.821667])
radius = 3
