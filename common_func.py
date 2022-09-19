import requests
import pandas as pd
import numpy as np


# function gets the lat and lon details from the given address
# it's a free API with a rate limit of 250 per min


def getcoordinates(address):
    req = requests.get(
        'https://developers.onemap.sg/commonapi/search?searchVal=' + address + '&returnGeom=Y&getAddrDetails=Y&pageNum=1')
    resultsdict = eval(req.text)
    if len(resultsdict['results']) > 0:
        return [resultsdict['results'][0]['LATITUDE'], resultsdict['results'][0]['LONGITUDE']]
    else:
        pass


def create_lat_lon(new_df):
    new_df = new_df.join(pd.DataFrame(new_df['Coords'].values.tolist(), columns=['LAT', 'LONG']), on=new_df.index)
    new_df.set_index(new_df.columns[0], inplace=True)
    new_df.drop(columns=['Coords'], inplace=True)
    return new_df


def load_mrt_malls():
    mrt = pd.read_csv('amenities/mrt.csv')
    malls = pd.read_csv('amenities/malls.csv')
    convert_mrt_array = mrt[['LAT', 'LONG']].to_numpy()
    convert_malls_array = malls[['LAT', 'LONG']].to_numpy()
    return convert_mrt_array, convert_malls_array


# helper variables for calculations

mrt_array, malls_array = load_mrt_malls()

reorder_list = ['storey_range',
                'floor_area_sqm',
                'remaining_lease_year',
                'distance_to_town',
                'distance_to_mrt',
                'distance_to_mall',
                'number_of_malls',
                'year',
                'flat_cat']

avg_area = {1: 31.0,
            2: 45.82892057026476,
            3: 68.18060710335504,
            4: 95.47028447439294,
            5: 118.0717443108435,
            6: 144.3410299943407,
            7: 160.15217391304347}

conversion = 111
central = np.array([1.300556, 103.821667])
radius = 3
