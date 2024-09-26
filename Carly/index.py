from .connections import CarlyVehicleHistory as CarlyAPI
from Utils.utils import flatten_dict

def get_carly_vehicle_history(vrm):
    carly_api = CarlyAPI()
    carly_data = carly_api.get_vehicle_history(vrm)
    carly_data = carly_api.extract_vehicle_info(carly_data, vrm)
    
    # Flatten the carly_data dictionary
    flattened_data = flatten_dict(carly_data)
    
    return flattened_data

__all__ = ['get_carly_vehicle_history']