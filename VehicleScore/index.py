from .connections import VehicleScoreConnector
from Utils.utils import flatten_dict
from Utils.logging import logger

def get_vehicle_score(vrm):
    try:
        score_api = VehicleScoreConnector()
        api_response = score_api.fetch_data(vrm)

        print(api_response)
        if api_response and 'pageProps' in api_response:
            if 'mot' in api_response['pageProps']:
                if 'motTests' in api_response['pageProps']['mot']:
                    del api_response['pageProps']['mot']['motTests']
    
        # Flatten the api_response dictionary
        flattened_data = flatten_dict(api_response)
    
        return flattened_data
    except Exception as e:
        logger.write(str(e), is_exception=True)

__all__ = ['get_vehicle_score']
