import pandas as pd
import numpy as np
import requests
import difflib as dl
from datetime import datetime


def load_mrt_malls():
    mrt = pd.read_csv('assets/amenities/mrt.csv')
    malls = pd.read_csv('assets/amenities/malls.csv')
    convert_mrt_array = mrt[['LAT', 'LONG']].to_numpy()
    convert_malls_array = malls[['LAT', 'LONG']].to_numpy()
    return convert_mrt_array, convert_malls_array

class Preprocessor:
    """
    A class for preprocessing the HDB resale price dataset.

    Methods:
    --------
    get_address(df):
        Adds a new column 'address' to the dataframe by concatenating 'block' and 
        'street_name' columns and drops the original columns.

    getcoordinates(address):
        Returns the latitude and longitude of the given address using OneMap API.

    get_storey_range(df):
        Splits the 'storey_range' column into two columns and takes the mean of the 
        two values. Replaces the original column with the mean value.

    get_remaining_lease(features):
        Calculates the remaining lease year of each flat based on the 'month' and 
        'lease_commence_date' columns.

    get_lat_lon(old_df:pd.DataFrame, new_df):
        Adds latitude and longitude columns to the new dataframe by using the existing
          values from the old dataframe or by calling the getcoordinates method.

    set_dtypes(df):
        Converts the 'lease_commence_date' column to datetime and 'resale_price' and 
        'floor_area_sqm' columns to float32.

    create_year_month(df):
        Extracts the year and month from the 'month' column and creates two new
        columns 'year' and 'month'.

    add_new_to_old(self,old_df:pd.DataFrame, new_df:pd.DataFrame):
        Adds the new dataframe to the old dataframe and returns the appended dataframe.

    __call__(self, df:pd.DataFrame):
        Calls all the above methods to preprocess the dataframe.
    """
    @staticmethod
    def get_address(df):
        df['address'] = df['block'] + ' ' + df['street_name']
        df.drop(['block', 'street_name'], axis=1, inplace=True)

    @staticmethod
    def getcoordinates(address):
        req = requests.get(
            'https://developers.onemap.sg/commonapi/search?searchVal=' +
              address +
                '&returnGeom=Y&getAddrDetails=Y&pageNum=1', timeout=30)
        resultsdict = eval(req.text)
        if len(resultsdict['results']) > 0:
            return [resultsdict['results'][0]['LATITUDE'], resultsdict['results'][0]['LONGITUDE']]
        else:
            pass

    @staticmethod
    def get_storey_range(df):
        df_storey =df['storey_range'].str.split(pat = " TO ", expand=True)
        df_storey = df_storey.astype(int)
        df_storey.head()
        df['storey_range'] =  df_storey.mean(axis = 1)

    @staticmethod
    def get_remaining_lease(features):
        features['month'] = pd.to_datetime(features['month'],format="%Y-%m")
        features['current_lease_dt']=features['month']-pd.to_datetime(features['lease_commence_date'],format="%Y")
        features['current_lease_year'] = features['current_lease_dt'] / np.timedelta64(1, 'Y')
        features['remaining_lease_year'] = 99-features['current_lease_year']
        features['remaining_lease_year'] = features['remaining_lease_year'].round(2)
        features.drop(columns = ['current_lease_year','current_lease_dt']
                    ,axis=1,inplace=True)

    def get_lat_lon(self,old_df:pd.DataFrame, new_df):
        dict_lat_lon = old_df[['address','latitude','longitude']].drop_duplicates(subset=['address']).set_index('address').to_dict()
        for idx,row in new_df.iterrows():
            value = dict_lat_lon['latitude'].get(row['address'], np.nan)
            if isinstance(value, (float, np.float64, np.float32)) and np.isnan(value):
                lat, lon = self.getcoordinates(row['address'])
                new_df.loc[idx,['latitude', 'longitude']] = lat,lon
                dict_lat_lon['latitude'][row['address']] = lat
                dict_lat_lon['longitude'][row['address']] = lon
            else:
                new_df.loc[idx,['latitude', 'longitude']] = dict_lat_lon['latitude'][row['address']],dict_lat_lon['longitude'][row['address']]

    @staticmethod      
    def set_dtypes(df):
        df['resale_price'] = df['resale_price'].astype(np.float32)
        df['floor_area_sqm'] = df['floor_area_sqm'].astype(np.float32)

    @staticmethod
    def create_year_month(df):
        df['year'] = df.month.dt.year
        df['month'] = df.month.dt.month
    
    def add_new_to_old(self,old_df:pd.DataFrame, new_df:pd.DataFrame):
        self.get_lat_lon(old_df,new_df)
        appended_df = pd.concat([old_df, new_df], axis=0)
        return appended_df
    
    def __call__(self, df:pd.DataFrame):
        """
        Prepares the HDB resale price dataset for merging

        Args:
            df (pd.DataFrame): The HDB resale price dataset.
        """
        self.get_address(df)
        self.get_storey_range(df)
        self.get_remaining_lease(df)
        self.set_dtypes(df)
        self.create_year_month(df)
        return df

def info_parser(features: dict, mrt_array, malls_array, hdb_details_df: pd.DataFrame):
    CONVERSION = 111
    CENTRAL = np.array([1.300556, 103.821667])
    RADIUS = 3
    AVG_AREA = {1: 31.0,
            2: 45.82892057026476,
            3: 68.18060710335504,
            4: 95.47028447439294,
            5: 118.0717443108435,
            6: 144.3410299943407,
            7: 160.15217391304347}
    
    REORDER_LIST = ['storey_range',
                'floor_area_sqm',
                'remaining_lease_year',
                'distance_to_town',
                'distance_to_mrt',
                'distance_to_mall',
                'number_of_malls',
                'year',
                'flat_cat']


    postal = features['Postal']
    req = requests.get('https://developers.onemap.sg/commonapi/search?searchVal=' + str(
        postal) + '&returnGeom=Y&getAddrDetails=Y&pageNum=1')
    resultsdict = eval(req.text)
    if len(resultsdict['results']) > 0:
        blk, street = resultsdict['results'][0]['BLK_NO'], resultsdict['results'][0]['ROAD_NAME']

        ignore_short_forms = dl.get_close_matches(street, hdb_details_df['street'].values)[0]

        row = hdb_details_df[(hdb_details_df['blk_no'] == blk) & (hdb_details_df['street'] == ignore_short_forms)]

        # build dict of features
        features['year'] = datetime.now().year
        if features['Lease'] == '':
            features['remaining_lease_year'] = features['year'] - row.iloc[0, -1]
        else:
            features['remaining_lease_year'] = features['year'] - int(features['Lease'])

        if features['floor_area_sqm'] == '':
            features['floor_area_sqm'] = AVG_AREA[int(features['flat_cat'])]

        coords = np.array([float(resultsdict['results'][0]['LATITUDE']),
                           float(resultsdict['results'][0]['LONGITUDE'])])
        features['distance_to_town'] = np.linalg.norm(coords - np.array([1.300556, 103.821667])) * CONVERSION
        features['distance_to_mrt'] = min(np.linalg.norm(coords - mrt_array, axis=1)) * CONVERSION
        features['distance_to_mall'] = min(np.linalg.norm(coords - malls_array, axis=1)) * CONVERSION
        features['number_of_malls'] = (np.linalg.norm(coords - malls_array, axis=1) < RADIUS / CONVERSION).sum()

        final_features = np.array([features[i] for i in REORDER_LIST],
                                  dtype=object).reshape(1, len(REORDER_LIST))
        return final_features