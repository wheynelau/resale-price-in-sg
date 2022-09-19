from flask import Flask, request, url_for, redirect, render_template, jsonify
from xgboost import XGBRegressor
from common_func import *
from datetime import datetime
import numpy as np


def info_parser(features: dict, mrt, malls, hdb_details_df: pd.DataFrame):
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
            features['floor_area_sqm'] = avg_area[int(features['flat_cat'])]

        coords = np.array([float(resultsdict['results'][0]['LATITUDE']),
                           float(resultsdict['results'][0]['LONGITUDE'])])
        features['distance_to_town'] = np.linalg.norm(coords - np.array([1.300556, 103.821667])) * conversion
        features['distance_to_mrt'] = min(np.linalg.norm(coords - mrt_array, axis=1)) * conversion
        features['distance_to_mall'] = min(np.linalg.norm(coords - malls_array, axis=1)) * conversion
        features['number_of_malls'] = (np.linalg.norm(coords - malls_array, axis=1) < radius / conversion).sum()

        final_features = np.array([features[i] for i in reorder_list],
                                  dtype=object).reshape(1, len(reorder_list))
        return final_features


model = XGBRegressor()
hdb_details = pd.read_csv('resale-flat-prices/hdb-property-information.csv',
                          usecols=['blk_no', 'street', 'year_completed'])

model.load_model('model_xgb.json')

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


# predict function, POST method to take in inputs
@app.route('/predict', methods=['POST', 'GET'])
def predict():
    feature_list = request.form.to_dict()
    print(feature_list)
    new_features = info_parser(feature_list, mrt_array, malls_array, hdb_details)

    prediction = model.predict(new_features)
    return render_template('index.html',
                           prediction_text=f"Your house is predicted to be valued at ${prediction[0]:.2f}")


if __name__ == "__main__":
    app.run(debug=True)
