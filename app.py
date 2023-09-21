from flask import Flask, request, url_for, redirect, render_template, jsonify
from xgboost import XGBRegressor
from src.common_func import *
from datetime import datetime
import numpy as np

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
