from sklearn.model_selection import train_test_split
from sklearn.neighbors import KDTree
import numpy as np
import pandas as pd

class PredictProcessor:

    RADIUS_KM = 5

    def __init__(self):

        self.load_mrt_malls_tree()

    def load_mrt_malls_tree(self):
        """
        Load as tree objects
        """
        mrt = pd.read_csv('assets/amenities/mrt.csv')
        malls = pd.read_csv('assets/amenities/malls.csv')
        # drop due to transfer station
        mrt.drop_duplicates(subset='Station',inplace=True)
        mrt.reset_index(drop=True, inplace=True)
        mrt_array = mrt[['LAT','LONG']].to_numpy()
        malls_array = malls[['LAT','LONG']].to_numpy()
        self.mrt_tree = KDTree(mrt_array, metric='euclidean')
        self.malls_tree = KDTree(malls_array,metric='euclidean')
        
    def __call__(self,df:pd.DataFrame) -> pd.DataFrame:
        """
        Process the dataframe
        """
        addresses = self.get_addresses(df)
        data_points = addresses[['latitude', 'longitude']].values
        indices_mrt, indices_malls = self.get_indices(data_points)
        dist_mrt, dist_malls = self.get_distance(data_points)
        dist_town = self.get_distance_to_town(addresses)


        addresses['mrt'] = indices_mrt
        addresses['malls'] = indices_malls
        addresses['dist_mrt'] = dist_mrt
        addresses['dist_malls'] = dist_malls
        addresses['distance_to_town'] = dist_town

        df = df.merge(addresses, on=['address','latitude','longitude'], how='right')

        features = self.numerical_features(df)
        assert features.shape[1] == 11, "Features are not 11"
        return features
    def get_addresses(self, df:pd.DataFrame) -> pd.DataFrame:
        """
        Get the addresses of the dataframe
        """
        addresses = df[['address','latitude','longitude']].drop_duplicates()
        return addresses.reset_index(drop=True)
    

    def get_indices(self, data_points:np.ndarray) -> np.ndarray:
        """
        Get the indices of the nearest points
        """
        radius = self.RADIUS_KM / 111.1
        indices_mrt = self.mrt_tree.query_radius(data_points, r=radius, count_only=True,)
        indices_malls = self.malls_tree.query_radius(data_points,r=radius, count_only=True)
        return indices_mrt, indices_malls
    def get_distance(self, data_points:np.ndarray) -> np.ndarray:
        """
        Get the distance of the nearest points
        """
        dist_mrt , _ = self.mrt_tree.query(data_points, k=1, return_distance=True)
        dist_malls , _ = self.malls_tree.query(data_points, k=1, return_distance=True)
        return dist_mrt, dist_malls
    
    def get_distance_to_town(self, df) -> np.ndarray:
        """
        Get the distance to town
        """
        town = np.array([1.300556, 103.821667])
        dist_town = np.linalg.norm(df[['latitude','longitude']] - town, axis=1)
        return dist_town
    
    def numerical_features(self, df:pd.DataFrame) -> pd.DataFrame:
        """
        Get the numerical features
        """
        df['flat_cat'] = df.flat_type.map({'2 ROOM':2,
                                        '3 ROOM':3,
                                        '4 ROOM':4,
                                        '5 ROOM': 5,
                                        '1 ROOM':1,
                                        'EXECUTIVE': 6,
                                        'MULTI-GENERATION':7})
        features = df[['storey_range', 'floor_area_sqm', 'flat_cat',
                        'remaining_lease_year', 'resale_price', 'mrt', 'malls', 'year'
                        ,'dist_mrt','dist_malls','distance_to_town']]
        return features