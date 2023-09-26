import os
import sys
import logging
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KDTree
from sklearn.metrics import r2_score
import numpy as np
import pandas as pd
import xgboost as xgb

THRESHOLD = 0.9

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)
class PredictProcessor:
    RADIUS_KM = 5
    CONVERSION = 111.1
    METRIC = "manhattan"

    def __init__(self):
        self.load_mrt_malls_tree()

    def load_mrt_malls_tree(self):
        """
        Load as tree objects
        """
        mrt = pd.read_csv("assets/amenities/mrt.csv")
        malls = pd.read_csv("assets/amenities/malls.csv")
        mrt.reset_index(drop=True, inplace=True)
        mrt_array = mrt[["latitude", "longitude"]].to_numpy()
        malls_array = malls[["LAT", "LONG"]].to_numpy()
        # manhattan is used to assume the longest distance
        self.mrt_tree = KDTree(mrt_array, metric=self.METRIC)
        self.malls_tree = KDTree(malls_array, metric=self.METRIC)

    def __call__(self, input_df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the dataframe
        """
        addresses = self.get_addresses(input_df)
        data_points = addresses[["latitude", "longitude"]].values
        indices_mrt, indices_malls = self.get_indices(data_points)
        dist_mrt, dist_malls = self.get_distance(data_points)
        dist_town = self.get_distance_to_town(addresses)

        addresses["mrt"] = indices_mrt
        addresses["malls"] = indices_malls
        addresses["dist_mrt"] = dist_mrt
        addresses["dist_malls"] = dist_malls
        addresses["distance_to_town"] = dist_town

        input_df = input_df.merge(
            addresses, on=["address", "latitude", "longitude"], how="right"
        )

        features = self.numerical_features(input_df)
        assert features.shape[1] == 11, "Features are not 11"
        return features

    def get_addresses(self, input_df: pd.DataFrame) -> pd.DataFrame:
        """
        Get the addresses of the dataframe
        """
        addresses = input_df[["address", "latitude", "longitude"]].drop_duplicates()
        return addresses.reset_index(drop=True)

    def get_indices(self, data_points: np.ndarray) -> np.ndarray:
        """
        Get the indices of the nearest points
        """
        radius = self.RADIUS_KM / self.CONVERSION
        indices_mrt = self.mrt_tree.query_radius(
            data_points,
            r=radius,
            count_only=True,
        )
        indices_malls = self.malls_tree.query_radius(
            data_points, r=radius, count_only=True
        )
        return indices_mrt, indices_malls

    def get_distance(self, data_points: np.ndarray) -> np.ndarray:
        """
        Get the distance of the nearest points
        """
        dist_mrt, _ = self.mrt_tree.query(data_points, k=1, return_distance=True)
        dist_malls, _ = self.malls_tree.query(data_points, k=1, return_distance=True)
        return dist_mrt * self.CONVERSION, dist_malls * self.CONVERSION

    def get_distance_to_town(self, input_df) -> np.ndarray:
        """
        Get the distance to town
        """
        town = np.array([1.300556, 103.821667])
        dist_town = np.linalg.norm(input_df[["latitude", "longitude"]] - town, axis=1)
        return dist_town * self.CONVERSION

    def numerical_features(self, input_df: pd.DataFrame) -> pd.DataFrame:
        """
        Get the numerical features
        """
        input_df["flat_cat"] = input_df.flat_type.map(
            {
                "2 ROOM": 2,
                "3 ROOM": 3,
                "4 ROOM": 4,
                "5 ROOM": 5,
                "1 ROOM": 1,
                "EXECUTIVE": 6,
                "MULTI-GENERATION": 7,
            }
        )
        features = input_df[
            [
                "storey_range",
                "floor_area_sqm",
                "flat_cat",
                "remaining_lease_year",
                "resale_price",
                "mrt",
                "malls",
                "year",
                "dist_mrt",
                "dist_malls",
                "distance_to_town",
            ]
        ]
        return features


if __name__ == "__main__":
    # Load the old model first
    MODEL_PATH = "./assets/models/xgb_model.json"
    DATA_PATH = "./assets/data/geo_coords_2017.csv"
    if os.path.exists("./assets/models/xgb_model.json"):
        xgb_model = xgb.XGBRegressor()
        xgb_model.load_model(MODEL_PATH)

        # Load the newest 100

        data = pd.read_csv(DATA_PATH, index_col=0).tail(100)
        processor = PredictProcessor()
        data = processor(data)
        y = data.pop("resale_price")

        # Score the old model
        score = xgb_model.score(data, y)
    else:
        score = 0

    if score < THRESHOLD:
        # if lower we retrain the model with the past 10000
        logging.info("Current score is %.3f, retraining model...", score)
        data = pd.read_csv(DATA_PATH, index_col=0).tail(10000)
        data = processor(data)
        # the values chosen are all just proof of concept, they may not be statistically
        # significant
        y = data.pop("resale_price")
        X = data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        def custom_r2(predt: np.ndarray, dtrain: xgb.DMatrix):
            """
            Calculates the negative R-squared score for a given set of predictions and training data.
            Needed for r2 in xgboost.
            Args:
            predt (np.ndarray): The predicted values.
            dtrain (xgb.DMatrix): The training data.
            
            Returns:
            float: The negative R-squared score.
            """
            return -r2_score(predt, dtrain)
        
        # no hyperparameter tuning is done as this will be done on github actions
        xgb_model = xgb.XGBRegressor(
            objective="reg:squarederror",
            colsample_bytree=0.8,
            learning_rate=0.1,
            max_depth=12,
            n_estimators=200,
            subsample=0.6,
            early_stopping_rounds=10,
            eval_metric=custom_r2,
        )

        training = xgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], 
                                 verbose=True,)

        score = training.best_score
        print(score)
        try:
            assert score > THRESHOLD, "Score is not above threshold"
        except AssertionError:
            logging.error("Score is not above threshold, exiting...")
            # raise to github actions
            sys.exit(1)
        logging.info("New score is %.3f.", score)
        xgb_model.save_model(MODEL_PATH)
