from .connections import VehicleScoreConnector
from Utils.utils import flatten_dict

def get_vehicle_score(vrm):
    score_api = VehicleScoreConnector()
    api_response = score_api.fetch_data(vrm)

    if api_response and 'pageProps' in api_response:
        if 'mot' in api_response['pageProps']:
            if 'motTests' in api_response['pageProps']['mot']:
                del api_response['pageProps']['mot']['motTests']
    
    # Flatten the api_response dictionary
    flattened_data = flatten_dict(api_response)
    

    return flattened_data



__all__ = ['get_vehicle_score']
