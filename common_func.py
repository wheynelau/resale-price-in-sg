import requests
import pandas as pd


# function gets the lat and lon details from the given address
# its a free API with a rate limit of 250 per min


def getcoordinates(address):
    req = requests.get('https://developers.onemap.sg/commonapi/search?searchVal='+address+'&returnGeom=Y&getAddrDetails=Y&pageNum=1')
    resultsdict = eval(req.text)
    if len(resultsdict['results'])>0:
        return [resultsdict['results'][0]['LATITUDE'], resultsdict['results'][0]['LONGITUDE']]
    else:
        pass

def create_lat_lon(new_df):
    new_df = new_df.join(pd.DataFrame(new_df['Coords'].values.tolist(),columns=['LAT','LONG']),on=new_df.index)
    new_df.set_index(new_df.columns[0],inplace=True)
    new_df.drop(columns=['Coords'],inplace=True)
    return new_df
def get_block_address(postal):
    req = requests.get('https://developers.onemap.sg/commonapi/search?searchVal='+postal+'&returnGeom=Y&getAddrDetails=Y&pageNum=1')
    resultsdict = eval(req.text)
    if len(resultsdict['results'])>0:
        return resultsdict['results'][0]['BLK_NO'], resultsdict['results'][0]['ROAD_NAME']
    else:
        print("No such address")
