import time
from typing import Tuple, Dict
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests


def mrt_geo_data() -> Dict:
    """
    Retrieves MRT station data from an API endpoint.

    Returns:
    A dictionary containing the MRT station data.
    """
    # TODO: Use proper API endpoint
    # workaround because the direct API had some issues
    headers = {
        "Accept": "*/*",
        "Sec-Fetch-Site": "cross-site",
        # 'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": "en-SG,en-GB;q=0.9,en;q=0.8",
        "Sec-Fetch-Mode": "cors",
        "Host": "kjo15bc7zd.execute-api.ap-southeast-1.amazonaws.com",
        "Origin": "https://beta.data.gov.sg",
        # 'Content-Length': '0',
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        "Referer": "https://beta.data.gov.sg/",
        "Sec-Fetch-Dest": "empty",
    }

    response = requests.post(
        "https://kjo15bc7zd.execute-api.ap-southeast-1.amazonaws.com/api/public/resources/d_af90df38d609c426c73bc9acea366786/generate-download-link",
        headers=headers,
        timeout=30,
    )
    url = response.json()["url"]
    time.sleep(1)  # prevent 429
    return requests.get(url, timeout=30).json()


def process_mrt(data) -> Tuple[str, float, float]:
    """
    Extracts MRT station name and coordinates from the given data.

    Args:
    data: A dictionary containing the properties and geometry of an MRT station.

    Returns:
    A tuple containing the MRT station name, and its coordinates (latitude and longitude).
    """
    soup = BeautifulSoup(data["properties"]["Description"], "html.parser")

    type_element = soup.find("th", string="TYPE")
    if type_element:
        td_element = type_element.find_next_sibling("td")
        if td_element:
            mrt_type = td_element.text

    # not interested in LRT stations
    if mrt_type == "LRT":
        return None, None, None

    name_element = soup.find("th", string="NAME")
    # duplicated names are not dropped, this is to account for stations with
    # multiple lines
    if name_element:
        td_element = name_element.find_next_sibling("td")
        if td_element:
            mrt = td_element.text

    # coordinates are returned as a polygon, therefore we take the mean
    coordinates = np.mean(data["geometry"]["coordinates"][0], axis=0)
    return mrt, coordinates[0], coordinates[1]


if __name__ == "__main__":
    CSV_PATH = "./assets/amenities/mrt.csv"
    HEADERS = ["mrt", "latitude", "longitude"]
    mrt_data = mrt_geo_data()
    mrt_stations = []
    for feature in mrt_data["features"]:
        mrt_name, long, lat = process_mrt(feature)
        if mrt_name:
            mrt_stations.append(dict(zip(HEADERS, [mrt_name, lat, long])))

    # read the length of old csv first
    df = pd.read_csv(CSV_PATH)

    if len(mrt_stations) > len(df):
        print(f"Updating MRT stations from {len(df)} to {len(mrt_stations)}")
        df = pd.DataFrame(mrt_stations)
        df.to_csv(CSV_PATH, index=False)
