import sys
import time
import pandas as pd
import requests
from utils.preprocessing import Preprocessor


class HDBDataset:

    """
    A class for fetching JSON data from the HDB resale price dataset API.
    """

    def __init__(self):
        """
        Initializes a new instance of the HDBDataset class.
        """
        self._resource_id = self.get_first_dataset()

    def fetch_json_response(self, **params):
        """
        Fetches JSON data from a given URL with the specified parameters.

        Args:
            params (dict, optional): Dictionary of query parameters.

        Returns:
            dict: JSON data as a Python dictionary.
        """
        if params.get('resource_id', None) is None:
            params['resource_id'] = self._resource_id
        response = requests.get("https://data.gov.sg/api/action/datastore_search",
                                 params=params, timeout=5)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()['result']['records']
        response.raise_for_status()

    def get_first_dataset(self):
        """
        Gets the resource ID of the first dataset that contains data from January 2017.

        Returns:
            str: The resource ID of the first dataset that contains data from January 2017.
        """
        metadata = requests.get(
            'https://api-production.data.gov.sg/v2/public/api/collections/189/metadata',
              timeout=5)
        resource_id = None
        # sanity check
        for child_dataset in metadata.json()['data']['collectionMetadata']['childDatasets']:
            resp = self.fetch_json_response(resource_id=child_dataset, limit=1)
            if resp[0]['month'] == '2017-01':
                resource_id = child_dataset
                break
            time.sleep(1)
        return resource_id

if __name__ == "__main__":
    dataset = HDBDataset()
    preprocessor = Preprocessor()

    CSV_PATH = 'assets/data/geo_coords_2017.csv'

    # 1. Load the current data
    old_df = pd.read_csv(CSV_PATH, index_col=0)

    # 2. Fetch the new data

    # 1000 is usually safe, it will usually not return more than 1000 records
    sample=dataset.fetch_json_response(limit=1000, offset = len(old_df))

    # 2a. Check if the new data is empty

    if len(sample) == 0:

        print("No new data to update")
        sys.exit(0)

    # 3. Convert the new data to a DataFrame
    print(f"New data fetched successfully, num differences = {len(sample)}")
    new_data = pd.DataFrame(sample)
    new_data['_id'] = new_data['_id']-1
    new_data.set_index('_id', inplace=True)

    # 4. Preprocess the new data
    new_data = preprocessor(df=new_data)

    # 5. Merge the new data with the old data
    appended = preprocessor.add_new_to_old(old_df, new_data)

    # 6. Save the merged data

    appended.to_csv(CSV_PATH)
